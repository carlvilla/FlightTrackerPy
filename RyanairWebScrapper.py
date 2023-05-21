from AirlineWebScrapper import AirlineWebScrapper
from selenium.webdriver.support import expected_conditions as EC
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

class RyanairWebScrapper(AirlineWebScrapper):

    def __init__(self):
        super().__init__("https://www.ryanair.com/")


    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        self.accept_cookies()
        flight_origin = self.driver.find_element(by='xpath', value='//input[@id="input-button__departure"]')
        flight_destiny = self.driver.find_element(by='xpath', value='//input[@id="input-button__destination"]')
        flight_date = self.driver.find_element(by='xpath', value='//input[@class="-button__input ng-star-inserted"]')
        flight_return_date = self.driver.find_element(by='xpath', value='//input[@class="-button__input ng-star-inserted"]')
        # flight_origin.send_keys("Madrid (MAD)")
        # time.sleep(2)
        flight_destiny.send_keys("Berlin Brandenburg")
        time.sleep(6.54343)
        flight_date.send_keys(" vie, 26 may ")
        time.sleep(10.28)
        flight_return_date.send_keys(" jue, 1 jun ")
        time.sleep(6.2329)

        select_nominee = WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'flight-search-widget__start-search ng-tns-c83-3 ry-button--gradient-yellow'))).click()

        # search_button = driver.find_element(By.ID, "buttonSubmit1")
        # search_button.click()
        time.sleep(30)

    def remove_euro(self, text):
        pass

    def accept_cookies(self):
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@class="cookie-popup-with-overlay__button"]'))).click()
