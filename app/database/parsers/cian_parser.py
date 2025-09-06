import requests
from bs4 import BeautifulSoup as bs
import re
import time

from logger import logger
from .dadata_func import get_address_info


class CIAN_pages:
    """
    Класс для сбора url-ов объявлений
    в рамках выбранного количества страниц
    на сайте ЦИАНа
    """
    def __init__(self, url, num_of_pages):
        self.url = url
        self.num_of_pages = num_of_pages
        self.list_of_url = []

    def __call__(self):
        for i in range(2, self.num_of_pages+1):
            url = self.url.replace('{???}', str(i))
            response = requests.get(url)

            if response.status_code == 200:
                text = bs(response.text, 'html.parser')
                all_url = text.find_all('h3', class_="_32bbee5fda--header-title--gznMp")
                for j in all_url:
                    urls = j.find('a', href=True)
                    self.list_of_url.append(urls['href'])
                time.sleep(2)
            else:
                logger.info(response.status_code)
        return self.list_of_url


class CIAN_ads:
    """
    Класс для сбора данных по каждому объявлению
    на сайте ЦИАНа
    """
    def __init__(self, url_list):
        self.url_list = url_list[:50]
        self.info_dict = {}

    def __call__(self):
        unik_id = 0

        for new_url in self.url_list:
            unik_id += 1
            source = 'ЦИАН'

            time.sleep(5)
            regex = r'https://kazan\.cian\.ru/rent/commercial/(.*)/'
            ads_url = int(re.findall(regex, new_url)[0])

            response_page = requests.get(new_url)
            if response_page.status_code == 200:
                text_of_page = bs(response_page.text, 'html.parser')

                name_info = text_of_page.find('div', {'data-name': "OfferTitleNew"})
                name = name_info.text
                name = name.replace('\xa0', ' ')
                if 'торг' in name.lower():
                    type = 'Торговая площадь'
                elif 'офис' in name.lower():
                    type = 'Офис'
                elif 'своб' in name.lower() and 'назн' in name.lower():
                    type = 'Свободного назначения'
                else:
                    type = 'not_defined'

                if text_of_page.find_all('div', class_="a10a3f92e9--area-parts-wrapper--Ac3xY"):
                    elems = text_of_page.find_all('div', {'data-name': 'AreasRow'})
                    for elem in elems:

                        square_info = elem.find('div', class_="a10a3f92e9--area-data-wrapper--IedAi")
                        square = square_info.text
                        square = square.replace('\xa0', '')
                        square = square.replace('Площадь', '')
                        square = square.replace('м²', '')
                        square = float(square.replace(',', '.').strip())

                        floor_info = elem.find('span',
                                               class_='a10a3f92e9--color_gray60_100--mYFjS a10a3f92e9--'
                                                      'lineHeight_5u--e6Sug a10a3f92e9--fontWeight_normal--JEG_c '
                                                      'a10a3f92e9--fontSize_14px--reQMB a10a3f92e9--display_block--'
                                                      'KYb25 a10a3f92e9--text--e4SBY a10a3f92e9--text_letterSpacing__0--cQxU5')
                        floor = floor_info.text
                        floor = floor.replace(' этаж', '')

                        price_info = elem.find('div', class_="a10a3f92e9--price-data-wrapper--dAWkY")
                        price = price_info.text
                        price = price.replace('\xa0', '')
                        price = price.replace('₽/мес.', '')
                        price = float(price.replace(',', '.').strip())
                else:
                    square = 'not_found'
                    floor = 'not_found'
                    price = 'not_found'

                try:
                    additional_elems = text_of_page.find('p', class_='a10a3f92e9--description--BAbY2')
                    additional = additional_elems.text
                    regex = r'(обеспечительный&nbsp;платёж&nbsp;)(.+)(&nbsp;₽)'
                    security_payment = re.search(regex, additional).group(2)
                    regex = r'(предоплата&nbsp;за&nbsp;)(.+)'
                    prepayment = re.search(regex, additional).group(2)
                    prepayment = prepayment.replace('&nbsp;', '')
                except:
                    security_payment = 'not_found'
                    prepayment = 'not_found'

                time.sleep(2)
                ness_properties = text_of_page.find('address')
                address_info = ness_properties.find_all('a', class_='a10a3f92e9--address--SMU25')
                address_list = [address_item.text for address_item in address_info]
                full_address_data = get_address_info(", ".join(address_list))
                region = full_address_data["region"]
                city = full_address_data["city"]
                city_area = full_address_data["city_area"]
                microdistrict = full_address_data["microdistrict"]

                underground_list = [j.text for j in ness_properties.find_all('a', class_='a10a3f92e9--underground_link--VnUVj')]
                undergrounds = ', '.join(underground_list)
                if not underground_list:
                    undergrounds = 'not_found'

                add_properties = text_of_page.find_all('div', {'data-name': 'OfferFactItem'})
                new_list = [property.text for property in add_properties]

                tax = new_list[1].replace('Налог', '')
                comission = new_list[2].replace('Комиссии', '')
                utility_payments = new_list[3].replace('Коммунальные платежи', '')
                maintenance_costs = new_list[4].replace('Эксплуатационные расходы', '')

                time.sleep(2)

                floor_info = text_of_page.find_all('div', class_='a10a3f92e9--text--eplgM')
                floor_list = [p.text for p in floor_info[1].find_all('span')]
                all_floors = floor_list[1][-1]

                if square == 'not_found':
                    square_new_info = text_of_page.find('div', class_='a10a3f92e9--text--eplgM')
                    square = square_new_info.text
                    square = square.replace('\xa0', '')
                    square = square.replace('Площадь', '')
                    square = square.replace('м²', '').strip()
                    square = float(square.replace(',', '.').strip())
                if floor == 'not_found':
                    floor = floor_list[1][0]
                    floor = floor.replace(' этаж', '')
                if price == 'not_found':
                    price_new_info = text_of_page.find('div', {'data-testid': 'price-amount'})
                    price = price_new_info.text
                    price = price.replace('\xa0', '')
                    price = price.replace('₽/мес.', '').strip()
                    price = float(price.replace(',', '.').strip())
                if tax == 'НДС не включен':
                    price = price * 1.2
                    tax = 'НДС включен'

                self.info_dict[unik_id] = {'ads_id': ads_url,
                                           'source': source,
                                           'building_type': type,
                                           'square': square,
                                           'price': price,
                                           'tax': tax,
                                           'comission': comission,
                                           'utility_payments': utility_payments,
                                           'security_payments': security_payment,
                                           'prepayment': prepayment,
                                           'maintenance_costs': maintenance_costs,
                                           'floor': floor,
                                           'all_floors': all_floors,
                                           'region': region,
                                           'city': city,
                                           'city_area': city_area,
                                           'microdistrict': microdistrict,
                                           'undergrounds': undergrounds
                                           }
                logger.info(self.info_dict)
            else:
                logger.info(response_page.status_code)
                time.sleep(30)
                logger.info('Произошла ошибка, но работа будет продолжена через 30 сек.')

        return self.info_dict
