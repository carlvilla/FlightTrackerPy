from datetime import datetime

class Flight:

    def __init__(self, from_city, to_city, departing_date, departing_hour, departing_duration, price):
        self.from_city = from_city
        self.to_city = to_city
        self.departing_date = departing_date
        self.departing_hour = datetime.strptime(departing_hour, '%H:%M').time()
        self.departing_duration = departing_duration
        self.price = self.remove_euro(price)

    def get_departing_hour(self):
        return self.departing_hour

    def get_price(self):
        return self.price

    def remove_euro(self, text):
        return float(text.replace('€', '').replace(' ', '').replace('.', ''))

    def __str__(self) -> str:
        return "--- FLIGHT INFORMATION ---\n From: " + self.from_city + "\n To: " + self.to_city + "\n Departing date: " \
               + self.departing_date + " (" + self.departing_hour.strftime("%H:%M") + ") \n Duration: " + self.departing_duration \
               + "\n Price: " + str(self.get_price()) + "\n"