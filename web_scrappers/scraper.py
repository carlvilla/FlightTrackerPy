import traceback
import datetime
import importlib
from emailsender.EmailSender import EmailSender
from flights.InterestingFlightCache import InterestingFlightCache
from web_scrappers.RyanairWebScrapper import RyanairWebScrapper
from web_scrappers.IberiaWebScrapper import IberiaWebScrapper
from web_scrappers.IberiaExpressWebScrapper import IberiaExpressWebScrapper
from web_scrappers.SkyscannerWebScrapper import SkyscannerWebScrapper

import logging
logger = logging.getLogger("root")

class Scraper:

    def __init__(self, settings, proxies):
        self.email_sender = EmailSender()
        self.interesting_flight_cache = InterestingFlightCache(settings["filter_repeated_destinations_but_more_expensive"])
        self.web_scrappers = [] 

        for websites_scrapper in settings["websites_scrappers"]:
            ScrapperClass = getattr(importlib.import_module(__name__), websites_scrapper)
            web_scrapper = ScrapperClass(proxies, **settings)
            self.web_scrappers.append(web_scrapper)


    def scrape_flights(self, from_city, to_city, weekend):
        try:
            for web_scrapper in self.web_scrappers:
                # Retrieve information about the desired flight and weekend
                is_flight_interesting, round_flight = web_scrapper.scrape(from_city, to_city, weekend[0], weekend[1])

                if is_flight_interesting:
                    logger.info("An interesting flight was found!")
                    logger.info(round_flight)

                    # Check if a cheaper flight was already reported
                    is_cheaper_than_before = self.interesting_flight_cache.save_flight(round_flight)
                    if not is_cheaper_than_before:
                        logger.info("The flight is not cheaper than a previously found option. Skipping notification")
                    else:
                        self.email_sender.send_flight(round_flight)
                else:
                    if round_flight is not None:
                        logger.info(f"No interesting flights found. Cheapest: {round_flight.get_total_price():.2f}€")
                    else:
                        logger.info("No interesting flights found")
        except Exception:
            logger.error(traceback.format_exc())
        #web_scrapper.close_scrapper()

def get_next_friday():
    today = datetime.date.today()
    friday = today + datetime.timedelta((3-today.weekday())%7+1)
    return friday

def get_next_saturday():
    today = datetime.date.today()
    friday = today + datetime.timedelta((4-today.weekday())%7+1)
    return friday

def get_next_sunday():
    today = datetime.date.today()
    sunday = today + datetime.timedelta((5-today.weekday())%7+1)
    return sunday

def get_next_weekends(num_weeks_to_analyse):
    weekends = []
    today = datetime.date.today()
    # It it is currently a weekend, start with the following
    if today.weekday() >= 4:
        today = today + datetime.timedelta(3)
    first_day = get_next_friday()
    sunday = today + datetime.timedelta((5 - today.weekday()) % 7 + 1)
    weekends.append((first_day.strftime('%d/%m/%Y'), sunday.strftime('%d/%m/%Y')))
    for idx_week in range(1, num_weeks_to_analyse):
        next_first_day = first_day + datetime.timedelta(7 * idx_week)
        next_sunday = sunday + datetime.timedelta(7 * idx_week)
        weekends.append((next_first_day.strftime('%d/%m/%Y'), next_sunday.strftime('%d/%m/%Y')))
    return weekends
