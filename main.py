import os
from db_definer import DbDefiner

from config import CONFIG, DB_NAME, DEV_DB_NAME, DB_USER, DB_PASSWORD
from config import CONN_STR, DEV_CONN_STR
from config import data_list
from prepare_db import prep_db


def main():
    prep_db()


if __name__ == '__main__':
    main()