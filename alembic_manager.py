from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
from typing import Optional
from contextlib import contextmanager
import sqlalchemy as sa
import os
import subprocess
import logging


class AlembicManager:
    """
    Класс для управления миграциями БД

    Args:
        alembic_ini_path (str): Путь к alembic.ini.
        migrations_dir (str): Путь к папке migrations.
        db_url (str): Строка подключения к БД.
        logger (logging.Logger): По умолчанию logging.Logger.
    """

    def __init__(self,
                 alembic_ini_path: str = 'alembic.ini',
                 migrations_dir: str = 'migrations',
                 db_url: Optional[str] = None,
                 logger: Optional[logging.Logger] = None):
        self.alembic_cfg = Config(alembic_ini_path)
        self.script = ScriptDirectory.from_config(self.alembic_cfg)
        self.alembic_ini_path = alembic_ini_path
        self.migrations_dir = migrations_dir
        self.db_url = db_url
        self.logger = logger or logging.getLogger(__name__)

    def init_alembic(self):
        """Инициализирует Alembic, если конфигурация не существует"""
        if not os.path.exists(self.alembic_ini_path):
            result = subprocess.run(
                ['alembic', 'init', self.migrations_dir],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return True
            else:
                raise Exception(f"Error occured: {result.stderr}")
        return False 

    def upgrade(self, revision: str = 'head'):
        """Применить миграции до указанной ревизии"""
        command.upgrade(self.alembic_cfg, revision)

    def downgrade(self, revision: str = 'base'):
        """Откат миграций"""
        command.downgrade(self.alembic_cfg, revision)

    def create_migration(self, message: str, autogenerate: bool = False):
        """Создание миграции"""
        command.revision(
            self.alembic_cfg,
            message=message,
            autogenerate=autogenerate
        )

    def get_current_revision(self):
        """Получить текущую ревизию"""
        try:
            # Получаем URL базы данных
            database_url = self.alembic_cfg.get_main_option("sqlalchemy.url")
            engine = sa.create_engine(database_url)
            
            with engine.connect() as conn:
                context = MigrationContext.configure(conn)
                return context.get_current_revision()
        except Exception as e:
            # Если таблицы alembic_version не существует
            error_msg = str(e).lower()
            if "doesn't exist" in error_msg or "no such table" in error_msg:
                return None
            
        
    def get_heads(self):
        """Получить список head-ревизий"""
        return self.script.get_heads()
    
    def stamp(self, revision: str):
        """Отметить БД как имеющую определенную ревизию"""
        command.stamp(self.alembic_cfg, revision)

# Написано с DeepSeek - разбирал с ним, потому что эта часть
# создания класса оказалась сложной для меня
    @contextmanager
    def _handle_errors(self, operation: str):
        """Контекстный менеджер для обработки ошибок"""
        try:
            yield
        except Exception as e:
            self.logger.error(f"Failed to {operation}: {e}")
            raise RuntimeError(f"Alembic {operation} failed") from e
        

    def upgrade_with_check(self, revision: str = 'head') -> bool:
        """Выполнить upgrade с проверкой успешности"""
        try:
            current = self.get_current_revision()
            self.upgrade(revision)
            new_revision = self.get_current_revision()

            self.logger.info(
                f"Upgrated from {current} to {new_revision}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Upgrade failed: {e}")
            return False
        
    def ensure_migrations_applied(self, target_revision: str = 'head'):
        """Гарантировать, что все миграции применены"""
        current = self.get_current_revision()
        heads = self.get_heads()

        if current not in heads:
            self.logger.warning(
                f"Current revision {current} is not in a head. Upgrating..."
            )
            self.upgrade(target_revision)

    def create_and_apply_migration(
            self,
            message: str,
            autogenerate: bool = True
            ):
        """Создать и применить миграцию"""
        with self._handle_errors('create migration'):
            self.create_migration(message, autogenerate)
            self.upgrade_with_check()
            self.logger.info(f"Created and applied migration: {message}")