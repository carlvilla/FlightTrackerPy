import traceback
import time
import datetime
import importlib
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from EmailSender import EmailSender
from web_scrappers.IberiaWebScrapper import IberiaWebScrapper
from web_scrappers.IberiaExpressWebScrapper import IberiaExpressWebScrapper
from web_scrappers.SkyscannerWebScrapper import SkyscannerWebScrapper
from web_scrappers.RyanairWebScrapper import RyanairWebScrapper
import json

def main():
    settings = load_settings()
    # Retrieve user settings
    num_weeks_to_analyse = settings["num_weeks_to_analyse"]
    destinations = settings["destinations"]
    # Get dates next weekends
    weekends = get_next_weekends(num_weeks_to_analyse)
    while(True):
        proxies = []
        #proxies = get_free_proxies()
        print("Number of proxies found:", len(proxies))
        for weekend in weekends:
            for idx, to_city in enumerate(destinations):
                print("Checking flights from " + settings["from_city"] + " to " + to_city + " [" + weekend[0] + " to "
                      + weekend[1] + "] - Destination " + str(idx + 1) + "/" + str(len(destinations)))
                scrape_flights(to_city, weekend, settings, proxies)
        time.sleep(7200)

# Function to load user settings
def load_settings(filepath='settings.json'):
    try:
        with open(filepath, 'r') as file:
            settings = json.load(file)
    except FileNotFoundError:
        settings = {}  # Return an empty dict if the file does not exist
    return settings

def scrape_flights(to_city, weekend, settings, proxies):
    email_sender = EmailSender(settings["email"])
    for websites_scrapper in settings["websites_scrappers"]:
        ScrapperClass = getattr(importlib.import_module("__main__"), websites_scrapper)
        web_scrapper = ScrapperClass(settings["min_departing_hour"], settings["min_returning_hour"], settings["max_price"], settings["num_weeks_to_analyse"], proxies)
        try:
            is_flight_interesting, round_flight = web_scrapper.scrape(settings["from_city"], to_city, weekend[0], weekend[1])
            if is_flight_interesting:
                print("An interesting flight was found!")
                print(round_flight)
                email_sender.send_flight(round_flight)
            else:
                # Check flight in next website
                # Check next weekend
                print("No interesting flights found")
        except Exception as e:
            print(traceback.format_exc())
        web_scrapper.close_scrapper()

def get_next_friday():
    today = datetime.date.today()
    friday = today + datetime.timedelta((3-today.weekday())%7+1)
    return friday

def get_next_sunday():
    today = datetime.date.today()
    sunday = today + datetime.timedelta((5-today.weekday())%7+1)
    return sunday

def get_next_weekends( num_weeks_to_analyse):
    weekends = []
    today = datetime.date.today()
    # It it is currently a weekend, start with the following
    if today.weekday() >= 4:
        today = today + datetime.timedelta(3)
    friday = today + datetime.timedelta((3 - today.weekday()) % 7 + 1)
    sunday = today + datetime.timedelta((5 - today.weekday()) % 7 + 1)
    weekends.append((friday.strftime('%d/%m/%Y'), sunday.strftime('%d/%m/%Y')))
    for idx_week in range(1, num_weeks_to_analyse):
        next_friday = friday + datetime.timedelta(7 * idx_week)
        next_sunday = sunday + datetime.timedelta(7 * idx_week)
        weekends.append((next_friday.strftime('%d/%m/%Y'), next_sunday.strftime('%d/%m/%Y')))
    return weekends

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
