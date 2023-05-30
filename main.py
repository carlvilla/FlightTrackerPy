import traceback
import time
import datetime
import importlib
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from EmailSender import EmailSender
from IberiaWebScrapper import IberiaWebScrapper
from IberiaExpressWebScrapper import IberiaExpressWebScrapper
from RyanairWebScrapper import RyanairWebScrapper
from SkyscannerWebScrapper import SkyscannerWebScrapper

max_price = 120
from_city = "Madrid"
min_departing_hour = "16:00"
min_returning_hour = "18:00"
email = "carlosvillablanco@gmail.com"
email_sender = EmailSender(email)
num_weeks_to_analyse = 30
#destinations = ["Londres", "París", "Amsterdam", "Berlín", "Roma", "Praga", "Atenas", "Viena", "Dublín", "Leeds",
#                "Lyon", "Bratislava", "Reykjavik", "Vilna", "Budapest", "Estocolmo", "Varsovia", "Copenhague",
#                "Helsinki", "Bruselas", "Oslo", "Zurich", "Milán", "Múnich", "Estambul", "Skopje", "Frankfurt",
#                "Bucarest", "Toulouse", "Belgrado", "Sofía", "Oporto", "Marrakech", "Fez", "Ginebra", "Funchal",
 #               "Venecia", "Niza", "Bolonia", "Marsella", "Zagreb", "Dubrovnik", "Dubai", "Birmingham", "Burdeos",
  #              "Breslavia", "Stuttgart", "Bremen", "Bristol", "Catania", "Basilea", "Colonia", "Bastia", "Corfu",
  #              "Córcega", "Cerdeña", "Cork", "Cracovia", "Doha", "Dortmund", "Dresden", "Dusseldorf", "Edimburgo",
   #             "Eindhoven", "Faro", "Florencia", "Gdansk", "Glasgow", "Gotemburgo", "Hamburgo", "Hanóver", "Ibiza",
    #            "Jersey", "La Palma", "Lanzarote", "Nantes", "La Valeta", "Liubliana", "Luxemburgo", "Málaga", "Pisa",
     #           "Manchester", "Menorca", "Mikonos", "Nápoles", "Palma de Mallorca", "Turin", "Podgorica", "Reikiavik",
      #          "Riga", "Rotterdam", "Santorini", "Sarajevo", "Split", "Tallin", "Tánger", "Tenerife", "Tirana",
       #         "Turín", "Varna", "Verona", "Barcelona", "Casablanca", "Tunisia", "Tel Aviv", "Amman", "Beirut",
        #        "Cairo", "Kaunas", "Gran canaria", "Palma"]

# Destinations Ryanair
destinations = ["Roma", "Fuerteventura", "Gran canaria", "Ibiza", "Lanzarote", "Menorca", "Palma", "Santiago","Tenerife", "Berlin", "Amman", "Cracovia", "Varsovia", "Viena", "Faro", "Bruselas", "Kaunas","Birminghan", "Bristol", "Edimburgo", "Liverpool", "Londres", "Manchester", "Burdeos", "Marsella","Paris", "Luxembourg", "Prague", "Sofia", "Malta", "Bucarest", "Budapest", "Agadir", "Essaouira","Fez", "Marrakech", "Nador", "Rabat", "Tanger", "Tetouan", "Dublin", "Billund", "Copenhague","Alghero", "Bari", "Bolonia", "Brindisi", "Cagliari", "Catania", "Milan", "Napoles", "Palermo","Pisa", "Turin", "Venecia", "Eindhoven"]

#websites_scrappers = ["RyanairWebScrapper", "IberiaExpressWebScrapper", "SkyscannerWebScrapper", "IberiaWebScrapper"]
websites_scrappers = ["RyanairWebScrapper"]
def main():
    # Get dates next weekends
    weekends = get_next_weekends(num_weeks_to_analyse)
    while(True):
        proxies = []
        #proxies = get_free_proxies()
        print("Number of proxies found:", len(proxies))
        for weekend in weekends:
            for idx, to_city in enumerate(destinations):
                print("Checking flights from " + from_city + " to " + to_city + " [" + weekend[0] + " to "
                      + weekend[1] + "] - Destination " + str(idx + 1) + "/" + str(len(destinations)))
                scrape_flights(weekend, to_city, num_weeks_to_analyse, proxies)
        time.sleep(7200)

def scrape_flights(weekend, to_city, num_weeks_to_analyse, proxies):
    for websites_scrapper in websites_scrappers:
        ScrapperClass = getattr(importlib.import_module("__main__"), websites_scrapper)
        web_scrapper = ScrapperClass(min_departing_hour, min_returning_hour, max_price, num_weeks_to_analyse, proxies)
        try:
            is_flight_interesting, round_flight = web_scrapper.scrape(from_city, to_city, weekend[0], weekend[1])
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
            web_scrapper.driver.quit()
            #scrape_flights(weekend, to_city)

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
    friday = today + datetime.timedelta((3-today.weekday())%7+1)
    sunday = today + datetime.timedelta((5 - today.weekday()) % 7 + 1)
    #weekends.append((friday.strftime('%d/%m/%Y'), sunday.strftime('%d/%m/%Y')))
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