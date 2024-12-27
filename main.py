import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from web_scrappers.IberiaWebScrapper import IberiaWebScrapper
from web_scrappers.IberiaExpressWebScrapper import IberiaExpressWebScrapper
from web_scrappers.SkyscannerWebScrapper import SkyscannerWebScrapper
from web_scrappers.RyanairWebScrapper import RyanairWebScrapper
import json
from flights.scraper import get_next_weekends, scrape_flights


def main():
    settings = load_settings()
    # Retrieve user settings
    num_weeks_to_analyse = settings["num_weeks_to_analyse"]
    origins = settings["origins"]
    destinations = settings["destinations"]
    # Get dates next weekends
    weekends = get_next_weekends(num_weeks_to_analyse)
    while(True):
        proxies = []
        #proxies = get_free_proxies()
        print("Number of proxies found:", len(proxies))
        for weekend in weekends:
            for from_city in origins:
                for idx, to_city in enumerate(destinations):
                    print("Checking flights from " + from_city + " to " + to_city + " [" + weekend[0] + " to "
                        + weekend[1] + "] - Destination " + str(idx + 1) + "/" + str(len(destinations)))
                    scrape_flights(from_city, to_city, weekend, settings, proxies)
        time.sleep(7200)

# Function to load user settings
def load_settings(filepath='settings.json'):
    try:
        with open(filepath, 'r') as file:
            settings = json.load(file)
    except FileNotFoundError:
        settings = {}  # Return an empty dict if the file does not exist
    return settings

def get_free_proxies():
    print("Retrieving proxies...")
    driver = uc.Chrome()
    driver.get('https://sslproxies.org')
    table = driver.find_element(By.TAG_NAME, 'table')
    thead = table.find_element(By.TAG_NAME, 'thead').find_elements(By.TAG_NAME, 'th')
    tbody = table.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
    headers = []
    for th in thead:
        headers.append(th.text.strip())
    proxies = []
    for tr in tbody:
        proxy_data = {}
        tds = tr.find_elements(By.TAG_NAME, 'td')
        for i in range(len(headers)):
            proxy_data[headers[i]] = tds[i].text.strip()
        proxies.append(proxy_data)
    driver.quit()
    print("Proxies retrieved!")
    return proxies

if __name__ == '__main__':
    main()
