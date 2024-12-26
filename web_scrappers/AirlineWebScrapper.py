import os
import pickle
import subprocess
import time
from abc import (ABC, abstractmethod)

from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
import undetected_chromedriver as uc
from datetime import datetime
import random
import urllib
from selenium.webdriver.firefox.options import Options

from RoundFlight import RoundFlight

#agents = ["Firefox/66.0.3", "Chrome/73.0.3683.68", "Edge/16.16299"]
#agents = ["Mozilla/5.0 (Windows NT 4.0; WOW64)", "AppleWebKit/537.36", "Chrome/37.0.2049.0", "Safari/537.36"]

agents = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'



class AirlineWebScrapper(ABC):

    def __init__(self, URL, min_departing_hour, min_returning_hour, max_price, num_weeks_to_analyse, proxies):
        self.proxies = proxies
        self.driver = self.setting_up_selenium()
        self.min_departing_hour = datetime.strptime(min_departing_hour, '%H:%M').time()
        self.min_returning_hour = datetime.strptime(min_returning_hour, '%H:%M').time()
        self.url = URL
        self.max_price = max_price
        self.num_weeks_to_analyse = num_weeks_to_analyse

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

    def filter_round_flights_by_hours(self, flights):
        flights_without_none_type = filter(None, flights)
        return list(
            filter(lambda flight: flight.get_departing_hour() > self.min_departing_hour and flight.get_returning_hour() > self.min_returning_hour, flights_without_none_type))

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

    def find_cheapest_flights(self, departing_flights, returning_flights):
        if departing_flights is not None and len(departing_flights) > 0 and returning_flights is not None and len(returning_flights) > 0:
            cheapest_departing_flight = min(departing_flights, key=lambda flight: flight.get_price())
            cheapest_returning_flight = min(returning_flights, key=lambda flight: flight.get_price())
            round_flight = RoundFlight(cheapest_departing_flight, cheapest_returning_flight, self.URL)
            return round_flight

    def find_cheapest_round_flight(self, round_flights):
        if round_flights is not None and len(round_flights) > 0:
            cheapest_flight = min(round_flights, key=lambda flight: flight.get_total_price())
            return cheapest_flight

    def setting_up_selenium(self):
        try:
            print("Setting up Selenium driver...")

            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"

            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument(f'user-agent={user_agent}')
            options.add_argument("--window-size=1920,1080")
            #options.add_argument('--ignore-certificate-errors')
            #options.add_argument('--allow-running-insecure-content')
            #options.add_argument("--disable-extensions")
            #options.add_argument("--proxy-server='direct://'")
            #options.add_argument("--proxy-bypass-list=*")
            #options.add_argument("--start-maximized")
            options.add_argument('--disable-gpu')
            #options.add_argument('--disable-dev-shm-usage')
            #options.add_argument('--no-sandbox')
            driver = webdriver.Chrome(options=options)

            # driver = webdriver.Firefox()

            #chromedriver_autoinstaller.install()
            # Create Chromeoptions instance
            #options = webdriver.ChromeOptions()


            # Adding argument to disable the AutomationControlled flag

            #options.add_experimental_option("excludeSwitches", ["enable-automation"])
            #options.add_experimental_option('excludeSwitches', ['enable-logging'])
            # Turn-off userAutomationExtension
            #options.add_experimental_option("useAutomationExtension", False)
            # Setting incognito mode
            #options.add_argument("--incognito")




            # Set browser’s user agent
            #options.add_argument(' - user-agent=' + random.choice(agents) + '"')

            #options.add_argument(f'--user-agent={agents}')
            #options.add_argument("start-maximized")
            #options.add_argument('--disable-gpu')

            #options.add_argument("--headless")  # Remove this if you want to see the browser (Headless makes the chromedriver not have a GUI)
            #options.add_argument("--window-size=1920,1080")
            #options.add_argument('--no-sandbox')
            #options.add_argument("--disable-extensions")

            #proxy = self.get_proxy()
            #options.add_argument('--proxy-server=%s' % proxy.http_proxy)


            #driver = webdriver.Chrome(options=options)




            #driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")



            #driver.get('https://httpbin.org/ip')
            #dict = ast.literal_eval(re.search('({.+})', driver.find_element(By.TAG_NAME, "body").text).group(0))
            #obtained_ip = dict["origin"]
            #if obtained_ip != proxy.ip:
            #    print("The obtained IP is not from the proxy...")
            #    return self.setting_up_selenium()
            #driver.close()

            #options = uc.ChromeOptions()
            #ua = UserAgent()
            #options.add_argument(f'user-agent={ua.random}')
            #options.add_argument("--disable-blink-features=AutomationControlled")
            #options.add_experimental_option("excludeSwitches", ["enable-automation"])
            #options.add_experimental_option('useAutomationExtension', False)
            #options.add_argument("start-maximized")
            #options.headless = True
            #options.add_argument('--headless')
            #driver = uc.Chrome(options=options)
            #driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
            #driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

            #os.system("""osascript -e 'tell app "Tor Browser" to open'""")
            #time.sleep(20)
            #tor_binary_path_driver = '/Applications/Tor\ Browser.app/Contents/MacOS/firefox'
            #geckodriver_path = '../drivers/geckodriver'

            #os.popen(tor_binary_path_driver)
            #options = Options()
            #options.headless = True

            #firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
            #firefox_capabilities['proxy'] = {
            #    "proxyType": "MANUAL",
            #    'socksProxy': '127.0.0.1:9150',
            #    "socksVersion": 5
            #}

            

            return driver
        except Exception as e:
            print(e)
            print("An error occurred while setting the Selenium driver...")
            #subprocess.call(['osascript', '-e', 'tell application "Tor Browser" to quit'])
            #return self.setting_up_selenium()

    def safe_cookies(self, driver):
        print("Saving cookies...")
        pickle_filename = "cookies.pkl"
        pickle.dump(driver.get_cookies(), open(pickle_filename, "wb"))

    def get_proxy(self):
        prox = Proxy()
        try:
            # Select a random proxy
            idx_proxy = random.randint(0, len(self.proxies))
            proxy_data = self.proxies[idx_proxy]

            print(proxy_data)

            proxy_ip = proxy_data['IP Address']
            proxy_port = proxy_data['Port']
            proxy_country = proxy_data['Country']
            prox.ip = proxy_ip
            prox.proxy_type = ProxyType.MANUAL
            prox.http_proxy = proxy_ip + ":" + proxy_port
            print("Trying to connect with proxy", proxy_ip, "from", proxy_country)
            proxy_handler = urllib.request.ProxyHandler({'https': proxy_ip + ":" + proxy_port})
            opener = urllib.request.build_opener(proxy_handler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            req = urllib.request.Request('http://www.example.com')
            urllib.request.urlopen(req)
            print("Proxy seems to be working!")
        except Exception:
            print("Connection error! (Trying another proxy)")
            return self.get_proxy()
        return prox

        
