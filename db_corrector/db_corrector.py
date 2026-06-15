import psycopg2
from psycopg2 import sql
from typing import Dict, List, Any, Optional
import logging


class DatabaseCorrector:
    """Класс для коррекции структуры БД по образцу"""

    def __init__(self, reference_db_config: Dict, target_db_config: Dict):
        """Инициализация корректора БД

        Args:
            reference_db_config (Dict):Конфигурация эталонной БД (образца)
            target_db_config (Dict): Конфигурация целевой БД (которую необходимо изменить)
        """
        self.reference_config = reference_db_config
        self.target_config = target_db_config
        self.logger = self._setup_logger()


    def _setup_logger(self):
        """Настройка логгирования"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger
    

    def _get_connection(self, config: Dict):
        """Создание соединения с БД"""
        try:
            conn = psycopg2.connect(
                host=config.get('host', 'localhost'),
                port=config.get('port', 5432),
                database=config.get('database'),
                user=config.get('user'),
                password=config.get('password')
            )
            conn.autocommit = False
            return conn
        except Exception as e:
            self.logger.error(f"Ошибка подключения к БД {config['database']}: {e}")
            raise


    def get_table_structure(self, conn, table_name: str) -> Dict[str, Any]:
        """Получение структуры таблицы"""
        structure = {
            'columns': [],
            'constrains': [],
            'indexes': []
        }

        cursor = conn.cursor()
        try:
            # Get columns
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            structure['columns'] = cursor.fetchall()

            # Get constraints
            cursor.execute("""
                SELECT conname, contype, pg_get_constraintdef(c.oid)
                FROM pg_constraint c
                JOIN pg_namespace n ON n.oid = c.connamespace
                WHERE conrelid = %s::regclass
            """, (table_name,))
            structure['constrains'] = cursor.fetchall()

            # Get indexes
            cursor.execute("""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = %s
            """, (table_name,))
            structure['indexes'] = cursor.fetchall()

        except Exception as e:
            self.logger.error(f"Ошибка получения структуры: {table_name}: {e}")
            raise
        finally:
            cursor.close()

        return structure
    

    def get_all_tables(self, conn) -> List[str]:
        """Получение списка всех таблиц БД"""

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
            """)
            tables = [row[0] for row in cursor.fetchall()]
            return tables
        finally:
            cursor.close()

    
    def compare_columns(self, reference_columns: List, target_columns: List) -> Dict:
        """Сравнение колонок двух таблиц"""
        target_cols_dict = {col[0] for col in target_columns}

        missing_columns = []
        column_diff =[]

        for ref_col in reference_columns:
            col_name = ref_col[0]
            if col_name not in target_cols_dict:
                missing_columns.append(ref_col)
            else:
                # Check types differences
                target_col = target_cols_dict[col_name]
                if ref_col[1] != target_col[1]:
                    column_diff.append({
                        'name': col_name,
                        'ref_type': ref_col[1],
                        'target_type': target_col[1]
                    })
        
        return {
            'missing_columns': missing_columns,
            'column_differences': column_diff
        }


    def add_missing_column(self, conn, table_name: str, column_info: tuple):
        """Добавление отсутствующей колонки"""
        column_name, data_type, is_nullable, column_default = column_info
        
        sql_query = sql.SQL("ALTER TABLE {} ADD COLUMN {} {}").format(
            sql.Identifier(table_name),
            sql.Identifier(column_name),
            sql.SQL(data_type)
        )

        if is_nullable == 'NO':
            sql_query = sql.SQL("{} NOT NULL").format(sql_query)

        if column_default:
            sql_query = sql.SQL("{} DEFAULT {}").format(
                sql_query,
                sql.SQL(column_default)
            )

        try:
            cursor = conn.cursor()
            cursor.execute(sql_query)
            self.logger.info(f"Добавлена колонка {column_name} в таблицу {table_name}")
        except Exception as e:
            self.logger.error(f"Ошибка при добавлении колонки {column_name}: {e}")
            raise
        finally:
            cursor.close()


    def correct_table(self, conn_target, conn_reference, table_name: str):
        """Коррекция структуры таблицы"""
        self.logger.info(f"Обработка таблицы: {table_name}...")

        # Get tables structure
        reference_structure = self.get_table_structure(conn_reference, table_name)
        target_structure = self.get_table_structure(conn_target, table_name)

        # Columns comparison
        comparison = self.compare_columns(
            reference_structure['columns'],
            target_structure['columns']
        )

        # Add missing columns
        for missing_col in comparison['missing_columns']:
            self.add_missing_column(conn_target, table_name, missing_col)

        # Columns differences logging
        if comparison['column_differences']:
            self.logger.warning(f"Различия в типах колонок в таблице {table_name}:")
            for diff in comparison['column_differences']:
                self.logger.warning(
                    f" - {diff['name']}: референс={diff['ref_type']}, "
                    f"целевая={diff['target_type']}"
                )

    
    def correct_database(self, dry_run: bool = True):
        """Основной метод коррекции БД

        Args:
            dry_run (bool, optional): Если True, только анализирует изменения, не применяя их.
            По умолчанию True.
        """
        conn_reference = None
        conn_target = None

        try:
            # Connect to both DB
            conn_reference = self._get_connection(self.reference_config)
            conn_target = self._get_connection(self.target_config)

            # Get tables list from ref db
            tables = self.get_all_tables(conn_reference)
            self.logger.info(f"Найдено таблиц в тестовой БД: {len(tables)}")

            if dry_run:
                self.logger.info("=== DRY RUN (Только анализ) ===")

            # Correct each table
            for table in tables:
                try:
                    if not dry_run:
                        self.correct_table(conn_target, conn_reference, table)
                    # just analize
                    else:
                        reference_structure = self.get_table_structure(conn_reference, table)

                        try:
                            target_structure = self.get_table_structure(conn_target, table)

                            comparison = self.compare_columns(
                                reference_structure['columns'],
                                target_structure['columns']
                            )
                            if comparison['missing_columns']:
                                self.logger.info(f"Таблица {table}: будет добавлено {len(comparison['missing_columns'])} колонок")
                        except Exception as e:
                            self.logger.error(f"Таблица {table} отсутствует в целевой БД. Нечего сравнить")
                
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке таблицы {table}: {e}")
                    if not dry_run:
                        conn_target.rollback()
                        raise()
                    
            # Commit changes if not dry_run
            if not dry_run:
                conn_target.commit()
                self.logger.info("Изменения применены")
            else:
                self.logger.info("Анализ завершен. Для изменения указать флаг dry_run=False")
        
        except Exception as e:
            self.logger.error(f"Ошибка! {e}")
            if conn_target:
                conn_target.rollback()
            raise
        finally:
            if conn_reference:
                conn_reference.close()
            if conn_target:
                conn_target.close()