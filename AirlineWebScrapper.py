from abc import (ABC, abstractmethod)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import Proxy, ProxyType
import undetected_chromedriver as uc
from datetime import datetime
import random

from RoundFlight import RoundFlight

class AirlineWebScrapper(ABC):

    def __init__(self, URL, min_departing_hour, min_returning_hour, max_price, proxies):
        self.proxies = proxies
        self.driver = self.setting_up_selenium()
        self.min_departing_hour = datetime.strptime(min_departing_hour, '%H:%M').time()
        self.min_returning_hour = datetime.strptime(min_returning_hour, '%H:%M').time()
        self.url = URL
        self.max_price = max_price

    def scrape(self, from_city="Madrid (MAD)", to_city="Nueva York (NYC)", departing_date="26/05/2023",
               returning_date="28/05/2023"):
        self.driver.get(self.url)
        return self.scrape_airline(from_city, to_city, departing_date, returning_date)

    @abstractmethod
    def scrape_airline(self,from_city, to_city, departing_date, returning_date):
        pass

    def close_scrapper(self):
        self.driver.quit()

    def extract_weekends_next_months(self, num_months=2):
        print("Extracting the weekends (Friday to Sunday) for the next", num_months, "months")

    def filter_flights_by_departing_hour(self, flights):
        flights_without_none_type = filter(None, flights)
        return list(
            filter(lambda flight: flight.get_departing_hour() > self.min_departing_hour, flights_without_none_type))

    def filter_flights_by_returning_hour(self, flights):
        flights_without_none_type = filter(None, flights)
        return list(
            filter(lambda flight: flight.get_departing_hour() > self.min_returning_hour, flights_without_none_type))

    def check_round_flights_under_max_price(self, round_flight):
        if round_flight is not None:
            return round_flight.get_total_price() < self.max_price
        return False

    def find_cheapest_round_flight(self, departing_flights, returning_flights):
        if departing_flights is not None and len(departing_flights) > 0 and returning_flights is not None and len(returning_flights) > 0:
            cheapest_departing_flight = min(departing_flights, key=lambda flight: flight.get_price())
            cheapest_returning_flight = min(returning_flights, key=lambda flight: flight.get_price())
            round_flight = RoundFlight(cheapest_departing_flight, cheapest_returning_flight)
            return round_flight

    def setting_up_selenium(self):
        # chromedriver_autoinstaller.install()
        # Create Chromeoptions instance
        options = webdriver.ChromeOptions()
        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # Turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)
        # Setting incognito mode
        options.add_argument("--incognito")
        # Setting the driver path and requesting a page
        # driver = webdriver.Chrome(options=options)
        # driver = webdriver.Chrome('/Users/carlosvillablanco/Downloads/chromedriver/chromedriver', options=options)

        # Setting user agent iteratively as Chrome 108 and 107
        # driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": useragentarray[1]})
        # Changing the property of the navigator value for webdriver to undefined
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Obtain proxy
        proxy = self.get_proxy()
        capabilities = webdriver.DesiredCapabilities.CHROME
        proxy.add_to_capabilities(capabilities)
        driver = uc.Chrome(desired_capabilities=capabilities)


        return driver

    def get_proxy(self):
        try:
            # Select a random proxy
            idx_proxy = random.randint(0, len(self.proxies))
            proxy_data = self.proxies[idx_proxy]
            proxy_ip = proxy_data['IP Address']
            proxy_port = proxy_data['Port']
            proxy_country = proxy_data['Country']
            prox = Proxy()
            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = proxy_ip + ":" + proxy_port
            #prox.socks_proxy = proxy_ip + ":" + proxy_port
            prox.ssl_proxy = proxy_ip + ":" + proxy_port
            print("Trying to connect with proxy", proxy_ip, "from", proxy_country)


            urllib.urlopen(
                proxy_ip,
                proxies={'http': proxy_ip}
            )
            return prox
        except IOError:
            print
            "Connection error! (Trying proxy)"
            return self.get_proxy

        