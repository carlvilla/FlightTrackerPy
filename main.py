import traceback
import time
import datetime

from EmailSender import EmailSender
from IberiaWebScrapper import IberiaWebScrapper
from RyanairWebScrapper import RyanairWebScrapper

max_price = 70
from_city = "Madrid"
min_departing_hour = "17:00"
min_returning_hour = "20:00"
email = "carlosvillablanco@gmail.com"
email_sender = EmailSender(email)
num_weeks_to_analyse = 10
destinations = ["Londres", "París", "Amsterdam", "Berlín", "Roma", "Praga", "Atenas", "Viena", "Lisboa", "Dublín", "Budapest", "Estocolmo", "Varsovia", "Copenhague", "Helsinki", "Bruselas", "Oslo", "Zurich", "Milán", "Múnich", "Estambul", "Frankfurt", "Bucarest", "Belgrado", "Sofía", "Lisboa", "Oporto", "Ginebra", "Venecia", "Niza", "Marsella", "Zagreb", "Lviv", "Dubrovnik", "Split", "Ámsterdam", "Birmingham", "Boloña", "Bordeaux", "Breslavia", "Bristol", "Budapest", "Catania", "Colonia", "Corfu", "Córcega", "Cork", "Cracovia", "Doha", "Dortmund", "Dresden", "Dusseldorf", "Edimburgo", "Eindhoven", "Faro", "Florencia", "Gdansk", "Glasgow", "Gotemburgo", "Hamburgo", "Hanóver", "Helsinki", "Ibiza", "Innsbruck", "Jersey", "Kiev", "La Palma", "Lanzarote", "La Valeta", "Liubliana", "Luxemburgo", "Málaga", "Manchester", "Menorca", "Mikonos", "Munich", "Nápoles", "Niza", "Oporto", "Palma de Mallorca", "Pisa", "Podgorica", "Reikiavik", "Riga", "Rotterdam", "Salónica", "San Petersburgo", "Santorini", "Sarajevo", "Sibiu", "Sofía", "Split", "Tallin", "Tánger", "Tenerife", "Tirana", "Turín", "Valencia", "Varsovia", "Varna", "Venecia", "Verona", "Viena", "Vigo", "Zagreb", "Zante", "Zúrich"]

def main():
    # Get dates next weekends
    weekends = get_next_weekends(num_weeks_to_analyse)
    while(True):
        for weekend in weekends:
            for to_city in destinations:
                print("Checking flights from", from_city, "to", to_city, "[", weekend[0], "to", weekend[1], "]")
                scrape_flights(weekend, to_city)
        time.sleep(18000)

def scrape_flights(weekend, to_city):
    web_scrapper = IberiaWebScrapper(min_departing_hour, min_returning_hour, max_price)
    try:
        is_flight_interesting, round_flight = web_scrapper.scrape(from_city, to_city, weekend[0], weekend[1])
        if is_flight_interesting:
            print("An interesting flight was found!")
            print(round_flight)
            email_sender.send_flight(round_flight)
        else:
            # Check flight in next website
            # Check next weekend
            print("No interesting flights found")


    except Exception as e:
        print(traceback.format_exc())
        web_scrapper.driver.quit()
        #scrape_flights(weekend, to_city)

def get_next_friday():
    today = datetime.date.today()
    friday = today + datetime.timedelta((3-today.weekday())%7+1)
    return friday

def get_next_sunday():
    today = datetime.date.today()
    sunday = today + datetime.timedelta((5-today.weekday())%7+1)
    return sunday

def get_next_weekends( num_weeks_to_analyse):
    weekends = []
    today = datetime.date.today()
    friday = today + datetime.timedelta((3-today.weekday())%7+1)
    sunday = today + datetime.timedelta((5 - today.weekday()) % 7 + 1)
    weekends.append((friday.strftime('%d/%m/%Y'), sunday.strftime('%d/%m/%Y')))
    for idx_week in range(1, num_weeks_to_analyse):
        next_friday = friday + datetime.timedelta(7 * idx_week)
        next_sunday = sunday + datetime.timedelta(7 * idx_week)
        weekends.append((next_friday.strftime('%d/%m/%Y'), next_sunday.strftime('%d/%m/%Y')))
    return weekends

if __name__ == '__main__':
    main()