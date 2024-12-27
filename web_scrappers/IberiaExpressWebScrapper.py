import calendar
from datetime import datetime


from web_scrappers.AirlineWebScrapper import AirlineWebScrapper
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from flights.Flight import Flight
import re

class IberiaExpressWebScrapper(AirlineWebScrapper):

    def __init__(self, min_departing_hour, min_returning_hour, max_price, num_weeks_to_analyse, proxies):
        self.URL = "https://www.iberiaexpress.com/es"
        super().__init__(self.URL, min_departing_hour, min_returning_hour, max_price, num_weeks_to_analyse, proxies)

    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        # Wait on the webpage before trying anything
        time.sleep(4.546)
        self.accept_cookies()
        flight_origin = self.driver.find_element(by='xpath', value='//input[@id="ib-org"]')
        flight_destiny = self.driver.find_element(by='xpath', value='//input[@id="ib-dst"]')
        flight_date = self.driver.find_element(by='xpath', value='//input[@id="ib-ow"]')
        flight_origin.click()
        flight_origin.send_keys(from_city)
        time.sleep(3.424)
        flight_origin.send_keys(Keys.ENTER)
        time.sleep(5.324)
        flight_destiny.send_keys(to_city)
        time.sleep(4.343)
        flight_destiny.send_keys(Keys.ENTER)
        time.sleep(3.613)
        flight_date.click()
        flight_date.click()
        time.sleep(3.632)
        self.set_dates(departing_date, returning_date)
        time.sleep(4.632)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[@aria-label="Close Passengers Selection"]'))).click()
        time.sleep(3.432)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//button[normalize-space()="BUSCAR VUELO"]'))).click()

        if self.was_bot_detected():
            #self.solve_captcha()
            return False, None

        departing_flights, returning_flights = self.retrieve_all_flights(from_city, to_city, departing_date, returning_date)
        departing_flights = self.filter_flights_by_departing_hour(departing_flights)
        returning_flights = self.filter_flights_by_returning_hour(returning_flights)
        round_flight = self.find_cheapest_flights(departing_flights, returning_flights)
        print("Successful scrapping")
        return self.check_round_flights_under_max_price(round_flight), round_flight

    def solve_captcha(self):
        time.sleep(2.632)
        print("Trying to solve captcha...")
        #solver = RecaptchaSolver(driver=self.driver)
        #recaptcha_iframe = self.driver.find_element(By.XPATH, '//iframe[@id="main-iframe"]')
        #solver.click_recaptcha_v2(iframe=recaptcha_iframe)
        print("Captcha solved?")

    def set_dates(self, departing_date, returning_date):
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
        departing_date_skyscanner_format = departing_weekday + ", " + str(
            departing_day) + " de " + departing_month + " de " + str(departing_year)
        returning_date_skyscanner_format = returning_weekday + ", " + str(
            returning_day) + " de " + returning_month + " de " + str(returning_year)
        time.sleep(2.551)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@aria-label="' + departing_date_skyscanner_format + '"]'))).click()
        time.sleep(2.243)
        WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, '//div[@aria-label="' + returning_date_skyscanner_format + '"]'))).click()
        time.sleep(2.352)

    def was_bot_detected(self):
        try:
            print("CHECKING IF BOT DETECTED")
            WebDriverWait(self.driver, 3).until(EC.presence_of_element_located((By.XPATH, "//iframe[@id='main-iframe']")))
            print("The bot seems to have been detected...")
            return True
        except Exception:
            print("NOT DETECTED")
            return False

    def retrieve_all_flights(self, from_city, to_city, departing_date, returning_date):
        WebDriverWait(self.driver, 50).until(EC.presence_of_element_located((By.XPATH, "//journey[@formcontrolname='journey']")))
        print("Retrieving flights from iberiaexpress.com...")
        time.sleep(1.537)

        departing_flights = []
        flight_page_source = self.driver.page_source
        soup = BeautifulSoup(flight_page_source, 'lxml')
        journey_departing_flights = soup.find_all('journey')
        for journey_flight in journey_departing_flights:
            flight = self.extract_flight(from_city, to_city, departing_date, journey_flight)
            departing_flights.append(flight)

        # Click on price first price (no club to avoid having to be registered) to show return flights
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='col-auto px-1 text-center noclub ng-star-inserted']/button"))).click()
        WebDriverWait(self.driver, 5).until(EC.element_to_be_clickable((By.XPATH, "//input[@name='outbound']"))).click()
        time.sleep(1.337)

        returning_flights = []
        flight_page_source = self.driver.page_source
        soup = BeautifulSoup(flight_page_source, 'lxml')
        journey_returning_flights = soup.find_all('journey')
        for journey_flight in journey_returning_flights:
            flight = self.extract_flight(to_city, from_city, departing_date, journey_flight)
            returning_flights.append(flight)

        return departing_flights, returning_flights

    def extract_flight(self, from_city, to_city, date, journey_flight):
        try:
            div_price = journey_flight.find('div', {'class': 'col-auto px-1 text-center club ng-star-inserted'})
            price = div_price.find(string=re.compile(r"[0-9]+€")).parent.parent.text
            div_hour = journey_flight.find('div', {'class': 'col-auto d-flex flex-column align-items-center pl-del'})
            hour = next(div_hour.children, None).text.replace("H", "")
            div_duration = journey_flight.find('div', {'class': 'col-auto ng-star-inserted'})
            duration = div_duration.text
            flight = Flight(from_city, to_city, date, hour, duration, price)
            return flight
        except IndexError:
            print("Handling exception. Price not found for a flight.")
            return

    def accept_cookies(self):
        WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[normalize-space()="Aceptar"]'))).click()
