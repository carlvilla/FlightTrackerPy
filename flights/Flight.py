from datetime import datetime

class Flight:

    def __init__(self, from_city: str, to_city: str, departing_date:str, departing_hour:str, departing_duration:str, price: str):
        self.from_city = from_city
        self.to_city = to_city
        self.departing_date = departing_date
        self.departing_hour = datetime.strptime(departing_hour, '%H:%M').time()
        self.departing_duration = departing_duration
        self.price: float = self.remove_euro(price)

    def get_departing_hour(self):
        return self.departing_hour

    def get_price(self):
        return self.price

    def remove_euro(self, text):
        price_without_euro_symbol = text.replace('€', '')
        maketrans = price_without_euro_symbol.maketrans
        return float(price_without_euro_symbol.translate(maketrans(',.', '.,', ' ')).replace(',', ", "))

    def __str__(self) -> str:
        return "--- FLIGHT INFORMATION ---\n From: " + self.from_city + "\n To: " + self.to_city + "\n Departing date: " \
               + self.departing_date + " (" + self.departing_hour.strftime("%H:%M") + ") \n Duration: " + self.departing_duration \
               + "\n Price: " + str(self.get_price()) + "\n"