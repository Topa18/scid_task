from mysql.connector import connect, Error
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
from models import Base


class DbDefiner:
    """
    Объект - инциализатор схемы БД, пользователя и таблиц в БД.

    Args:
        config (dict): Параметры подключения к БД с root доступом\n
                       {'host': host,\n
                        'user': user,\n
                        'password': password}.
        db_name (str): Имя основной базы данных.
        dev_db_name (str): Имя тестовой базы данных.
        db_user (str): Имя пользователя для доступа к БД.
        db_password (str): Пароль пользователя db_user.
    """

    def __init__(self, config:dict, db_name:str, dev_db_name:str,
                 db_user:str, db_password:str):
        self.config = config
        self.host = config.get('host')
        self.db_name = db_name
        self.dev_db_name = dev_db_name
        self.db_user = db_user
        self.db_password = db_password
        
    def create_schema_and_user(self):
        """
        Настройка и инициализация баз данных и пользователя.
        """
        try:
            with connect(**self.config) as connection:
                with connection.cursor() as cursor:
                    # Создаем две БД 
                    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.db_name}')
                    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.dev_db_name}')
                    # Создаем пользователя
                    cursor.execute(f'CREATE USER IF NOT EXISTS\'{self.db_user}\'@\'{self.host}\''\
                                   f'IDENTIFIED BY \'{self.db_password}\'')
                    # Наделяем пользователя правами к созданным БД
                    cursor.execute(f'GRANT ALL PRIVILEGES ON {self.db_name}.*' \
                                   f'TO \'{self.db_user}\'@\'{self.host}\'')
                    cursor.execute(f'GRANT ALL PRIVILEGES ON {self.dev_db_name}.*' \
                                   f'TO \'{self.db_user}\'@\'{self.host}\'')
                    cursor.execute('FLUSH PRIVILEGES')
                    
                    print(f'Базы данных {self.db_name} и {self.dev_db_name} подготовлены')
                    print(f'Пользователь \'{self.db_user}\'@\'{self.host}\' подготовлен')
                    print(connection)
        except Error as e:
            print(f'Error occured: {e}')

    def create_tables(self, connection_str:str):
        """
        Создание таблиц, если они не были созданы ранее.
        В ином случае None

        Args:
            connection_str (str): Строка соединения с БД
        """
        engine = create_engine(connection_str, echo=True)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            Base.metadata.create_all(bind=engine)
            print("Таблицы созданы")
        else:
            print("Таблицы уже были созданы")

    def drop(self, connection_str):
        """
        Удаление всех таблиц с данными.

        Args:
            connection_str (str): Строка соединения с БД
        """
        engine = create_engine(connection_str, echo=True)
        Base.metadata.drop_all(bind=engine)

    def insert_data(self, connection_str:str, data:Base):
        """
        Вставка заготовленных данных для работы с БД.

        Args:
            connection_str (str): Строка соединения с БД
            data (Base): Объект или последовательность объектов, соответсвующих моделям в models.py
        """
        engine = create_engine(connection_str, echo=True)
        session = Session(engine)

        # Наполняем БД данными
        try:
            with session as s:
                s.add(data)
                s.commit()
                print(f'Данные добавлены: {data}')
        except Exception as e:
            print(f'Error occured: {e}')

