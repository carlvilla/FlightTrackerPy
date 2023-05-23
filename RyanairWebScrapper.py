from AirlineWebScrapper import AirlineWebScrapper
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from datetime import datetime
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from Flight import Flight

class RyanairWebScrapper(AirlineWebScrapper):

    def __init__(self, min_departing_hour, min_returning_hour, max_price, proxies):
        self.URL = "https://www.ryanair.com/"
        super().__init__(self.URL, min_departing_hour, min_returning_hour, max_price, proxies)

    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        time.sleep(1.21)
        self.accept_cookies()
        flight_origin = self.driver.find_element(by='xpath', value='//input[@id="input-button__departure"]')
        flight_destiny = self.driver.find_element(by='xpath', value='//input[@id="input-button__destination"]')
        time.sleep(1.324)
        flight_destiny.send_keys(to_city)
        time.sleep(1.3)
        div_list_places = self.driver.find_elements(by='xpath', value='//fsw-airport-item[@class="ng-star-inserted"]')
        time.sleep(1.321)
        if len(div_list_places) > 1:
            div_list_places[1].click()
        else:
            print("Destination not available")
            self.close_scrapper()
            return False, None
        time.sleep(1.543)
        departing_date_ryaniar_format = datetime.strptime(departing_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        returning_date_ryaniar_format = datetime.strptime(returning_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        element_departing_date_to_select = "div[data-id='" + departing_date_ryaniar_format + "']"
        element_returning_date_to_select = "div[data-id='" + returning_date_ryaniar_format + "']"
        flight_departing_date = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, element_departing_date_to_select)))
        flight_departing_date.click()
        time.sleep(1.632)
        flight_returning_date = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.CSS_SELECTOR, element_returning_date_to_select)))
        flight_returning_date.click()
        time.sleep(1.732)
        # Search flights
        WebDriverWait(self.driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Buscar"]'))).click()
        departing_flights, returning_flights = self.retrieve_all_flights(from_city, to_city, departing_date,
                                                                         returning_date)
        departing_flights = self.filter_flights_by_departing_hour(departing_flights)
        returning_flights = self.filter_flights_by_returning_hour(returning_flights)
        round_flight = self.find_cheapest_flights(departing_flights, returning_flights)
        print("Successful scrapping")
        self.close_scrapper()
        return self.check_round_flights_under_max_price(round_flight), round_flight

    def retrieve_all_flights(self, from_city, to_city, departing_date, returning_date):
        print("Retrieving flights from ryanair.com...")
        WebDriverWait(self.driver, 40).until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="Seleccionar"]')))
        flight_page_source = self.driver.page_source
        soup = BeautifulSoup(flight_page_source, 'lxml')
        flight_lists = soup.find_all('flight-list')
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

    def accept_cookies(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="cookie-popup-with-overlay__button"]'))).click()
