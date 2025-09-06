from selenium.webdriver.common.by import By
from seleniumbase import SB
import re
import time

from logger import logger
from .dadata_func import get_address_info


class DomClickPages:
    """
    Класс для сбора url-ов объявлений
    в рамках выбранного количества страниц
    на сайте Домклик
    """
    def __init__(self, url, num_of_pages: int = 3, debug_mode: int = 1):
        self.url = url
        self.num_of_pages = num_of_pages
        self.debug_mode = debug_mode
        self.list_of_url = []

    def parse_urls(self):
        for page in range(self.num_of_pages):
            self.driver.open(self.url + str(20 * page))
            if "Доступ ограничен" in self.driver.get_title():
                time.sleep(10)
                raise Exception("Блокировка IP")
            try:
                elems = self.driver.find_elements(By.CLASS_NAME, 'a4tiB2')
                for elem in elems:
                    href = elem.get_attribute('href')
                    self.list_of_url.append(href)
            except Exception as e:
                logger.error(str(e))

    def first_step_parse(self):
        with SB(uc=True,
                headed=True if self.debug_mode else False,
                headless=True if not self.debug_mode else False,
                page_load_strategy="eager",
                block_images=True,
                ) as self.driver:
            try:
                self.parse_urls()
            except Exception as e:
                logger.error(str(e))


class DomClickAds:
    """
    Класс для сбора данных по каждому объявлению
    на сайте Домклик
    """
    def __init__(self, list_of_url, debug_mode: int = 1):
        self.list_of_url = list_of_url[:50]
        self.debug_mode = debug_mode
        self.info_dict = {}

    def ads_parser(self):
        unik_id = 0
        for ad_url in self.list_of_url:
            unik_id += 1
            source = 'Домклик'
            self.driver.open(ad_url)
            if "Доступ ограничен" in self.driver.get_title():
                time.sleep(10)
                raise Exception("Блокировка IP в ad")

            try:
                regex = r'(\d+)'
                ad_id = int(re.search(regex, ad_url).group(1))

                name_elem = self.driver.find_element(By.TAG_NAME, 'h1')
                name = name_elem.text

                if 'торг' in name.lower():
                    type = 'Торговая площадь'
                elif 'офис' in name.lower():
                    type = 'Офис'
                elif 'своб' in name.lower() and 'назн' in name.lower():
                    type = 'Свободного назначения'
                else:
                    type = 'not_defined'

                price_elem = self.driver.find_elements(By.CLASS_NAME, 'l2ytJ')
                price = price_elem[1].text
                price = price.replace(' ', '')
                price = price.replace('₽/мес.', '')
                price = float(price.replace(',', '.').strip())

                try:
                    extra_elems = self.driver.find_elements(By.CLASS_NAME, '_cGv6')
                    regex = r'^(Налогообложение\n )(.+)'
                    tax = [re.search(regex, tax_elem.text) for tax_elem in extra_elems
                           if re.search(regex, tax_elem.text) is not None][0].group(2)
                except Exception:
                    tax = 'not_found'
                comission = 'not_found'

                try:
                    extra_elems = self.driver.find_elements(By.CLASS_NAME, '_cGv6')
                    regex = r'^(Коммунальные платежи\n )(.+)'
                    utility_payments = [re.search(regex, utility_payments_elem.text) for utility_payments_elem in extra_elems
                                        if re.search(regex, utility_payments_elem.text) is not None][0].group(2)
                    utility_payments = utility_payments.lower()
                except Exception:
                    utility_payments = 'not_found'

                security_payments = 'not_found'
                prepayment = 'not_found'
                maintenance_costs = 'not_found'

                square_floor_elem = self.driver.find_elements(By.CLASS_NAME, 'adkhV')
                square = square_floor_elem[0].text
                square = square.replace(' м²', '')
                square = float(square.replace(',', '.').strip())

                if len(square_floor_elem[1].text.split(' из ')) == 2:
                    floors = square_floor_elem[1].text.split(' из ')
                    floor = floors[0]
                    all_floors = floors[1]
                elif int(square_floor_elem[1].text) <= 36:
                    floor = square_floor_elem[1].text
                    all_floors = 'not_found'
                else:
                    floor = 'not_found'
                    all_floors = 'not_found'

                address_elems = self.driver.find_elements(By.CLASS_NAME, 'nTNXE')
                address = ', '.join([address.text for address in address_elems])
                full_address_data = get_address_info(address)
                region = full_address_data["region"]
                city = full_address_data["city"]
                city_area = full_address_data["city_area"]
                microdistrict = full_address_data["microdistrict"]

                underground_elems = self.driver.find_elements(By.CLASS_NAME, 'LpfGS')
                regex = r"^(.*?)(?=\n)"
                undergrounds = ', '.join([re.search(regex, underground.text).group(1)
                                          for underground in underground_elems])
                if not undergrounds:
                    undergrounds = 'not_found'

                self.info_dict[unik_id] = {'ads_id': ad_id,
                                           'source': source,
                                           'building_type': type,
                                           'square': square,
                                           'price': price,
                                           'tax': tax,
                                           'comission': comission,
                                           'utility_payments': utility_payments,
                                           'security_payments': security_payments,
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
            except Exception as e:
                logger.error(str(e))

    def second_step_parse(self):
        with SB(uc=True,
                headed=True if self.debug_mode else False,
                headless=True if not self.debug_mode else False,
                page_load_strategy="eager",
                block_images=True,
                ) as self.driver:
            try:
                self.ads_parser()
                return self.info_dict
            except Exception as e:
                logger.error(str(e))
