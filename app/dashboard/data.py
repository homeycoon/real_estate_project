from database.db_gateway import DBGateway


# Выгружаем данные из БД и строим доп. столбец 'price/square'
def load_data():
    db_gateway = DBGateway()
    df = db_gateway.get_full_data()
    return df
