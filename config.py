import os
from dotenv import load_dotenv
from models import User, Address, Item, Category


load_dotenv()

reference_config = {
    'host': os.getenv('REF_PG_HOST'),
    'port': os.getenv('REF_PG_PORT'),
    'database': os.getenv('REF_PG_DB'),
    'user': os.getenv('REF_PG_USER'),
    'password': os.getenv('REF_PG_PW')
}

target_config = {
    'host': os.getenv('TRGT_PG_HOST'),
    'port': os.getenv('TRGT_PG_PORT'),
    'database': os.getenv('TRGT_PG_DB'),
    'user': os.getenv('TRGT_PG_USER'),
    'password': os.getenv('TRGT_PG_PW')
}

CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('MYSQL_ROOT_USER'),
    'password': os.getenv('MYSQL_ROOT_PW')
          }

DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

CONN_STR = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{CONFIG.get('host')}/{DB_NAME}"


# Данные для наполнения БД
frst_user = User(id=1, name='Ivan')
sec_user = User(id=2, name='Alexey')
trhd_user = User(id=3, name='Vasya')

frst_address = Address(id=1, 
                       user_id=frst_user.id,
                       city='Moscow',
                       email_address='ivan@gmail.com')
sec_address = Address(id=2,
                      user_id=sec_user.id,
                      city='Tula',
                      email_address='alextula@gmail.com')
trhd_address = Address(id=3,
                       user_id=trhd_user.id,
                       city='Spb',
                       email_address='vasya@gmail.com')


frst_category = Category(id=1, name='Cars')
sec_category = Category(id=2, name='Planes')


frst_item = Item(id=1,
                 name='Toyota',
                 category_id=frst_category.id,
                 description="Japan car",
                 price=1000.0)
sec_item = Item(id=2,
                name='BMW',
                category_id=frst_category.id,
                description="German car",
                price=1500.0)
thrd_item = Item(id=3,
                 name='AN-21',
                 category_id=sec_category.id,
                 description="Plane for low altitude trips",
                 price=2000.0)


data_list = [frst_user, sec_user, trhd_user,
             frst_address, sec_address, trhd_address,
             frst_category, sec_category,
             frst_item, sec_item, thrd_item]

