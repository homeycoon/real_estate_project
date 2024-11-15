from dash import dcc, html
import dash_bootstrap_components as dbc

from dashboard.data import load_data

df = load_data()


# Формируем макет дашборда
def make_layout():

    filter_id_dict = {
        'source': 'Источник',
        'city_area': 'Район города',
        'microdistrict': 'Микрорайон',
        'building_type': 'Тип помещения',
        'floor': 'Этаж',
    }

    # Фильтры
    lst_of_filters = [
        html.Div(
            children=dcc.Dropdown(
                options=sorted(
                    [
                        {'label': value, 'value': value} for value in df[filter_key].unique()
                        if value != 'not_found' and value != 'not_defined'
                    ],
                    key=lambda item: item['value']
                ),
                id=f'{filter_key}-filter-slider',
                multi=True,
                searchable=True,
                placeholder=filter_value
            )
        ) for filter_key, filter_value in filter_id_dict.items()
    ]

    # KPI
    lst_if_KPIs = [
        html.Div(
            children=dbc.Card(),
            id=f'KPI{i}-with-slider'
        ) for i in range(1, 6)
    ]

    # Графики с основной инфо
    hist_fig_ads_ca = html.Div(children=dcc.Graph(id='graph_ads_ca-with-slider'))
    pie_fig_ads_bt = html.Div(children=dcc.Graph(id='graph_ads_bt-with-slider'))
    scatter_fig_pps_vs_s = html.Div(children=dcc.Graph(id='graph_pps_vs_s-with-slider'))
    hist_fig_pps = html.Div(children=dcc.Graph(id='graph_hist_pps-with-slider'))
    hist_fig_square = html.Div(children=dcc.Graph(id='graph_hist_square-with-slider'))

    # Графики со статистикой
    box_fig_pps_by_d = html.Div(children=dcc.Graph(id='graph_pps_by_d-with-slider'))
    box_fig_pps_by_bt = html.Div(children=dcc.Graph(id='graph_pps_by_bt-with-slider'))
    box_fig_p_by_d = html.Div(children=dcc.Graph(id='graph_p_by_d-with-slider'))
    box_fig_p_by_bt = html.Div(children=dcc.Graph(id='graph_p_by_bt-with-slider'))
    box_square_by_dis = html.Div(children=dcc.Graph(id='graph_s_by_d-with-slider'))
    box_square_by_bt = html.Div(children=dcc.Graph(id='graph_s_by_bt-with-slider'))

    # Разметка
    title_div = html.H1('Дашборд по рынку аренды коммерческой недвижимости в Казани')
    filters_div = html.Div(lst_of_filters, id='filters_div')
    KPIs_div = html.Div(lst_if_KPIs, id='cards_div')
    upper_div = html.Div(
        [
            html.Div([pie_fig_ads_bt, hist_fig_ads_ca], style={'width': '30%'}),
            html.Div([scatter_fig_pps_vs_s], style={'width': '40%'}),
            html.Div([hist_fig_pps, hist_fig_square], style={'width': '30%'})
        ],
        style={'display': 'flex'}
    )
    subtitle_div = html.H2('Статистика в разрезе районов и типов помещений')
    lower_div = html.Div(
        [
            html.Div([box_fig_pps_by_d, box_fig_pps_by_bt], style={'width': '33%'}),
            html.Div([box_fig_p_by_d, box_fig_p_by_bt], style={'width': '34%'}),
            html.Div([box_square_by_dis, box_square_by_bt], style={'width': '33%'})
        ],
        style={'display': 'flex', 'width': '100%'}
    )

    # Конечный макет
    layout = html.Div(
        children=[
            # Navbar
            html.Div(
                className="navbar",
                children=[
                    # Главное меню
                    html.Ul(
                        className="mainmenu",
                        children=[
                            html.Li(html.A("Главная страница", href="/")),
                            html.Li("|"),
                            html.Li(html.A("Дашборд", href="/dash")),
                            html.Li("|"),
                            html.Li(html.A("Калькулятор", href="/calculator")),
                        ]
                    ),
                    # Кнопка "Выгрузить в .xlsx"
                    html.Div(
                        className="button-container",
                        children=[html.A("Выгрузить в .xlsx", href="/export_to_excel", className="excel-button")]
                    )
                ]
            ),
            # Сам дашборд
            html.Div(
                children=[
                    title_div,
                    filters_div,
                    KPIs_div,
                    upper_div,
                    subtitle_div,
                    lower_div
                ]
            )
        ],
    )

    return layout
