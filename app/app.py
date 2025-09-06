from flask import Flask, render_template, request, make_response
from dash import dash
from dotenv import load_dotenv

from config import Config
from dashboard.layout import make_layout
from dashboard.callbacks import define_callbacks
from database.db_gateway import DBGateway
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
    """
    Эндпоинт для формирования главной страницы
    с картой медианной стоимости аренды
    по районам города Казань
    """

    build_graph()
    return render_template('index.html')


@app.route('/export_to_excel')
def export_to_excel():
    """
    Эндпоинт для выгрузки информации
    в Excel (по кнопке "Выгрузить в .xlsx")
    """

    result = to_excel_process()
    result.seek(0)

    response = make_response(result.read())
    response.headers['Content-Disposition'] = 'attachment; filename=real_estate_Kazan.xlsx'
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return response


# Страница с калькулятором
@app.route('/calculator', methods=['GET', 'POST'])
def calculator():
    """
    Эндпоинт для формирования страницы
    с калькулятором и расчета примерной
    стоимости квартиры в соответствии
    с заданными параметрами

    :return: возвращает HTML страницу
    """

    params_list = ['city_area', 'microdistrict',
                   'floor', 'building_type',
                   'utility_payments',
                   'maintenance_costs',
                   'tax', 'undergrounds']
    db_gateway = DBGateway()
    result_params_dict = db_gateway.get_bd_data(params_list)

    form = CalculatorForm(city_areas=result_params_dict['city_area'],
                          microdistricts=result_params_dict['microdistrict'],
                          floors=result_params_dict['floor'],
                          building_types=result_params_dict['building_type'],
                          utility_payments_l=result_params_dict['utility_payments'],
                          maintenance_costs_l=result_params_dict['maintenance_costs'],
                          taxes=result_params_dict['tax'],
                          undergrounds_l=result_params_dict['undergrounds'])

    if request.method == 'POST':
        square = request.form.get('square')

        new_params_dict = {}
        for param in params_list:
            if param == 'floor':
                if request.form.get(param) != 'Не выбрано':
                    param_value = int(request.form.get(param))
                else:
                    param_value = request.form.get(param)
            else:
                param_value = str(request.form[param])
            new_params_dict[param] = param_value

        result = db_gateway.get_bd_data_by_filters(new_params_dict)

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
