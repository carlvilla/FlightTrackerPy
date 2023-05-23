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
from RoundFlight import RoundFlight

import calendar
import locale
locale.setlocale(locale.LC_TIME, "es_ES")

class SkyscannerWebScrapper(AirlineWebScrapper):

    def __init__(self, min_departing_hour, min_returning_hour, max_price, proxies):
        self.URL = "https://www.skyscanner.es"
        super().__init__(self.URL, min_departing_hour, min_returning_hour, max_price, proxies)

    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        time.sleep(4.24)
        self.accept_cookies()
        flight_destiny = self.driver.find_element(by='xpath', value='//input[@id="destinationInput-input"]')
        time.sleep(4.324)
        flight_destiny.click()
        time.sleep(3.2)
        flight_destiny.send_keys(to_city)
        time.sleep(4.56)
        flight_destiny.send_keys(Keys.ENTER)
        time.sleep(5.743)
        _departing_date = datetime.strptime(departing_date, '%d/%m/%Y')
        _returning_date = datetime.strptime(returning_date, '%d/%m/%Y')
        departing_weekday = calendar.day_name[_departing_date.weekday()]
        returning_weekday = calendar.day_name[_returning_date.weekday()]
        departing_day = _departing_date.day
        returning_day = _returning_date.day
        departing_month = calendar.month_name[_departing_date.month]
        returning_month = calendar.month_name[_returning_date.month]
        departing_year = _departing_date.year
        returning_year = _returning_date.year
        departing_date_skyscanner_format = departing_weekday + ", " + str(departing_day) + " de " + departing_month + " de " + str(departing_year) + ". Seleccionar como fecha de salida"
        returning_date_skyscanner_format = returning_weekday + ", " + str(returning_day) + " de " + returning_month + " de " + str(returning_year) + ". Seleccionar como fecha de vuelta"
        flight_departing_date = self.driver.find_element(by='xpath', value='//button[@aria-label="'+departing_date_skyscanner_format+'"]')
        flight_departing_date.click()
        time.sleep(3.632)
        flight_returning_date = self.driver.find_element(by='xpath', value='//button[@aria-label="'+returning_date_skyscanner_format+'"]')
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
        time.sleep(1.53)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.53)
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.53)
        flights = self.retrieve_all_flights(from_city, to_city, departing_date,
                                                                         returning_date)
        flights = self.filter_round_flights_by_hours(flights)
        cheapest_flight = self.find_cheapest_round_flight(flights)
        print("Successful scrapping")
        self.close_scrapper()
        return self.check_round_flights_under_max_price(cheapest_flight), cheapest_flight

    def retrieve_all_flights(self, from_city, to_city, departing_date, returning_date):
        print("Retrieving flights from skyscanner.es...")
        time.sleep(10.537)
        flight_page_source = self.driver.page_source
        soup = BeautifulSoup(flight_page_source, 'lxml')
        flight_lists = soup.find_all("div", {"class": "FlightsTicket_container__NWJkY"})
        flights = []
        for div_flight in flight_lists:
            hours = div_flight.find_all('span', {'class': 'BpkText_bpk-text__MWZkY BpkText_bpk-text--subheading__NzkwO'})
            departing_hour = hours[0].text
            returning_hour = hours[2].text
            price = div_flight.find('span', {'class': 'BpkText_bpk-text__MWZkY BpkText_bpk-text--lg__NjNhN'}).text
            durations = div_flight.find_all('span',
                            {'class': 'BpkText_bpk-text__MWZkY BpkText_bpk-text--xs__ZDJmY Duration_duration__NmUyM'})
            departing_duration = durations[0].text
            returning_duration = durations[1].text
            departing_flight = Flight(from_city, to_city, departing_date, departing_hour, departing_duration, "0")
            returning_flight = Flight(to_city, from_city, departing_date, returning_hour, returning_duration, "0")
            flight = RoundFlight(departing_flight, returning_flight, self.URL, price)
            flights.append(flight)
        return flights

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
