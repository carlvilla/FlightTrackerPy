# FlightTrackerPy
Automatically scrape airline tickets at your desired price, origin, destination, and schedule, and get notified via email. Currently it only checks Ryanair flights for weekend trips.

## Configuration

Modify the settings.json file to set your preferences.

The following environment variables need to be set for email notifications:
- `SENDER_EMAIL_ADDRESS`: Email address used to send notifications.
- `SENDER_EMAIL_PASSWORD`: The password of the email used for notifications.
- `RECEIVER_EMAIL_ADDRESS`: Email address to receive the notifications.