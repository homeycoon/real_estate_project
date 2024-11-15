from dadata import Dadata
from dotenv import load_dotenv
import os


# Получаем город, район города и микрорайон с помощью сервиса Dadata
def get_address_info(address: str):
    load_dotenv()
    token = os.environ.get("DADATA_TOKEN")
    secret = os.environ.get("DADATA_SECRET")
    with Dadata(token, secret) as dadata:

        for short_name in ("м-н", "мкр.", "мкр-н", "мк-н", "мкр", "мкрн", "м/н", "м/р-н", "мрн"):
            if short_name in address:
                microdistrict_data = list(
                    filter(lambda x: short_name in x, address.split(", "))
                )[0].replace(short_name, "").strip()
                clean_address = "Республика Татарстан, Казань, " + ", ".join(
                    list(filter(lambda x: short_name not in x, address.split(", "))))
                break
            else:
                microdistrict_data = "not_found"
                clean_address = address

        try:
            suggestion = dadata.suggest(name="address", query=clean_address)
            result = dadata.suggest(name="address", query=suggestion[0].get("unrestricted_value"), count=1)
            city = result[0].get("data", {}).get("city", "not_found")
            city_area = result[0].get("data", {}).get("city_district", "not_found")
        except:
            city = "Казань"
            city_area = "not_found"

        new_result = {
            "region": "Республика Татарстан",
            "city": city,
            "city_area": city_area if city_area else "not_found",
            "microdistrict": microdistrict_data
        }
    return new_result
