from web_scrappers.AirlineWebScrapper import AirlineWebScrapper
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
from datetime import datetime
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from Flight import Flight
import traceback

class RyanairWebScrapper(AirlineWebScrapper):

    def __init__(self, min_departing_hour, min_returning_hour, max_price, num_weeks_to_analyse, proxies):
        self.URL = "https://www.ryanair.com/"
        super().__init__(self.URL, min_departing_hour, min_returning_hour, max_price, num_weeks_to_analyse, proxies)

    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        self.accept_cookies()
        #flight_origin = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="input-button__departure"]')))
        flight_destiny = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@id="input-button__destination"]')))
        time.sleep(1)
        flight_destiny.click()
        time.sleep(1)
        flight_destiny.send_keys(to_city)
        time.sleep(1)
        div_list_places = self.driver.find_elements(by='xpath', value='//fsw-airport-item[@class="ng-star-inserted"]')
        if len(div_list_places) > 1:
            div_list_places[1].click()
        else:
            print("Destination not available")
            return False, None
        dates_set = self.set_dates(departing_date, returning_date)
        if not dates_set:
            return False, None
        # Search flights
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Buscar"]'))).click()
        departing_flights, returning_flights = self.retrieve_all_flights(from_city, to_city, departing_date,
                                                                         returning_date)
        departing_flights = self.filter_flights_by_departing_hour(departing_flights)
        returning_flights = self.filter_flights_by_returning_hour(returning_flights)
        round_flight = self.find_cheapest_flights(departing_flights, returning_flights)
        print("Successful scrapping")
        return self.check_round_flights_under_max_price(round_flight), round_flight

    def set_dates(self, departing_date, returning_date, analysed_months=0, pending="departing"):
        # Find how many months could we need to analyse
        max_num_months_to_analyse = self.num_weeks_to_analyse / 4
        if analysed_months > max_num_months_to_analyse:
            return False
        departing_date_ryaniar_format = datetime.strptime(departing_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        returning_date_ryaniar_format = datetime.strptime(returning_date, '%d/%m/%Y').strftime('%Y-%m-%d')
        element_departing_date_to_select = "//div[@data-id='" + departing_date_ryaniar_format + "']"
        element_returning_date_to_select = "//div[@data-id='" + returning_date_ryaniar_format + "']"
        time.sleep(1.2)
        try:
            if pending == "departing":
                flight_departing_date = self.driver.find_element(by='xpath', value=element_departing_date_to_select)
                time.sleep(1.24)
                if "calendar-body__cell--disabled" in flight_departing_date.get_attribute("class"):
                    print("Fechas no disponibles")
                    return False
                flight_departing_date.click()
        except Exception:
            print("Dates could not be found in the displayed calendar")
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-ref="calendar-btn-next-month"]'))).click()
            analysed_months = analysed_months + 1
            return self.set_dates(departing_date, returning_date, analysed_months)
        time.sleep(1.35)
        try:
            flight_returning_date = self.driver.find_element(by='xpath', value=element_returning_date_to_select)
        except Exception:
            print("Dates could not be found in the displayed calendar")
            WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-ref="calendar-btn-next-month"]'))).click()
            analysed_months = analysed_months + 1
            return self.set_dates(departing_date, returning_date, analysed_months, pending="returning")
        time.sleep(1.332)
        if "calendar-body__cell--disabled" in flight_returning_date.get_attribute("class"):
            print("Fechas no disponibles")
            return False
        flight_returning_date.click()
        return True

    def retrieve_all_flights(self, from_city, to_city, departing_date, returning_date):
        print("Retrieving flights from ryanair.com...")
        WebDriverWait(self.driver, 35).until(EC.presence_of_element_located((By.XPATH, '//button[normalize-space()="Seleccionar"]')))
        time.sleep(5)
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
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@data-ref="cookie.no-thanks"]'))).click()
