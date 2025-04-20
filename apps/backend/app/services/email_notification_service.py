import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class EmailNotificationService:
    """Service for sending email notifications"""
    
    def __init__(self):
        """Initialize the email notification service"""
        self.smtp_server = os.environ.get("SMTP_SERVER", "")
        self.smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        self.smtp_username = os.environ.get("SMTP_USERNAME", "")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "")
        self.from_email = os.environ.get("FROM_EMAIL", "notifications@vogo.family")
        
        # For demo purposes, we'll log emails instead of sending them if SMTP credentials are not provided
        self.use_mock = not (self.smtp_server and self.smtp_username and self.smtp_password)
        if self.use_mock:
            logger.warning("SMTP credentials not provided. Using mock email service.")
    
    def send_email(self, 
                  to_email: str, 
                  subject: str, 
                  body_html: str, 
                  body_text: Optional[str] = None,
                  cc: Optional[List[str]] = None,
                  bcc: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            body_html: HTML email body
            body_text: Plain text email body (optional)
            cc: List of CC recipients (optional)
            bcc: List of BCC recipients (optional)
            
        Returns:
            Dictionary with status and details
        """
        try:
            # If using mock service, just log the email
            if self.use_mock:
                logger.info(f"MOCK EMAIL: To: {to_email}, Subject: {subject}")
                logger.info(f"MOCK EMAIL BODY: {body_text or body_html}")
                return {
                    "status": "success",
                    "message": "Email logged (mock mode)",
                    "to_email": to_email,
                    "subject": subject
                }
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add CC recipients if provided
            if cc:
                msg['Cc'] = ", ".join(cc)
                
            # Add text and HTML parts
            if body_text:
                msg.attach(MIMEText(body_text, 'plain'))
            msg.attach(MIMEText(body_html, 'html'))
            
            # Determine all recipients
            recipients = [to_email]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.sendmail(self.from_email, recipients, msg.as_string())
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return {
                "status": "success",
                "message": "Email sent",
                "to_email": to_email,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"Error sending email: {str(e)}")
            return {
                "status": "error",
                "message": f"Error sending email: {str(e)}",
                "to_email": to_email,
                "subject": subject
            }
    
    def send_reservation_notification(self, 
                                    service_name: str,
                                    date: str,
                                    time: str,
                                    customer_name: Optional[str] = None,
                                    customer_email: Optional[str] = None,
                                    location: Optional[str] = None,
                                    additional_details: Optional[str] = None) -> Dict[str, Any]:
        """
        Send a reservation notification email
        
        Args:
            service_name: Name of the service
            date: Reservation date
            time: Reservation time
            customer_name: Customer name (optional)
            customer_email: Customer email (optional)
            location: Service location (optional)
            additional_details: Additional reservation details (optional)
            
        Returns:
            Dictionary with status and details
        """
        try:
            # Set default reservation email
            to_email = "reservations@vogo.family"
            
            # Create email subject
            subject = f"New Reservation: {service_name} on {date} at {time}"
            
            # Create email body
            body_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; }}
                    .container {{ padding: 20px; }}
                    h1 {{ color: #0066cc; }}
                    .details {{ margin-top: 20px; }}
                    .footer {{ margin-top: 30px; font-size: 12px; color: #666; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>New Reservation</h1>
                    <div class="details">
                        <p><strong>Service:</strong> {service_name}</p>
                        <p><strong>Date:</strong> {date}</p>
                        <p><strong>Time:</strong> {time}</p>
                        {f"<p><strong>Customer:</strong> {customer_name}</p>" if customer_name else ""}
                        {f"<p><strong>Email:</strong> {customer_email}</p>" if customer_email else ""}
                        {f"<p><strong>Location:</strong> {location}</p>" if location else ""}
                        {f"<p><strong>Additional Details:</strong> {additional_details}</p>" if additional_details else ""}
                    </div>
                    <div class="footer">
                        <p>This is an automated message from the Vogo.Family Chatbot.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            body_text = f"""
            New Reservation
            
            Service: {service_name}
            Date: {date}
            Time: {time}
            {f"Customer: {customer_name}" if customer_name else ""}
            {f"Email: {customer_email}" if customer_email else ""}
            {f"Location: {location}" if location else ""}
            {f"Additional Details: {additional_details}" if additional_details else ""}
            
            This is an automated message from the Vogo.Family Chatbot.
            """
            
            # Send email
            return self.send_email(
                to_email=to_email,
                subject=subject,
                body_html=body_html,
                body_text=body_text,
                cc=[customer_email] if customer_email else None
            )
            
        except Exception as e:
            logger.error(f"Error sending reservation notification: {str(e)}")
            return {
                "status": "error",
                "message": f"Error sending reservation notification: {str(e)}"
            }
