from mysql.connector import connect, Error


class DbDefiner():
    """
    Настройка и инициализация баз данных и пользователя.

    Args:
        config (dict): Параметры подключения к БД с root доступом
                       (host, user, password).
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