import traceback
import datetime
import importlib
from emailsender.EmailSender import EmailSender

def scrape_flights(from_city, to_city, weekend, settings, proxies):
    email_sender = EmailSender()
    for websites_scrapper in settings["websites_scrappers"]:
        ScrapperClass = getattr(importlib.import_module("__main__"), websites_scrapper)
        web_scrapper = ScrapperClass(settings["min_departing_hour"], settings["min_returning_hour"], settings["max_price"], settings["num_weeks_to_analyse"], proxies)
        try:
            is_flight_interesting, round_flight = web_scrapper.scrape(from_city, to_city, weekend[0], weekend[1])
            if is_flight_interesting:
                print("An interesting flight was found!")
                print(round_flight)
                email_sender.send_flight(round_flight)
            else:
                if round_flight is not None:
                    print(f"No interesting flights found. Cheapest: {round_flight.get_total_price():.2f}€")
                else:
                    print("No interesting flights found")
        except Exception as e:
            print(traceback.format_exc())
        web_scrapper.close_scrapper()

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
