from dash import Input, Output, html
import dash_bootstrap_components as dbc
import plotly.express as px

from dashboard.data import load_data

df = load_data()

standard_styles = {
    "font": {'color': '#FFFFFF'},
    "plot_bgcolor": '#242d38',
    "paper_bgcolor": '#242d38'
}


# Отображение KPI в зависимости от выбранных фильтров
def define_callbacks(dash_app):
    # KPI
    @dash_app.callback(
        Output('KPI1-with-slider', 'children'),
        Output('KPI2-with-slider', 'children'),
        Output('KPI3-with-slider', 'children'),
        Output('KPI4-with-slider', 'children'),
        Output('KPI5-with-slider', 'children'),
        Input('source-filter-slider', 'value'),
        Input('city_area-filter-slider', 'value'),
        Input('microdistrict-filter-slider', 'value'),
        Input('building_type-filter-slider', 'value'),
        Input('floor-filter-slider', 'value'))
    def update_KPIs(selected_cities, selected_city_areas, selected_microdistrict,
                    selected_building_types, selected_floors):
        filtered_df = df
        if selected_cities:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_cities)]
        if selected_city_areas:
            filtered_df = filtered_df[filtered_df['city_area'].isin(selected_city_areas)]
        if selected_microdistrict:
            filtered_df = filtered_df[filtered_df['microdistrict'].isin(selected_microdistrict)]
        if selected_building_types:
            filtered_df = filtered_df[filtered_df['building_type'].isin(selected_building_types)]
        if selected_floors:
            filtered_df = filtered_df[filtered_df['floor'].isin(selected_floors)]

        # Общее кол-во объектов
        KPI_amount_card = dbc.CardBody(
                    [html.H6("Количество объявлений", className="card-title"),
                     html.P(filtered_df['ads_id'].count(), className="card-text")]
        )
        # Медианная цена
        KPI_price_avg_card = dbc.CardBody(
            [html.H6("Медианная цена", className="card-title"),
             html.P(f'{round(filtered_df.price.median())} руб.', className="card-text")]
        )
        # Медианная площадь
        KPI_square_med_card = dbc.CardBody(
                [html.H6("Медианная площадь", className="card-title"),
                 html.P(f'{round(filtered_df.square.median())} м2', className="card-text")]
        )
        # Медианная цена за 1 м2
        KPI_pps_med_card = dbc.CardBody(
                [html.H6("Медианная цена 1 м2", className="card-title"),
                 html.P(f'{round(filtered_df["price/square"].median())} руб.', className="card-text")]
        )
        # Средняя цена за 1 м2
        KPI_pps_avg_card = dbc.CardBody(
            [html.H6("Средняя цена 1 м2", className="card-title"),
             html.P(f'{round(filtered_df["price/square"].mean())} руб.', className="card-text")]
        )

        return (KPI_amount_card, KPI_price_avg_card,
                KPI_square_med_card, KPI_pps_med_card, KPI_pps_avg_card)

    # Отображение графиков с основной инфо в зависимости от выбранных фильтров
    @dash_app.callback(
        Output('graph_ads_bt-with-slider', 'figure'),
        Output('graph_ads_ca-with-slider', 'figure'),
        Output('graph_pps_vs_s-with-slider', 'figure'),
        Output('graph_hist_pps-with-slider', 'figure'),
        Output('graph_hist_square-with-slider', 'figure'),
        Input('source-filter-slider', 'value'),
        Input('city_area-filter-slider', 'value'),
        Input('microdistrict-filter-slider', 'value'),
        Input('building_type-filter-slider', 'value'),
        Input('floor-filter-slider', 'value'))
    def update_figs_ads_amount(selected_cities, selected_city_areas, selected_microdistrict,
                               selected_building_types, selected_floors):
        filtered_df = df
        if selected_cities:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_cities)]
        if selected_city_areas:
            filtered_df = filtered_df[filtered_df['city_area'].isin(selected_city_areas)]
        if selected_microdistrict:
            filtered_df = filtered_df[filtered_df['microdistrict'].isin(selected_microdistrict)]
        if selected_building_types:
            filtered_df = filtered_df[filtered_df['building_type'].isin(selected_building_types)]
        if selected_floors:
            filtered_df = filtered_df[filtered_df['floor'].isin(selected_floors)]

        # Pie-chart: количество объявлений по типам помещений
        pie_fig_ads_bt = px.pie(filtered_df,
                                names='building_type',
                                values=filtered_df.value_counts().values,
                                title='Количество объявлений по типам помещений',
                                labels={'city_area': 'Район'},
                                color_discrete_sequence=['#ff6a00'])
        pie_fig_ads_bt.update_traces(hoverinfo='percent',
                                     textinfo='value+percent',
                                     textfont_size=12, textposition="outside",
                                     opacity=0.7)
        pie_fig_ads_bt.update_layout(xaxis={'title': 'Количество объявлений'},
                                     **standard_styles)

        # Столбчатая диаграмма: количество объявлений по районам
        hist_fig_ads_ca = px.histogram(filtered_df,
                                       x='city_area',
                                       title='Количество объявлений по районам города',
                                       labels={'city_area': 'Район'},
                                       color_discrete_sequence=['#ff6a00'])
        hist_fig_ads_ca.update_traces(textfont_size=12,
                                      textposition="outside",
                                      opacity=0.7)
        hist_fig_ads_ca.update_layout(yaxis={'categoryorder': 'total ascending',
                                             'title': None},
                                      xaxis={'title': 'Количество объявлений'},
                                      **standard_styles)

        # Scatter 'price/square VS square'
        scatter_fig_pps_vs_s = px.scatter(filtered_df,
                                          x='price/square',
                                          y='square',
                                          title='График цены 1 м2 vs площади',
                                          labels={'price/square': 'Цена за 1 м2',
                                                  'square': 'Площадь'},
                                          color_discrete_sequence=['#ff6a00'])
        scatter_fig_pps_vs_s.update_traces(opacity=0.7)
        scatter_fig_pps_vs_s.update_layout(**standard_styles)

        # Распределение цен за 1 м2 по рынку
        hist_fig_pps = px.histogram(filtered_df,
                                    x='price/square',
                                    histfunc='count',
                                    title='Распределение цен 1 м2 на рынке',
                                    color_discrete_sequence=['#ff6a00'])
        hist_fig_pps.update_traces(opacity=0.7)
        hist_fig_pps.update_layout(yaxis={'categoryorder': 'total ascending',
                                          'title': 'Количество'},
                                   xaxis={'title': 'Цена 1 м2'},
                                   **standard_styles)

        # Распределение площадей по рынку
        hist_fig_square = px.histogram(filtered_df,
                                         x='square',
                                         histfunc='count',
                                         title='Распределение площадей на рынке',
                                         color_discrete_sequence=['#ff6a00'])
        hist_fig_square.update_traces(opacity=0.7)
        hist_fig_square.update_layout(yaxis={'categoryorder': 'total ascending',
                                             'title': 'Количество'},
                                      xaxis={'title': 'Площадь'},
                                      **standard_styles)

        return (pie_fig_ads_bt, hist_fig_ads_ca, scatter_fig_pps_vs_s,
                hist_fig_pps, hist_fig_square)

    # Отображение графиков со статистикой в зависимости от выбранных фильтров (boxplots)
    @dash_app.callback(
        Output('graph_pps_by_d-with-slider', 'figure'),
        Output('graph_pps_by_bt-with-slider', 'figure'),
        Output('graph_p_by_d-with-slider', 'figure'),
        Output('graph_p_by_bt-with-slider', 'figure'),
        Output('graph_s_by_d-with-slider', 'figure'),
        Output('graph_s_by_bt-with-slider', 'figure'),
        Input('source-filter-slider', 'value'),
        Input('city_area-filter-slider', 'value'),
        Input('microdistrict-filter-slider', 'value'),
        Input('building_type-filter-slider', 'value'),
        Input('floor-filter-slider', 'value'))
    def update_figs_price_square(selected_cities, selected_city_areas, selected_microdistrict,
                                 selected_building_types, selected_floors):
        filtered_df = df.query('city_area != "not_found"')
        filtered_df = filtered_df.query('building_type != "not_defined"')
        if selected_cities:
            filtered_df = filtered_df[filtered_df['source'].isin(selected_cities)]
        if selected_city_areas:
            filtered_df = filtered_df[filtered_df['city_area'].isin(selected_city_areas)]
        if selected_microdistrict:
            filtered_df = filtered_df[filtered_df['microdistrict'].isin(selected_microdistrict)]
        if selected_building_types:
            filtered_df = filtered_df[filtered_df['building_type'].isin(selected_building_types)]
        if selected_floors:
            filtered_df = filtered_df[filtered_df['floor'].isin(selected_floors)]

        # Boxplot: цена за 1 м2 по районам
        box_fig_pps_by_d = px.box(filtered_df,
                                  x='price/square',
                                  y='city_area',
                                  title='Цена 1 м2: по районам города',
                                  labels={'price/square': 'Цена за 1 м2',
                                          'city_area': 'Район'},
                                  color_discrete_sequence=['#ff6a00'])
        box_fig_pps_by_d.update_layout(**standard_styles)

        # Boxplot: цена за 1 м2 по типам помещений
        box_fig_pps_by_bt = px.box(filtered_df,
                                   x='price/square',
                                   y='building_type',
                                   title='Цена 1 м2: по типам помещений',
                                   labels={'price/square': 'Цена за 1 м2',
                                           'building_type': 'Тип помещения'},
                                   color_discrete_sequence=['#ff6a00'])
        box_fig_pps_by_bt.update_layout(**standard_styles)

        # Boxplot: цена по районам
        box_fig_p_by_d = px.box(filtered_df,
                                x='price',
                                y='city_area',
                                title='Цена: по районам города',
                                labels={'price': 'Цена',
                                        'city_area': 'Район'},
                                color_discrete_sequence=['#ff6a00'])
        box_fig_p_by_d.update_layout(**standard_styles)

        # Boxplot: цена по типам помещений
        box_fig_p_by_bt = px.box(filtered_df,
                                 x='price',
                                 y='building_type',
                                 title='Цена: по типам помещенияй',
                                 labels={'price': 'Цена',
                                         'building_type': 'Тип помещения'},
                                 color_discrete_sequence=['#ff6a00'])
        box_fig_p_by_bt.update_layout(**standard_styles)

        # Boxplot: площадь по районам
        box_fig_s_by_d = px.box(filtered_df,
                                x='square',
                                y='city_area',
                                title='Площадь: по районам города',
                                labels={'square': 'Площадь',
                                        'city_area': 'Район'},
                                color_discrete_sequence=['#ff6a00'])
        box_fig_s_by_d.update_layout(**standard_styles)

        # Boxplot площадь по типам помещений
        box_fig_s_by_bt = px.box(filtered_df,
                                 x='square',
                                 y='building_type',
                                 title='Площадь: по типам помещений',
                                 labels={'square': 'Площадь',
                                         'building_type': 'Тип помещения'},
                                 color_discrete_sequence=['#ff6a00'])
        box_fig_s_by_bt.update_layout(**standard_styles)

        return (box_fig_pps_by_d, box_fig_pps_by_bt,
                box_fig_p_by_d, box_fig_p_by_bt,
                box_fig_s_by_d, box_fig_s_by_bt)
