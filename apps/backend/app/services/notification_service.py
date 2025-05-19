from typing import Dict, Any
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class NotificationService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_username = os.getenv("SMTP_USERNAME", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", "noreply@vogo.family")

    async def send_booking_confirmation(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Send booking confirmation email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.from_email
            msg['To'] = "reservations@vogo.family"
            msg['Subject'] = f"New Service Booking - {booking_details['service_name']}"

            body = f"""
            New Service Booking Details:
            
            Service: {booking_details['service_name']}
            Date: {booking_details['date']}
            Time: {booking_details['time']}
            Location: {booking_details['location']}
            Issue: {booking_details['issue']}
            
            Customer Contact: {booking_details.get('customer_contact', 'Not provided')}
            
            This is an automated message from Vogo.Family Chatbot.
            """

            msg.attach(MIMEText(body, 'plain'))

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            return {
                'status': 'success',
                'message': 'Booking confirmation sent successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
