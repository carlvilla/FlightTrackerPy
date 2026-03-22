import datetime
import importlib
import logging
import traceback

from emailsender.EmailSender import EmailSender
from flights.InterestingFlightCache import InterestingFlightCache

logger = logging.getLogger("root")


class Scraper:
    def __init__(self, settings, proxies):
        self.email_sender = EmailSender()
        self.interesting_flight_cache = InterestingFlightCache(
            settings["filter_repeated_destinations_but_more_expensive"]
        )
        self.web_scrappers = []

        for scrapper_name in settings["websites_scrappers"]:
            try:
                module = importlib.import_module(f"web_scrappers.{scrapper_name}")
                ScrapperClass = getattr(module, scrapper_name)
                web_scrapper = ScrapperClass(proxies, **settings)
                self.web_scrappers.append(web_scrapper)
                logger.info("Loaded scraper: %s", scrapper_name)
            except (ImportError, AttributeError) as exc:
                logger.error(
                    "Could not load scraper '%s' — check that 'web_scrappers/%s.py' exists "
                    "and defines a class named '%s'. Error: %s",
                    scrapper_name, scrapper_name, scrapper_name, exc,
                )

    def scrape_flights(self, from_city, to_city, weekend):
        try:
            for web_scrapper in self.web_scrappers:
                is_flight_interesting, round_flight = web_scrapper.scrape(
                    from_city, to_city, weekend[0], weekend[1]
                )

                if is_flight_interesting:
                    logger.info("An interesting flight was found!")
                    logger.info(round_flight)

                    is_cheaper_than_before = self.interesting_flight_cache.save_flight(round_flight)
                    if not is_cheaper_than_before:
                        logger.info(
                            "The flight is not cheaper than a previously found option. Skipping notification"
                        )
                    else:
                        self.email_sender.send_flight(round_flight)
                else:
                    if round_flight is not None:
                        logger.info(
                            f"No interesting flights found. Cheapest: {round_flight.get_total_price():.2f}€"
                        )
                    else:
                        logger.info("No interesting flights found")
        except Exception:
            logger.error(traceback.format_exc())


def get_next_friday():
    today = datetime.date.today()
    friday = today + datetime.timedelta((3 - today.weekday()) % 7 + 1)
    return friday


def get_next_saturday():
    today = datetime.date.today()
    friday = today + datetime.timedelta((4 - today.weekday()) % 7 + 1)
    return friday


def get_next_sunday():
    today = datetime.date.today()
    sunday = today + datetime.timedelta((5 - today.weekday()) % 7 + 1)
    return sunday


def get_next_weekends(num_weeks_to_analyse):
    weekends = []
    today = datetime.date.today()
    if today.weekday() >= 4:
        today = today + datetime.timedelta(3)
    first_day = get_next_friday()
    sunday = today + datetime.timedelta((5 - today.weekday()) % 7 + 1)
    weekends.append((first_day.strftime("%d/%m/%Y"), sunday.strftime("%d/%m/%Y")))
    for idx_week in range(1, num_weeks_to_analyse):
        next_first_day = first_day + datetime.timedelta(7 * idx_week)
        next_sunday = sunday + datetime.timedelta(7 * idx_week)
        weekends.append(
            (next_first_day.strftime("%d/%m/%Y"), next_sunday.strftime("%d/%m/%Y"))
        )
    return weekends
