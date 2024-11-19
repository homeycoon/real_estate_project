from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.fields.numeric import IntegerField
from wtforms.validators import NumberRange, DataRequired


# Создаем форму для страницы "Калькулятор"
class CalculatorForm(FlaskForm):
    square = IntegerField("Площадь: ", validators=[
        NumberRange(min=0, max=1000,
                    message="Площадь должна быть в "
                            "диапазоне от 0 до 1000 "
                            "квадратных метров.")
    ])
    city_area = SelectField("Район города: ", validators=[DataRequired()])
    microdistrict = SelectField("Микрорайон: ", validators=[DataRequired()])
    floor = SelectField("Этаж: ", validators=[DataRequired()])
    building_type = SelectField("Тип здания: ", validators=[DataRequired()])
    utility_payments = SelectField("Коммунальные платежи: ", validators=[DataRequired()])
    maintenance_costs = SelectField("Эксплуатационные расходы: ", validators=[DataRequired()])
    undergrounds = SelectField("Метро: ", validators=[DataRequired()])
    tax = SelectField("Налог: ", validators=[DataRequired()])

    def __init__(self, city_areas=[], microdistricts=[], floors=[],
                 building_types=[], utility_payments_l=[], maintenance_costs_l=[],
                 undergrounds_l=[], taxes=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.city_area.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, x) for x in city_areas if x != 'not_found'], key=lambda x: x[0])
        self.microdistrict.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, x) for x in microdistricts if x != 'not_found'], key=lambda x: x[0])
        self.floor.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, str(x)) for x in floors if x != 'not_found'], key=lambda x: x[0])
        self.building_type.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, x) for x in building_types if x != 'not_defined'], key=lambda x: x[0])
        self.utility_payments.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, x) for x in utility_payments_l if x != 'not_found'], key=lambda x: x[0])
        self.maintenance_costs.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, x) for x in maintenance_costs_l if x != 'not_found'], key=lambda x: x[0])
        self.undergrounds.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, x) for x in undergrounds_l if x != 'not_found'], key=lambda x: x[0])
        self.tax.choices = [('Не выбрано', 'Не выбрано')] + sorted([(x, x) for x in taxes if x != 'not_found'], key=lambda x: x[0])
