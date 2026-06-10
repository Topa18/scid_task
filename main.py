import os
from db_definer import DbDefiner
from manager import AlembicManager

from config import CONFIG, DB_NAME, DEV_DB_NAME, DB_USER, DB_PASSWORD
from config import CONN_STR, DEV_CONN_STR
from config import data_list
from prepare_db import prep_db, drop_db


def main():
    # prep_db()
    manager = AlembicManager(db_url=CONN_STR)
    manager.init_alembic()
    manager.create_migration('test', autogenerate=True)
    manager.upgrade()

if __name__ == '__main__':
    main()