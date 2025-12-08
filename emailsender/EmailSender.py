import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

class EmailSender:

    def __init__(self):
        load_dotenv()
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = os.getenv("SENDER_EMAIL_ADDRESS")
        self.password = os.getenv("SENDER_EMAIL_PASSWORD")
        self.receiver_email = os.getenv("RECEIVER_EMAIL_ADDRESS")

    def send_flight(self, round_flight):
        # Create a multipart message
        message = MIMEMultipart()
        message["From"] = self.sender_email
        message["To"] = self.receiver_email
        message["Subject"] = "An interesting flight was found!"
        # Add body to the email
        body = str(round_flight)
        message.attach(MIMEText(body, "plain"))
        # Connect to the SMTP server and send the email
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.password)
            server.send_message(message)
        print("Email sent successfully!")