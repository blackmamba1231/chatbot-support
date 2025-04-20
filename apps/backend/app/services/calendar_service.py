from typing import Dict, Any
from datetime import datetime
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/calendar']

class CalendarService:
    def __init__(self):
        self.creds = None
        self.service = None
        self.setup_credentials()

    def setup_credentials(self):
        """Setup Google Calendar API credentials"""
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not self.creds or not self.creds.valid:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            self.creds = flow.run_local_server(port=0)
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('calendar', 'v3', credentials=self.creds)

    async def add_event(self, service_details: Dict[str, Any], date: str, time: str) -> Dict[str, Any]:
        """Add a service appointment to calendar"""
        try:
            start_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            end_time = start_time.replace(hour=start_time.hour + 1)

            event = {
                'summary': f"Auto Service Appointment - {service_details['name']}",
                'location': service_details['location'],
                'description': f"Service appointment for: {service_details['description']}",
                'start': {
                    'dateTime': start_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': 'UTC',
                },
                'reminders': {
                    'useDefault': False,
                    'overrides': [
                        {'method': 'email', 'minutes': 24 * 60},
                        {'method': 'popup', 'minutes': 30},
                    ],
                },
            }

            event = self.service.events().insert(calendarId='primary', body=event).execute()
            return {
                'status': 'success',
                'event_id': event['id'],
                'html_link': event['htmlLink']
            }
        except HttpError as error:
            return {
                'status': 'error',
                'message': str(error)
            }
