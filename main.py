from alembic_manager import AlembicManager
from config import CONN_STR
from prepare_db import prep_db, drop_db


def main():
    prep_db()

    manager = AlembicManager(db_url=CONN_STR)
    manager.init_alembic()
    manager.create_migration('test', autogenerate=True)
    manager.upgrade()

    # drop_db()

if __name__ == '__main__':
    main()