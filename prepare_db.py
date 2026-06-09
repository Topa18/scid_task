from db_definer import DbDefiner

from config import CONFIG, DB_NAME, DEV_DB_NAME, DB_USER, DB_PASSWORD
from config import CONN_STR, DEV_CONN_STR
from config import data_list


def prep_db():
    """
    Использует класс DbDefiner для подготовки двух БД:
    тестовой и "боевой", и их наполнения шаблонными данными.
    """
    
    definer = DbDefiner(CONFIG, DB_NAME, DEV_DB_NAME,
                        DB_USER, DB_PASSWORD)
    definer.create_schema_and_user()
    definer.create_tables(connection_str=CONN_STR)
    definer.create_tables(connection_str=DEV_CONN_STR)

    for data in data_list:
        definer.insert_data(CONN_STR, data=data)
        definer.insert_data(DEV_CONN_STR, data=data)


    #Для теста
    # definer.drop(CONN_STR)
    # definer.drop(DEV_CONN_STR)