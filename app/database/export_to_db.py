import sqlite3

from logger import logger


# Создание таблицы, если не существует
def create_table():
    connection = sqlite3.connect('real_estate.db')
    cursor = connection.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS real_estate (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ads_id INTEGER UNIQUE NOT NULL,
            source TEXT NOT NULL,
            building_type TEXT NOT NULL,
            square REAL NOT NULL,
            price REAL NOT NULL,
            tax TEXT NOT NULL,
            comission TEXT NOT NULL,
            utility_payments TEXT NOT NULL,
            security_payments TEXT NOT NULL,
            prepayment TEXT NOT NULL,
            maintenance_costs TEXT NOT NULL,
            floor TEXT NOT NULL,
            all_floors TEXT NOT NULL,
            region TEXT NOT NULL,
            city TEXT NOT NULL,
            city_area TEXT NOT NULL,
            microdistrict TEXT  NOT NULL,
            undergrounds TEXT NOT NULL
        );'''
    )
    connection.close()


# Заполнение таблицы данными, которые были спарсены
# с предварительной проверкой их отсуствия в таблице
def check_db(ads):
    with sqlite3.connect('real_estate.db') as connection:
        cursor = connection.cursor()
        for i, ad in ads.items():
            ad_id = ad['ads_id']
            cursor.execute(
                '''SELECT ads_id FROM real_estate WHERE ads_id = (?)''',
                (ad_id,),
            )
            result = cursor.fetchone()
            if result is None:
                cursor.execute(
                    '''INSERT INTO real_estate
                    VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                    tuple(ad.values()),
                )
                connection.commit()
                logger.info(f'Объявление {ad_id} добавлено '
                            'в базу данных "real_estate"')
            else:
                logger.info(f'Объявление {ad_id} !!! НЕ !!! '
                            'добавлено в базу данных "real_estate"')
