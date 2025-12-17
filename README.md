# FlightTrackerPy
Automatically scrape airline tickets at your desired price, origin, destination, and schedule, and get notified via email. Currently it only checks Ryanair flights for weekend trips.

## App configuration

Modify the settings.json file to set your preferences, including:
- `origins`: List of origin cities.
- `destinations`: List of destination cities.
- `max_price`: Maximum price for the round trip.
- `min_departing_hour`: Minimum hour for departing flights (24-hour format).
- `min_returning_hour`: Minimum hour for returning flights (24-hour format).
- `num_weeks_to_analyse`: Number of weeks ahead to check for flights.
- `filter_repeated_destinations_but_more_expensive`: If true, filters out repeated destinations that are more expensive than previously found options.

## Environment Variables

The following environment variables need to be set for email notifications:
- `SENDER_EMAIL_ADDRESS`: Email address used to send notifications.
- `SENDER_EMAIL_PASSWORD`: The password of the email used for notifications.
- `RECEIVER_EMAIL_ADDRESS`: Email address to receive the notifications.