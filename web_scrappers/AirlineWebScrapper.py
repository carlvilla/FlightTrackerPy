import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from driver.selenium_driver import setting_up_selenium
from flights.RoundFlight import RoundFlight


class AirlineWebScrapper(ABC):
    def __init__(
        self,
        URL,
        proxies,
        min_departing_hour,
        min_returning_hour,
        max_price,
        num_weeks_to_analyse,
        show_browser=False,
    ):
        self.proxies = proxies
        self.driver = setting_up_selenium(show_browser)
        self.min_departing_hour = datetime.strptime(min_departing_hour, "%H:%M").time()
        self.min_returning_hour = datetime.strptime(min_returning_hour, "%H:%M").time()
        self.url = URL
        self.max_price = max_price
        self.num_weeks_to_analyse = num_weeks_to_analyse
        self.were_cookies_accepted = False
        self.path_screenshots = "./screenshots"
        self.path_exception_screenshots = "./screenshots/exception"
        Path(self.path_exception_screenshots).mkdir(parents=True, exist_ok=True)

    def scrape(
        self,
        from_city="Madrid (MAD)",
        to_city="Nueva York (NYC)",
        departing_date="26/05/2023",
        returning_date="28/05/2023",
    ) -> Tuple[bool, Optional[RoundFlight]]:
        self.driver.get(self.url)
        try:
            is_flight_interesting, round_flight = self.scrape_airline(
                from_city, to_city, departing_date, returning_date
            )
        except Exception:
            self.save_screenshot(
                f"{from_city}_{to_city}_{departing_date}_{returning_date}"
            )
            return False, None
        return is_flight_interesting, round_flight

    @abstractmethod
    def scrape_airline(
        self, from_city, to_city, departing_date, returning_date
    ) -> Tuple[bool, Optional[RoundFlight]]:
        pass

    def close_scrapper(self):
        self.driver.quit()

    def filter_round_flights_by_hours(self, flights):
        flights_without_none_type = filter(None, flights)
        return list(
            filter(
                lambda flight: flight.get_departing_hour() > self.min_departing_hour
                and flight.get_returning_hour() > self.min_returning_hour,
                flights_without_none_type,
            )
        )

    def filter_flights_by_departing_hour(self, flights):
        flights_without_none_type = filter(None, flights)
        return list(
            filter(
                lambda flight: flight.get_departing_hour() > self.min_departing_hour,
                flights_without_none_type,
            )
        )

    def filter_flights_by_returning_hour(self, flights):
        flights_without_none_type = filter(None, flights)
        return list(
            filter(
                lambda flight: flight.get_departing_hour() > self.min_returning_hour,
                flights_without_none_type,
            )
        )

    def check_round_flights_under_max_price(self, round_flight) -> bool:
        if round_flight is not None:
            return round_flight.get_total_price() < self.max_price
        return False

    def find_cheapest_flights(
        self, departing_flights, returning_flights
    ) -> Optional[RoundFlight]:
        if (
            departing_flights is not None
            and len(departing_flights) > 0
            and returning_flights is not None
            and len(returning_flights) > 0
        ):
            cheapest_departing_flight = min(
                departing_flights, key=lambda flight: flight.get_price()
            )
            cheapest_returning_flight = min(
                returning_flights, key=lambda flight: flight.get_price()
            )
            round_flight = RoundFlight(
                cheapest_departing_flight, cheapest_returning_flight, self.url
            )
            return round_flight

    def find_cheapest_round_flight(self, round_flights):
        if round_flights is not None and len(round_flights) > 0:
            cheapest_flight = min(
                round_flights, key=lambda flight: flight.get_total_price()
            )
            return cheapest_flight

    def save_screenshot(self, filename, exception=False):
        path_save_screenshot = (
            self.path_exception_screenshots if exception else self.path_screenshots
        )
        self.driver.get_screenshot_as_file(
            os.path.join(path_save_screenshot, f"{filename}.png")
        )

    def accept_cookies(self):
        if not self.were_cookies_accepted:
            try:
                WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, self._get_cookies_accept_button_xpath())
                    )
                ).click()
                self.were_cookies_accepted = True
            except Exception:
                pass

    @abstractmethod
    def _get_cookies_accept_button_xpath(self) -> str:
        pass
