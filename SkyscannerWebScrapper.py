import re

from selenium.common import StaleElementReferenceException

from AirlineWebScrapper import AirlineWebScrapper
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from bs4 import BeautifulSoup
from datetime import datetime
import string

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from Flight import Flight


class SkyscannerWebScrapper(AirlineWebScrapper):

    def __init__(self, min_departing_hour, min_returning_hour, max_price):
        super().__init__("https://www.skyscanner.es", min_departing_hour, min_returning_hour, max_price)


    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        time.sleep(40)
        self.accept_cookies()
        flight_destiny = self.driver.find_element(by='xpath', value='//input[@id="destinationInput-input"]')
        time.sleep(4.324)
        flight_destiny.click()
        time.sleep(1.2)
        flight_destiny.send_keys(to_city)
        time.sleep(1.56)
        flight_destiny.send_keys(Keys.ENTER)
        time.sleep(5.743)

        departing_date_skyscanner_format = datetime.strptime(departing_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        returning_date_skyscanner_format = datetime.strptime(returning_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        element_departing_date_to_select = "//button[matches(@aria-label, '.*26.*mayo.*2023.*')]"
        element_returning_date_to_select = "//button[matches(@aria-label, '.*28.*mayo.*2023.*')]"

        flight_departing_date = self.driver.find_element(by='xpath', value='//button[@aria-label="viernes, 26 de mayo de 2023. Seleccionar como fecha de salida"]')
        flight_departing_date.click()
        time.sleep(3.632)
        flight_returning_date = self.driver.find_element(by='xpath', value='//button[@aria-label="domingo, 28 de mayo de 2023. Seleccionar como fecha de vuelta"]')
        flight_returning_date.click()
        time.sleep(3.732)


        # Search flights
        search_button = self.driver.find_element(by='xpath',value='//button[normalize-space()="Buscar"]')
        search_button.click()
        search_button.click()

        # Press "More results" button
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Más resultados"]'))).click()
        time.sleep(3.23)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2.53)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.53)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        departing_flights, returning_flights = self.retrieve_all_flights(from_city, to_city, departing_date,
                                                                         returning_date)
        departing_flights = self.filter_flights_by_departing_hour(departing_flights)
        returning_flights = self.filter_flights_by_returning_hour(returning_flights)
        round_flight = self.find_cheapest_round_flight(departing_flights, returning_flights)
        print("Successful scrapping")
        self.close_scrapper()
        return self.check_round_flights_under_max_price(round_flight), round_flight


    def retrieve_all_flights(self, from_city, to_city, departing_date, returning_date):
        print("Retrieving flights from skyscanner.es...")
        time.sleep(10.537)
        flight_page_source = self.driver.page_source
        soup = BeautifulSoup(flight_page_source, 'lxml')
        flight_lists = soup.find("div", {"class": "FlightsResults_dayViewItems__ZDFlO"})[1:-1]

        for div_flight in flight_lists:
            hour = div_flight.find('span', {'class': 'BpkText_bpk-text__MWZkY BpkText_bpk-text--subheading__NzkwO'}).text
            price = div_flight.find('span', {'class': 'BpkText_bpk-text__MWZkY BpkText_bpk-text--lg__NjNhN'}).text
            duration = div_flight.find('span', {'class': 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY Duration_duration__NmUyM'}).text

            print(hour)
            print(price)
            print(duration)

        time.sleep(223.732)


        flight_list_departing_flights = flight_lists[0]
        flight_list_returning_flights = flight_lists[1]
        flight_cards_departing_flights = flight_list_departing_flights.find_all('flight-card-new')
        departing_flights = []
        for flight_card in flight_cards_departing_flights:
            price = flight_card.find('flights-price-simple').text.translate({ord(c): None for c in string.whitespace})
            hour = flight_card.find("span", {"class": "flight-info__hour"}).text.translate({ord(c): None for c in string.whitespace})
            duration = flight_card.find("div", {"data-ref": "flight_duration"}).text.translate({ord(c): None for c in string.whitespace})
            flight = Flight(from_city, to_city, departing_date, hour, duration, price)
            departing_flights.append(flight)

        flight_cards_returning_flights = flight_list_returning_flights.find_all('flight-card-new')
        returning_flights = []
        for flight_card in flight_cards_returning_flights:
            price = flight_card.find('flights-price-simple').text.translate({ord(c): None for c in string.whitespace})
            hour = flight_card.find("span", {"class": "flight-info__hour"}).text.translate({ord(c): None for c in string.whitespace})
            duration = flight_card.find("div", {"data-ref": "flight_duration"}).text.translate({ord(c): None for c in string.whitespace})
            flight = Flight(from_city, to_city, returning_date, hour, duration, price)
            returning_flights.append(flight)

        return departing_flights, returning_flights

    def regex_to_be_present_in_element(self, locator, regexp):
        """ An expectation for checking if the given text is present in the
        specified element, extended to allow and return a regex match
        locator, text
        """
        def _predicate(driver):
            try:
                element_text = driver.find_element(*locator).text
                return re.search(regexp, element_text)
            except StaleElementReferenceException:
                return False

        return _predicate

    def accept_cookies(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="BpkButtonBase_bpk-button__NmRiZ UserPreferencesContent_buttons__YTQ4Y UserPreferencesContent_acceptButton__NjQxZ"]'))).click()
