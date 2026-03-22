import logging
import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from flights.Flight import Flight
from flights.RoundFlight import RoundFlight
from web_scrappers.AirlineWebScrapper import AirlineWebScrapper

logger = logging.getLogger("root")

_CITY_TO_IATA = {
    "a coruña": "LCG",
    "agadir": "AGA",
    "alicante": "ALC",
    "almería": "LEI",
    "almeria": "LEI",
    "ámsterdam": "AMS",
    "amsterdam": "AMS",
    "argel": "ALG",
    "asturias": "OVD",
    "atenas": "ATH",
    "banjul": "BJL",
    "barcelona": "BCN",
    "bari": "BRI",
    "basilea": "BSL",
    "bilbao": "BIO",
    "birmingham": "BHX",
    "birminghan": "BHX",
    "bolonia": "BLQ",
    "bruselas": "BRU",
    "burdeos": "BOD",
    "cagliari": "CAG",
    "catania": "CTA",
    "copenhague": "CPH",
    "creta": "HER",
    "dakar": "DSS",
    "dublín": "DUB",
    "dublin": "DUB",
    "dubrovnik": "DBV",
    "düsseldorf": "DUS",
    "edimburgo": "EDI",
    "estocolmo": "ARN",
    "faro": "FAO",
    "florencia": "FLR",
    "fuerteventura": "FUE",
    "génova": "GOA",
    "genova": "GOA",
    "ginebra": "GVA",
    "gran canaria": "LPA",
    "granada": "GRX",
    "hamburgo": "HAM",
    "hanóver": "HAJ",
    "hanover": "HAJ",
    "ibiza": "IBZ",
    "jerez (cádiz)": "XRY",
    "la palma": "SPC",
    "lanzarote": "ACE",
    "lisboa": "LIS",
    "liverpool": "LPL",
    "londres": "LGW",
    "lyon": "LYS",
    "madrid": "MAD",
    "málaga": "AGP",
    "malaga": "AGP",
    "malta": "MLA",
    "manchester": "MAN",
    "marrakech": "RAK",
    "marsella": "MRS",
    "menorca": "MAH",
    "mikonos": "JMK",
    "milán": "MXP",
    "milan": "MXP",
    "múnich": "MUC",
    "munich": "MUC",
    "nantes": "NTE",
    "nápoles": "NAP",
    "napoles": "NAP",
    "niza": "NCE",
    "nuremberg": "NUE",
    "olbia": "OLB",
    "oporto": "OPO",
    "oslo": "OSL",
    "palermo": "PMO",
    "palma (mallorca)": "PMI",
    "palma": "PMI",
    "mallorca": "PMI",
    "parís (charles de gaulle)": "CDG",
    "paris (charles de gaulle)": "CDG",
    "parís (orly)": "ORY",
    "paris (orly)": "ORY",
    "paris": "CDG",
    "praga": "PRG",
    "cracovia": "KRK",
    "varsovia": "WAW",
    "reikiavik": "KEF",
    "roma (fiumicino)": "FCO",
    "roma": "FCO",
    "san sebastián": "EAS",
    "santander": "SDR",
    "santiago": "SCQ",
    "santorini": "JTR",
    "sevilla": "SVQ",
    "split": "SPU",
    "stuttgart": "STR",
    "sofía": "SOF",
    "sofia": "SOF",
    "tánger": "TNG",
    "tanger": "TNG",
    "tetuán": "TTU",
    "tetouan": "TTU",
    "tenerife": "TFS",
    "túnez": "TUN",
    "tunez": "TUN",
    "turín": "TRN",
    "turin": "TRN",
    "valencia": "VLC",
    "venecia": "VCE",
    "viena": "VIE",
    "vigo": "VGO",
    "zúrich": "ZRH",
    "zurich": "ZRH",
    "luxembourg": "LUX",
    "billund": "BLL",
    "budapest": "BUD",
    "bucarest": "OTP",
    "rabat": "RBA",
    "fez": "FEZ",
    "essaouira": "ESU",
    "nador": "NDR",
    "kaunas": "KUN",
    "bristol": "BRS",
    "eindhoven": "EIN",
    "amman": "AMM",
    "alghero": "AHO",
    "brindisi": "BDS",
    "pisa": "PSA",
}

_MONTH_ABBR = {
    1: "ENE",
    2: "FEB",
    3: "MAR",
    4: "ABR",
    5: "MAY",
    6: "JUN",
    7: "JUL",
    8: "AGO",
    9: "SEP",
    10: "OCT",
    11: "NOV",
    12: "DIC",
}


def _city_to_iata(city_name: str) -> str:
    key = city_name.lower().strip()
    if key in _CITY_TO_IATA:
        return _CITY_TO_IATA[key]
    for k, v in _CITY_TO_IATA.items():
        if k in key or key in k:
            return v
    logger.warning("Vueling: no IATA code found for city '%s'", city_name)
    return city_name.upper()[:3]


def _parse_price_from_label(aria_label: str) -> float | None:
    m = re.search(r"([\d]+),([\d]+)\s+EUR", aria_label)
    if m:
        try:
            return float(f"{m.group(1)}.{m.group(2)}")
        except ValueError:
            pass
    return None


class VuelingWebScrapper(AirlineWebScrapper):
    def __init__(self, proxies, **kwargs):
        logger.info("Setting up Vueling web scrapper...")
        self.URL = "https://www.vueling.com/es/reserva-tu-vuelo/calendario-de-precios"
        super().__init__(
            self.URL,
            proxies,
            min_departing_hour=kwargs["min_departing_hour"],
            min_returning_hour=kwargs["min_returning_hour"],
            max_price=kwargs["max_price"],
            num_weeks_to_analyse=kwargs["num_weeks_to_analyse"],
            show_browser=kwargs.get("show_browser", False),
        )

    def scrape(
        self,
        from_city="Madrid",
        to_city="Barcelona",
        departing_date="26/05/2023",
        returning_date="28/05/2023",
    ):
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

    def scrape_airline(self, from_city, to_city, departing_date, returning_date):
        from_iata = _city_to_iata(from_city)
        to_iata = _city_to_iata(to_city)

        calendar_url = (
            f"https://www.vueling.com/es/reserva-tu-vuelo/calendario-de-precios"
            f"?originCalendar={from_iata}&destinationCalendar={to_iata}"
            f"&dateComplete={departing_date}"
        )
        self.driver.get(calendar_url)
        time.sleep(3)
        self.accept_cookies()

        _dep = datetime.strptime(departing_date, "%d/%m/%Y")
        _ret = datetime.strptime(returning_date, "%d/%m/%Y")

        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "div.calendar-day_label")
                )
            )
        except Exception:
            logger.warning(
                "Vueling: calendar did not load for %s→%s", from_city, to_city
            )
            return False, None

        time.sleep(2)

        dep_month_abbr = _MONTH_ABBR[_dep.month]
        ret_month_abbr = _MONTH_ABBR[_ret.month]

        self._switch_outbound_calendar_to_month(dep_month_abbr, _dep.year)
        time.sleep(1)

        if _dep.month != _ret.month or _dep.year != _ret.year:
            self._switch_return_calendar_to_month(ret_month_abbr, _ret.year)
            time.sleep(2)

        departing_price = self._get_price_for_day(
            _dep.day, dep_month_abbr, calendar_index=0
        )
        returning_price = self._get_price_for_day(
            _ret.day, ret_month_abbr, calendar_index=1
        )

        if departing_price is None or returning_price is None:
            logger.warning(
                "Vueling: no price found for %s→%s dep=%s(%s) ret=%s(%s)",
                from_city,
                to_city,
                _dep.day,
                dep_month_abbr,
                _ret.day,
                ret_month_abbr,
            )
            return False, None

        total_price = round(departing_price + returning_price, 2)
        price_str = f"{total_price}€"

        departing_flight = Flight(
            from_city, to_city, departing_date, "00:00", "", f"{departing_price}€"
        )

        returning_flight = Flight(
            to_city, from_city, returning_date, "00:00", "", f"{returning_price}€"
        )

        logger.warning("Vueling crawler currently does not consider departure hours")

        """
        if not self.filter_flights_by_departing_hour(
            [departing_flight]
        ) or not self.filter_flights_by_returning_hour([returning_flight]):
            return False
        """

        round_flight = RoundFlight(
            departing_flight, returning_flight, calendar_url, price_str
        )

        logger.info(
            "Vueling: %s→%s dep=%s %.2f€ ret=%s %.2f€ total=%.2f€",
            from_city,
            to_city,
            departing_date,
            departing_price,
            returning_date,
            returning_price,
            total_price,
        )
        return self.check_round_flights_under_max_price(round_flight), round_flight

    def _get_price_for_day(
        self, day: int, month_abbr: str, calendar_index: int
    ) -> float | None:
        try:
            all_labels = self.driver.find_elements(
                By.CSS_SELECTOR, "div.calendar-day_label"
            )
            total = len(all_labels)
            half = total // 2
            if calendar_index == 0:
                subset = all_labels[:half]
            else:
                subset = all_labels[half:]

            target_prefix = f"{day} {month_abbr} "
            for el in subset:
                aria = el.get_attribute("aria-label") or ""
                if aria.startswith(target_prefix) and "EUR" in aria:
                    price = _parse_price_from_label(aria)
                    if price is not None and price > 0:
                        logger.debug(
                            "Vueling: calendar[%d] day=%d %s price=%.2f (label=%r)",
                            calendar_index,
                            day,
                            month_abbr,
                            price,
                            aria,
                        )
                        return price
        except Exception as exc:
            logger.warning(
                "Vueling: error reading calendar[%d]: %s", calendar_index, exc
            )
        return None

    def _switch_outbound_calendar_to_month(self, month_abbr: str, year: int):
        target_label = f"{month_abbr} {year}"
        try:
            tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f'(//span[contains(@class,"vy-date-tabs-selector_item_content")][@aria-label="{target_label}"])[1]',
                    )
                )
            )
            tab.click()
            logger.debug("Vueling: switched outbound calendar to %s", target_label)
        except Exception as exc:
            logger.warning(
                "Vueling: could not switch outbound calendar to %s: %s",
                target_label,
                exc,
            )

    def _switch_return_calendar_to_month(self, month_abbr: str, year: int):
        target_label = f"{month_abbr} {year}"
        try:
            tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        f'(//span[contains(@class,"vy-date-tabs-selector_item_content")][@aria-label="{target_label}"])[2]',
                    )
                )
            )
            tab.click()
            logger.debug("Vueling: switched return calendar to %s", target_label)
        except Exception:
            try:
                tabs = self.driver.find_elements(
                    By.XPATH,
                    f'//span[contains(@class,"vy-date-tabs-selector_item_content")][@aria-label="{target_label}"]',
                )
                if len(tabs) >= 2:
                    tabs[1].click()
                elif tabs:
                    tabs[0].click()
            except Exception as exc2:
                logger.warning(
                    "Vueling: could not switch return calendar to %s: %s",
                    target_label,
                    exc2,
                )

    def was_bot_detected(self):
        try:
            WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        '//iframe[@title="reCAPTCHA"] | //*[contains(@class,"captcha")]',
                    )
                )
            )
            logger.warning("Vueling: bot detection triggered.")
            return True
        except Exception:
            return False

    def _get_cookies_accept_button_xpath(self) -> str:
        return (
            '//button[normalize-space()="OK, LAS ACEPTO"] | '
            '//button[normalize-space()="Aceptar todas"] | '
            '//button[@id="onetrust-accept-btn-handler"]'
        )
