from abc import (ABC, abstractmethod)

from selenium import webdriver
import undetected_chromedriver as uc
from proxybroker import Broker
import asyncio
from datetime import datetime

from RoundFlight import RoundFlight

class AirlineWebScrapper(ABC):

    def __init__(self, URL, min_departing_hour, min_returning_hour, max_price):
        self.driver = self.setting_up_selenium()
        self.min_departing_hour = datetime.strptime(min_departing_hour, '%H:%M').time()
        self.min_returning_hour = datetime.strptime(min_returning_hour, '%H:%M').time()
        self.url = URL
        self.max_price = max_price

    def scrape(self, from_city="Madrid (MAD)", to_city="Nueva York (NYC)", departing_date="26/05/2023",
               returning_date="28/05/2023"):

        proxies = asyncio.Queue()
        broker = Broker(proxies)
        tasks = asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], limit=5), save(proxies, filename='proxies.txt'))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(tasks)


        self.driver.get(self.url)
        return self.scrape_airline(from_city, to_city, departing_date, returning_date)

    def get_random_proxy():
        """
        Get random proxy from 'proxies.txt'.
        """
        lines = open('proxies.txt').read().splitlines()
        rproxy = random.choice(lines)
        PROXY = rproxy

    async def save(proxies, filename):
        """
        Save proxies to a file.
        """
        with open(filename, 'w') as file:
            while True:
                proxy = await proxies.get()
                if proxy is None:
                    break
                # Check accurately if the proxy is working.
                if proxy.is_working:
                    protocol = 'https' if 'HTTPS' in proxy.types else 'http'
                    line = '{protocol}://{proxy.host}:{proxy.port}\n'
                    file.write(line)

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
        driver = uc.Chrome()
        # Setting user agent iteratively as Chrome 108 and 107
        # driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": useragentarray[1]})
        # Changing the property of the navigator value for webdriver to undefined
        # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return driver
