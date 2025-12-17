from flights.RoundFlight import RoundFlight

class InterestingFlightCache():
    """
    A simple in-memory cache to store interesting flights and avoid sending repeated destinations at higher prices.
    """
    
    def __init__(self, save_flights: bool = True):
        self.cache = {}
        self.save_flights = save_flights

    def save_flight(self, round_flight: RoundFlight) -> bool:
        """
        Saves the provided flight if it is cheaper than a previously stored one.

        Returns
        -------
        bool
            True if the flight was saved (i.e., it is cheaper than the previous one or not present), False otherwise.
        """
        if not self.save_flights:
            return True

        from_city = round_flight.departing_flight.from_city
        to_city = round_flight.departing_flight.to_city
        price = round_flight.get_total_price()

        # Define HashMap key with from and to cities
        key = (from_city, to_city)
        
        # Check if the flight is already in the cache
        if (key in self.cache and self.cache[key] > price) or key not in self.cache:
            self.cache[key] = price
            print(f"Updated cache for flight from {from_city} to {to_city} with price {price}")
            return True
        
        return False