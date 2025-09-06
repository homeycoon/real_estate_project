import json
import os

import plotly.graph_objs as go
import plotly.io as pio
import requests

from database.db_gateway import DBGateway


def download_districs_boarders(districts_names_list: list[str]) -> dict:
    if not os.path.isfile("geo_main_page/kazan_borders.json"):
        # Если нет файла с границами, скачиваем данные и записываем в файл

        district_dict = {
            "type": "FeatureCollection",
            "licence": "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright",
            "features": []
        }

        for indx, district in enumerate(districts_names_list):
            result = requests.get(
                f"https://nominatim.openstreetmap.org/search?q=Казань+{district}&format=geojson&polygon_geojson=1&featureType=settlement",
                headers={'User-Agent': 'Mozilla/5.0 (compatible; HandsomeBrowser/1.2)'}
            )
            serialized_result = json.loads(result.text)
            district_data = serialized_result["features"][0]
            district_data["id"] = indx
            district_dict["features"].append(district_data)

        final_result = json.dumps(district_dict)

        with open("geo_main_page/kazan_borders.json", "w", encoding="utf-8") as file:
            file.write(final_result)

    with open("geo_main_page/kazan_borders.json", "r", encoding="utf-8") as file:
        district_dict = json.loads(file.read())

    return district_dict


# Создаем график (используется на главной странице)
def build_graph():

    districts_names_list = [
        "Вахитовский+район",
        "Авиастроительный+район",
        "Советский+район",
        "Кировский+район",
        "Приволжский+район",
        "Московский+район",
        "Ново-Савиновский+район"
    ]

    # Выгружаем районы с рассчитанными по ним медианам стоимости 1 кв.м.
    db_gateway = DBGateway()
    city_areas = db_gateway.get_city_districts()

    for district_name in districts_names_list:
        district_name = district_name.replace('+', ' ')
        if district_name not in city_areas:
            city_areas[district_name] = 0.00

    # Выгружаем данные о границах из файла
    district_dict = download_districs_boarders(districts_names_list)

    # Формируем график
    fig = go.Figure(go.Choroplethmapbox(
        geojson=district_dict,
        locations=[x["id"] for x in district_dict["features"]],
        colorscale="Plasma",
        text=[x["properties"]["name"] for x in district_dict["features"]],
        z=[city_areas[x["properties"]["name"]] for x in district_dict["features"]],
        marker_opacity=0.85,
        hovertemplate='<b>%{text}</b><br>Медианная стоимость 1 кв.м.: %{z} руб.<extra></extra>',
        hoverinfo='text, z'
    ))
    fig.update_traces(marker_line_color='grey',
                      colorbar_bgcolor='#1F2833',
                      colorbar_tickfont_color='#D3D3D3')
    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=9,
                      mapbox_center = {"lat": 55.7944, "lon": 49.1108},
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})

    pio.write_html(fig, file='./static/interactive_map.html', auto_open=False)
