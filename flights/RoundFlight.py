from flights.Flight import Flight
from typing import Optional

class RoundFlight:

    def __init__(self, departing_flight: Flight, returning_flight: Flight, website_found: str, price: Optional[float] =None):
        self.departing_flight = departing_flight
        self.returning_flight = returning_flight
        if price is not None:
            self.price: float = self.remove_euro(price)
        else:
            self.price: float = self.departing_flight.get_price() + self.returning_flight.get_price()
        self.price = round(self.price, 2)
        self.website_found = website_found

    def get_departing_hour(self):
        return self.departing_flight.get_departing_hour()

    def get_returning_hour(self):
        return self.returning_flight.get_departing_hour()

    def get_total_price(self):
        return self.price

    def remove_euro(self, text):
        price_without_euro_symbol = text.replace('€', '')
        maketrans = price_without_euro_symbol.maketrans
        return float(price_without_euro_symbol.translate(maketrans(',.', '.,', ' ')).replace(',', ", "))

    def __str__(self) -> str:
        return "--- ROUND FLIGHT INFORMATION ---\n Found in: " + self.website_found + "\nTotal price:" + str(self.get_total_price()) + "\n*** DEPARTING FLIGHT ***\n From: " + self.departing_flight.from_city + "\n To: " + self.departing_flight.to_city + "\n Departing date: " \
               + self.departing_flight.departing_date + " (" + self.departing_flight.departing_hour.strftime("%H:%M") + ") \n Duration: " + self.departing_flight.departing_duration \
               + "\n Price: " + str(self.departing_flight.get_price()) + "\n *** RETURNING FLIGHT ***\n From: " + self.returning_flight.to_city + "\n To: " + self.returning_flight.from_city + "\n Departing date: " \
               + self.returning_flight.departing_date + " (" + self.returning_flight.departing_hour.strftime("%H:%M") + ") \n Duration: " + self.returning_flight.departing_duration \
               + "\n Price: " + str(self.returning_flight.get_price()) + "\n"