from db_definer import DbDefiner

from config import CONFIG, DB_NAME, DB_USER, DB_PASSWORD
from config import CONN_STR
from config import data_list


def prep_db():
    """
    Использует класс DbDefiner для подготовки двух БД:
    тестовой и "боевой", и их наполнения шаблонными данными.
    """
    
    definer = DbDefiner(CONFIG, DB_NAME, DB_USER, DB_PASSWORD)
    definer.create_schema_and_user()
    definer.create_tables(connection_str=CONN_STR)

    for data in data_list:
        definer.insert_data(CONN_STR, data=data)

#Для теста
def drop_db():
    definer = DbDefiner(CONFIG, DB_NAME, DB_USER, DB_PASSWORD)
    definer.drop(CONN_STR)