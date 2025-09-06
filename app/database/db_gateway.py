import sqlite3
import pandas as pd


class DBGateway:
    def __init__(self):
        self.db_name = 'database/real_estate.db'

    def get_bd_data(self, params_list: list[str]):
        """
        Получение значений по определенным параметрам
        :param params_list: список параметров (полей)
        :return: словарь с полученными значениями
        """
        with (sqlite3.connect(self.db_name) as connection):
            cursor = connection.cursor()
            result_params_dict = {}
            for param in params_list:
                cursor.execute('SELECT DISTINCT (?) FROM real_estate', (param,),)
                if param == 'undergrounds':
                    undergrounds_set = set()
                    all_undergrounds = [x[0].split(', ') for x in cursor.fetchall()]
                    for items in all_undergrounds:
                        for underground in items:
                            undergrounds_set.add(underground)
                    result = list(undergrounds_set)
                else:
                    result = [x[0] for x in cursor.fetchall()]
                result_params_dict[param] = result

            return result_params_dict

    def get_bd_data_by_filters(self, filters_dict: dict):
        """
        Получение медианной стоимости 1 кв.м. квартир по заданным параметрам
        :param filters_dict: словарь с параметрами запроса
        :return: результат запроса
        """
        with sqlite3.connect(self.db_name) as connection:

            temp_dict = {key: value for key, value in filters_dict if value != 'Не выбрано'}

            text = ('WITH cte1 AS ('
                    'SELECT price / square AS price_per_square '
                    'FROM real_estate')
            if temp_dict:
                text += ' WHERE '
                conditions = []
                values = []
                for key, value in temp_dict:
                    if key == 'undergrounds':
                        conditions.append(f'{key} IN (?)')
                    else:
                        conditions.append(f'{key} = (?)')
                    values.append(value)
                text += ' AND '.join(conditions)
                text += (')'
                         'SELECT CASE WHEN (SELECT COUNT(*) FROM cte1) % 2 = 0 '
                         'THEN '
                         '(SELECT AVG(price_per_square) '
                         'FROM cte1 '
                         'ORDER BY price_per_square '
                         'LIMIT 2 '
                         'OFFSET (SELECT COUNT(*) FROM cte1) / 2 - 1) '
                         'ELSE '
                         '(SELECT price_per_square '
                         'FROM cte1 '
                         'ORDER BY price_per_square '
                         'LIMIT 1 '
                         'OFFSET (SELECT COUNT(*) FROM cte1) / 2) '
                         'END AS median')

            cursor = connection.cursor()
            cursor.execute(text, tuple(values), )
            result = cursor.fetchone()

            return result

    def get_city_districts(self):
        """
        Получение списка райнов города Казань
        с медианной стоимостью 1 кв.м. жилья
        :return:
        """
        with (sqlite3.connect(self.db_name) as connection):
            cursor = connection.cursor()
            cursor.execute('WITH cte1 AS ('
                           'SELECT city_area, price / square AS price_per_square, '
                           'ROW_NUMBER() OVER (PARTITION BY city_area ORDER BY price / square) AS row_num, '
                           'COUNT(*) OVER (PARTITION BY city_area) AS total_rows '
                           'FROM real_estate) '
                           'SELECT city_area, '
                           'CASE WHEN total_rows % 2 = 0 '
                           'THEN '
                           '(SELECT AVG(price_per_square) '
                           'FROM cte1 AS cte2 '
                           'WHERE cte2.city_area = cte1.city_area '
                           'AND cte2.row_num IN (total_rows / 2, (total_rows / 2) + 1)) '
                           'ELSE '
                           '(SELECT price_per_square '
                           'FROM cte1 AS cte2 '
                           'WHERE cte2.city_area = cte1.city_area '
                           'AND cte2.row_num = (total_rows + 1) / 2) '
                           'END AS median '
                           'FROM cte1 '
                           'GROUP BY city_area, total_rows')
            city_areas = {}
            for x in cursor.fetchall():
                city_areas[x[0] + ' район'] = x[1]

            return city_areas

    def get_full_data(self) -> pd.DataFrame:
        """
        Выгрузка полных данных из таблицы real_estate
        и преобразование в датафрейм
        """
        with (sqlite3.connect(self.db_name) as connection):
            df = pd.read_sql('select * from real_estate', connection)
            df['price/square'] = round(df['price'] / df['square'], 2)
            return df
