import time

from parsers.config import CIAN_URL, DOM_ClICK_URL
from export_to_db import create_table, check_db
from parsers.cian_parser import CIAN_pages, CIAN_ads
from parsers.dom_click_parser import DomClickPages, DomClickAds


def cian_parse(cian_url):
    url_list = CIAN_pages(cian_url, 3)
    cian_ads = CIAN_ads(url_list())
    return cian_ads()


def dom_click_parse(dom_click_url):
    while True:
        dom_click_ads = {}
        try:
            dom_click_pages = DomClickPages(dom_click_url)
            dom_click_pages.first_step_parse()
            dom_click_ads = DomClickAds(dom_click_pages.list_of_url).second_step_parse()
        except Exception as error:
            print(error)
            print('Произошла ошибка, но работа будет продолжена через 30 сек.')
            time.sleep(30)
        finally:
            return dom_click_ads


if __name__ == '__main__':
    create_table()
    cian_ads = cian_parse(CIAN_URL)
    check_db(cian_ads)
    # dom_click_ads = dom_click_parse(DOM_ClICK_URL)
    # check_db(dom_click_ads)
