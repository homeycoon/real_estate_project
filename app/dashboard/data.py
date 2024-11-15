import sqlite3
import pandas as pd


# Выгружаем данные из БД и строим доп. столбец 'price/square'
def load_data():
    conn = sqlite3.connect('./database/real_estate.db')
    df = pd.read_sql('select * from real_estate', conn)
    df['price/square'] = round(df['price'] / df['square'], 2)
    return df
