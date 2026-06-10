from alembic.config import Config
from alembic import command
from alembic.script import ScriptDirectory
from alembic.runtime.migration import MigrationContext
import sqlalchemy as sa
from typing import Optional, List
import os
import subprocess


class AlembicManager:
    def __init__(self,
                 alembic_ini_path: str = 'alembic.ini',
                 migrations_dir: str = 'migrations',
                 db_url: Optional[str] = None):
        self.alembic_cfg = Config(alembic_ini_path)
        self.alembic_ini_path = alembic_ini_path
        self.migrations_dir = migrations_dir
        self.db_url = db_url

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
        with self.alembic_cfg.attributes['connection'].connect() as conn:
            context = MigrationContext.configure(conn)
            return context.get_current_revision()
    
    def stamp(self, revision: str):
        """Отметить БД как имеющую определенную ревизию"""
        command.stamp(self.alembic_cfg, revision)