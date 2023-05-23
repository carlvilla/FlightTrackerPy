from AirlineWebScrapper import AirlineWebScrapper
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from Flight import Flight

class IberiaWebScrapper(AirlineWebScrapper):

    def __init__(self, min_departing_hour, min_returning_hour, max_price, proxies):
        self.URL = "https://www.iberia.com/es"
        super().__init__(self.URL, min_departing_hour, min_returning_hour, max_price, proxies)

    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        # Wait on the webpage before trying anything
        time.sleep(1.5)
        self.accept_cookies()
        flight_origin = self.driver.find_element(by='xpath', value='//input[@name="flight_origin"]')
        flight_destiny = self.driver.find_element(by='xpath', value='//input[@name="flight_destiny"]')
        flight_hotel_round_date = self.driver.find_element(by='xpath', value='//input[@name="flight_hotel_round_date"]')
        flight_return_date = self.driver.find_element(by='xpath', value='//input[@name="flight_return_date"]')
        flight_origin.clear()
        flight_origin.send_keys(from_city)
        time.sleep(4.124)
        flight_origin.send_keys(Keys.ENTER)
        flight_destiny.send_keys(to_city)
        time.sleep(4.513)
        flight_destiny.send_keys(Keys.ENTER)
        flight_hotel_round_date.send_keys(departing_date)
        time.sleep(4.243)
        flight_return_date.send_keys(returning_date)
        time.sleep(3.632)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, 'buttonSubmit1'))).click()
        if self.was_bot_detected():
            return False, None
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.ID, 'originDestination-0')))
        time.sleep(1.134)
        departing_flights, returning_flights = self.retrieve_all_flights(from_city, to_city, departing_date, returning_date)
        departing_flights = self.filter_flights_by_departing_hour(departing_flights)
        returning_flights = self.filter_flights_by_returning_hour(returning_flights)
        round_flight = self.find_cheapest_flights(departing_flights, returning_flights)
        print("Successful scrapping")
        self.close_scrapper()

        return self.check_round_flights_under_max_price(round_flight), round_flight

    def was_bot_detected(self):
        try:
            WebDriverWait(self.driver, 10).until(EC.text_to_be_present_in_element((By.CLASS_NAME, "ib-error-amadeus__title"), 'Lo sentimos,'))
            self.close_scrapper()
            print("The bot seems to have been detected...")
            return True
        except Exception:
            return False

    def retrieve_all_flights(self, from_city, to_city, departing_date, returning_date):
        print("Retrieving flights from iberia.com...")
        WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, 'bbki-slice-info-cabin-0-0-E-btn')))
        time.sleep(1.137)
        flight_page_source = self.driver.page_source
        soup = BeautifulSoup(flight_page_source, 'lxml')
        div_departing_flights = soup.find('div', {'class': 'ib-fc-calendar-slides-loading'})
        departing_flights = []
        for div_flight in div_departing_flights.findChildren("div", recursive=False)[2:-1]:
            flight = self.extract_flight(from_city, to_city, departing_date, div_flight)
            departing_flights.append(flight)
        WebDriverWait(self.driver, 60).until(EC.element_to_be_clickable((By.ID, 'bbki-slice-info-cabin-0-0-E-btn'))).click()
        time.sleep(3.337)
        flight_page_source = self.driver.page_source
        soup = BeautifulSoup(flight_page_source, 'lxml')
        div_returning_flights = soup.find('div', {'class': 'ib-fc-calendar-slides-loading'})
        returning_flights = []
        for div_flight in div_returning_flights.findChildren("div", recursive=False)[2:-1]:
            flight = self.extract_flight(from_city, to_city, returning_date, div_flight)
            returning_flights.append(flight)
        return departing_flights, returning_flights

    def extract_flight(self, from_city, to_city, date, div_flight):
        try:
            span_price = div_flight.find_all('span', {'class': 'ib-box-mini-fare__box-price'})[0]
            span_hour = div_flight.find_all('span', {'class': 'ib-info-journey__time'})[0]
            span_duration = div_flight.find_all('span', {'class': 'ib-info-journey__detail'})[1]
            # Remove IATA from hour span
            span_hour.find_all('span', {'class': 'ib-info-journey--iata'})[0].decompose()
            price = span_price.get_text()
            hour = "".join(span_hour.get_text().split())
            duration = span_duration.get_text()
            flight = Flight(from_city, to_city, date, hour, duration, price)
            return flight

        except IndexError:
            print("Handling exception. Price not found for a flight.")
            return

    def accept_cookies(self):
        # Wait for 3 seconds until finding the element
        wait = WebDriverWait(self.driver, 3)
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="onetrust-accept-btn-handler"]'))).click()
