from mysql.connector import connect, Error
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect
from models import Base
from typing import Optional
import logging


class DbDefiner:
    """
    Объект - инциализатор схемы БД, пользователя и таблиц в БД.

    Args:
        config (dict): Параметры подключения к БД с root доступом\n
                       {'host': host,\n
                        'user': user,\n
                        'password': password}.
        db_name (str): Имя основной базы данных.
        db_user (str): Имя пользователя для доступа к БД.
        db_password (str): Пароль пользователя db_user.
    """

    def __init__(self, config:dict, db_name:str,
                 db_user:str, db_password:str,
                 logger: Optional[logging.Logger] = None):
        self.config = config
        self.host = config.get('host')
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.logger = logger or logging.getLogger(__name__)
        
        
    def create_schema_and_user(self):
        """
        Настройка и инициализация баз данных и пользователя.
        """
        try:
            with connect(**self.config) as connection:
                with connection.cursor() as cursor:
                    # Создаем БД 
                    cursor.execute(f'CREATE DATABASE IF NOT EXISTS {self.db_name}')
                    # Создаем пользователя
                    cursor.execute(f'CREATE USER IF NOT EXISTS\'{self.db_user}\'@\'{self.host}\''\
                                   f'IDENTIFIED BY \'{self.db_password}\'')
                    # Наделяем пользователя правами к созданным БД
                    cursor.execute(f'GRANT ALL PRIVILEGES ON {self.db_name}.*' \
                                   f'TO \'{self.db_user}\'@\'{self.host}\'')
                    cursor.execute('FLUSH PRIVILEGES')
                    
                    self.logger.info(f'База данных {self.db_name} подготовлена')
                    self.logger.info(f'Пользователь \'{self.db_user}\'@\'{self.host}\' подготовлен')
        except Error as e:
            self.logger.error(f'Error occured: {e}')

    def create_tables(self, connection_str:str):
        """
        Создание таблиц, если они не были созданы ранее.
        В ином случае None

        Args:
            connection_str (str): Строка соединения с БД
        """
        engine = create_engine(connection_str)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        if not tables:
            Base.metadata.create_all(bind=engine)
            self.logger.info("Таблицы созданы")
        else:
            self.logger.info("Таблицы уже были созданы")
                                                        
    def drop(self, connection_str):
        """
        Удаление всех таблиц с данными.

        Args:
            connection_str (str): Строка соединения с БД
        """
        engine = create_engine(connection_str)
        Base.metadata.drop_all(bind=engine)

    def insert_data(self, connection_str:str, data:Base):
        """
        Вставка заготовленных данных для работы с БД.

        Args:
            connection_str (str): Строка соединения с БД
            data (Base): Объект или последовательность объектов, соответсвующих моделям в models.py
        """
        engine = create_engine(connection_str)
        session = Session(engine)

        # Наполняем БД данными
        try:
            with session as s:
                s.add(data)
                s.commit()
                self.logger.info(f'Данные добавлены: {data}')
        except Exception as e:
            self.logger.error(f'Error occured: {e}')

