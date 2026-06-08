import os
from db_definer import DbDefiner
from dotenv import load_dotenv

load_dotenv()

CONFIG = {'host': os.getenv('DB_HOST'),
            'user': os.getenv('MYSQL_ROOT_USER'),
            'password': os.getenv('MYSQL_ROOT_PW')}
DB_NAME = os.getenv('DB_NAME')
DEV_DB_NAME = os.getenv('DEV_DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

def main():
    definer = DbDefiner(CONFIG, DB_NAME, DEV_DB_NAME,
                        DB_USER, DB_PASSWORD)
    definer.create_schema_and_user()

if __name__ == '__main__':
    main()