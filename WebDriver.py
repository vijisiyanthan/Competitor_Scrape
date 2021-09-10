import re
import selenium
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

URL_REGEX = r'(https?:\/\/)?([\w\-])+\.{1}([a-zA-Z]{2,63})([\/\w-]*)*\/?\??([^#\n\r]*)?#?([^\n\r]*)'


class ProductInformation:
    information = {}

    def __init__(self):
        self.information['Product SKU'] = ""
        self.information['Product Name'] = ""
        self.information['Price'] = ""
        self.information['Strike Through Price'] = ""
        self.information['Add To Cart Option'] = ""
        self.information['Free Delivery Option'] = ""
        self.information['Contact For Price Option'] = ""
        self.information['Page Link'] = ""


class NellaOnlineProductPage:
    product_information = {}

    def __init__(self):
        self.PATH = "C:/Users/sviji/Downloads/chromedriver.exe"
        # self.options = webdriver.ChromeOptions()
        # self.options.add_argument(argument='--headless')
        # self.options.add_argument(argument='log-level=3')
        self.driver = webdriver.Chrome(self.PATH)
        self.wait = WebDriverWait(self.driver, 5)

    def scrape(self, path):
        try:
            self.driver.get(path)
        except:
            self.driver.quit()
        pass


class NellaOnlineCollectionsPage:

    def __init__(self):
        self.PATH = "C:/Users/sviji/Downloads/chromedriver.exe"
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument(argument='--headless')
        # self.options.add_argument(argument='log-level=3')
        self.driver = webdriver.Chrome(self.PATH)
        self.wait = WebDriverWait(self.driver, 5)

        self.page_links = set()
        self.df_products = pd.DataFrame()

    def get_product_sku(self):
        self.df_products['Product SKU'] = self.df_products.apply(lambda row: self.scrape_product_sku(row['Page Link']),
                                                                 axis=1)

    def scrape_product_sku(self, url):
        try:
            self.driver.get(f"https://www.nellaonline.com/{url}")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME,"table")))
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            table_rows = soup.find_all("tr")
            for row in table_rows:
                columns = row.find_all("td")
                if len(columns) != 0:
                    if columns[0].text == "Model":
                        return columns[1].text
                else:
                    pass
        except:
            pass

    def get_product_links(self):
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find("div", {"class": "product_c"})
        links = div.find_all("a", href=True)
        product_divs = div.find_all("div", {"class": "main_box"})
        collections_pages_links = set()
        for div in product_divs:
            product = ProductInformation()
            product.information['Product Name'] = (div.find("div", {"id": "desc-hide"})).find("a", href=True).text
            product.information['Page Link'] = (div.find("div", {"id": "desc-hide"})).find("a", href=True)['href']
            product.information['Price'] = "" if div.find("div", {"class": "price"}) is None else (div.find("div", {
                "class": "price"}).text).split("CAD$")[1]
            product.information['Add To Cart Option'] = "N" if div.find("div", {"style": "font-size:1.32em;line-height"
                                                                                         ":1;"}) is None else "Y"
            product.information['Strike Through Price'] = "" if div.find("span", {"id": "comparePrice"}) is None else \
                div.find("span", {"id": "comparePrice"}).text.split("$")[1]
            product.information['Free Delivery Option'] = "N" if div.find("span", {
                "style": "color: #fff;padding: 0 5px;transform: skewX(10deg) skewY(0);display: block;font-size: 12px;"}) is None else "Y"
            product.information['Contact For Price Option'] = div.find_all(
                lambda tag: tag.text == "Contact Us For Pricing")
            product.information['Contact For Price Option'] = "N" if len(
                product.information['Contact For Price Option']) == 0 else "Y"
            self.df_products = self.df_products.append(product.information, ignore_index=True)

        # for a in links:
        #     if re.match(URL_REGEX, a['href']):
        #         collections_pages_links.add(a['href'])
        #     else:
        #         if len(a['href'].split("/products")) != 1:
        #             self.page_links.add(a['href'])
        #
        # if len(collections_pages_links) != 0:
        #     for link in collections_pages_links:
        #         if collection_main_page:
        #             collection_name = link.split("https://www.nellaonline.com/collections/")[1]
        #             self.scrape(collection_name=collection_name, collection_main_page=False)

    def scrape(self, collection_name, collection_main_page=True):
        try:
            page = 1
            while True:
                self.driver.get(f"https://www.nellaonline.com/collections/{collection_name}?page={page}")
                soup = BeautifulSoup(self.driver.page_source, 'html.parser')
                if len(soup.find_all("div", {"class": "main_box"})) > 0:
                    self.get_product_links()
                    page += 1
                else:
                    break
            self.get_product_sku()
        except:
            self.driver.quit()

        self.driver.quit()
