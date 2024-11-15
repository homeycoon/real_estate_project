import sqlite3

from flask import Flask, render_template, request, make_response
from dash import dash
from dotenv import load_dotenv

from config import Config
from dashboard.layout import make_layout
from dashboard.callbacks import define_callbacks
from forms import CalculatorForm
from geo_main_page.geo import build_graph
from dashboard.to_excel import to_excel_process

load_dotenv()

app = Flask('real_estate_project')
app.config.from_object(Config)

# Для страницы с дашбордом
dash_app = dash.Dash(server=app,
                     routes_pathname_prefix='/dash/')
dash_app.layout = make_layout()
define_callbacks(dash_app=dash_app)


# Главная страница
@app.route('/')
def main_page():
    build_graph()
    return render_template('index.html')


# Роутер для выгрузки информации в Excel (по кнопке "Выгрузить в .xlsx")
@app.route('/export_to_excel')
def export_to_excel():
    result = to_excel_process()
    result.seek(0)

    response = make_response(result.read())
    response.headers['Content-Disposition'] = 'attachment; filename=real_estate_Kazan.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return response


# Страница с калькулятором
@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    with (sqlite3.connect('database/real_estate.db') as connection):
        cursor = connection.cursor()
        cursor.execute('SELECT DISTINCT city_area FROM real_estate')
        city_areas = [x[0] for x in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT microdistrict FROM real_estate')
        microdistricts = [x[0] for x in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT floor FROM real_estate')
        floors = [x[0] for x in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT building_type FROM real_estate')
        building_types = [x[0] for x in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT utility_payments FROM real_estate')
        utility_payments_l = [x[0] for x in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT maintenance_costs FROM real_estate')
        maintenance_costs_l = [x[0] for x in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT tax FROM real_estate')
        taxes = [x[0] for x in cursor.fetchall()]
        cursor.execute('SELECT DISTINCT undergrounds FROM real_estate')
        undergrounds_set = set()
        all_undergrounds = [x[0].split(', ') for x in cursor.fetchall()]
        for items in all_undergrounds:
            for underground in items:
                undergrounds_set.add(underground)
        undergrounds_l = list(undergrounds_set)

    form = CalculatorForm(city_areas=city_areas, microdistricts=microdistricts,
                          floors=floors, building_types=building_types,
                          utility_payments_l=utility_payments_l,
                          maintenance_costs_l=maintenance_costs_l,
                          taxes=taxes, undergrounds_l=undergrounds_l)
    if request.method == 'POST':
        square = request.form['square']
        city_area = str(request.form['city_area'])
        microdistrict = str(request.form['microdistrict'])
        floor = int(request.form['floor']) if request.form['floor'] != 'Не выбрано' else request.form['floor']
        building_type = str(request.form['building_type'])
        utility_payments = str(request.form['utility_payments'])
        maintenance_costs = str(request.form['maintenance_costs'])
        undergrounds = str(request.form['undergrounds'])
        tax = str(request.form['tax'])

        with sqlite3.connect('database/real_estate.db') as connection:

            all_filters = (city_area, microdistrict, floor,
                           building_type, utility_payments,
                           maintenance_costs, tax, undergrounds)

            chosen_filters = [field for field in all_filters if field != "Не выбрано"]

            text = ('WITH cte1 AS ('
                    'SELECT price / square AS price_per_square '
                    'FROM real_estate')
            if chosen_filters:
                text += ' WHERE '
                conditions = []
                if city_area in chosen_filters:
                    conditions.append('city_area = (?)')
                if microdistrict in chosen_filters:
                    conditions.append('microdistrict = (?)')
                if floor in chosen_filters:
                    conditions.append('floor = (?)')
                if building_type in chosen_filters:
                    conditions.append('building_type = (?)')
                if utility_payments in chosen_filters:
                    conditions.append('utility_payments = (?)')
                if maintenance_costs in chosen_filters:
                    conditions.append('maintenance_costs = (?)')
                if tax in chosen_filters:
                    conditions.append('tax = (?)')
                if undergrounds in chosen_filters:
                    conditions.append('undergrounds IN (?)')
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
            cursor.execute(text, chosen_filters, )

            result = cursor.fetchone()
            if result:
                estimated_price = int(result[0]) * int(square)
            else:
                estimated_price = "примеры квартир с такими параметрами не найдены"
    elif request.method == 'GET':
        estimated_price = None
    else:
        return render_template('page404.html')

    return render_template('calculator.html',
                           form=form,
                           estimated_price=estimated_price
                           )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
