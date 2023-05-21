class RoundFlight:

    def __init__(self, departing_flight, returning_flight):
        self.departing_flight = departing_flight
        self.returning_flight = returning_flight

    def get_total_price(self):
        return self.departing_flight.get_price() + self.returning_flight.get_price()

    def __str__(self) -> str:
        return "--- ROUND FLIGHT INFORMATION ---\n Total price:" + str(self.get_total_price()) + "\n*** DEPARTING FLIGHT ***\n From: " + self.departing_flight.from_city + "\n To: " + self.departing_flight.to_city + "\n Departing date: " \
               + self.departing_flight.departing_date + " (" + self.departing_flight.departing_hour.strftime("%H:%M") + ") \n Duration: " + self.departing_flight.departing_duration \
               + "\n Price: " + str(self.departing_flight.get_price()) + "\n *** RETURNING FLIGHT ***\n From: " + self.returning_flight.to_city + "\n To: " + self.returning_flight.from_city + "\n Departing date: " \
               + self.returning_flight.departing_date + " (" + self.returning_flight.departing_hour.strftime("%H:%M") + ") \n Duration: " + self.returning_flight.departing_duration \
               + "\n Price: " + str(self.returning_flight.get_price()) + "\n"