import os
import logging
import datetime
from typing import Dict, Any, Optional, List
import requests
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

logger = logging.getLogger(__name__)

class CalendarIntegrationService:
    """Service for integrating with calendar systems"""
    
    def __init__(self):
        """Initialize the calendar integration service"""
        self.api_url = os.environ.get("CALENDAR_API_URL", "")
        self.api_key = os.environ.get("CALENDAR_API_KEY", "")
        
        # Google Calendar API credentials path
        self.credentials_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "credentials",
            "credentials.json"
        )
        
        # Google Calendar API token path
        self.token_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "credentials",
            "token.json"
        )
        
        # Google Calendar API scopes
        self.scopes = ['https://www.googleapis.com/auth/calendar']
        
        # Google Calendar service
        self.service = None
        
        # For testing, we'll use mock data instead of real Google Calendar
        self.use_mock = True
        logger.info("Using mock calendar service for testing")
        
        # Only try to initialize Google Calendar if not using mock
        if not self.use_mock:
            try:
                self._init_google_calendar()
            except Exception as e:
                logger.error(f"Error initializing Google Calendar service: {str(e)}")
                self.use_mock = True
        
        # For demo purposes, we'll use a local file to store events
        self.events_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "knowledge_base", 
            "calendar_events.json"
        )
        
        # Create events file if it doesn't exist
        if not os.path.exists(self.events_file):
            with open(self.events_file, 'w') as f:
                json.dump({"events": []}, f)
                
    def _init_google_calendar(self):
        """Initialize Google Calendar API service"""
        creds = None
        
        # Check if token.json exists
        if os.path.exists(self.token_path):
            try:
                creds = Credentials.from_authorized_user_info(
                    json.load(open(self.token_path, 'r')),
                    self.scopes
                )
            except Exception as e:
                logger.error(f"Error loading credentials from token file: {str(e)}")
                creds = None
        
        # If there are no valid credentials, let the user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    logger.error(f"Error refreshing credentials: {str(e)}")
                    creds = None
            
            # If still no valid credentials, flow through the OAuth process
            if not creds:
                if os.path.exists(self.credentials_path):
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_path, self.scopes
                        )
                        creds = flow.run_local_server(port=0)
                        
                        # Save the credentials for the next run
                        with open(self.token_path, 'w') as token:
                            token.write(creds.to_json())
                    except Exception as e:
                        logger.error(f"Error in OAuth flow: {str(e)}")
                        creds = None
                else:
                    logger.warning(f"Credentials file not found at {self.credentials_path}")
                    return
        
        # Build the Google Calendar service
        if creds:
            try:
                self.service = build('calendar', 'v3', credentials=creds)
                logger.info("Google Calendar API service initialized successfully")
            except Exception as e:
                logger.error(f"Error building Google Calendar service: {str(e)}")
                self.service = None
    
    def add_event(self, 
                  title: str, 
                  date: str, 
                  time: Optional[str] = None, 
                  location: Optional[str] = None, 
                  description: Optional[str] = None) -> Dict[str, Any]:
        """
        Add an event to the calendar
        
        Args:
            title: Event title
            date: Event date (in format YYYY-MM-DD)
            time: Event time (optional)
            location: Event location (optional)
            description: Event description (optional)
            
        Returns:
            Dictionary with event details and status
        """
        try:
            # Create event object for local storage
            event = {
                "id": f"event_{datetime.datetime.now().timestamp()}",
                "title": title,
                "date": date,
                "time": time,
                "location": location,
                "description": description,
                "created_at": datetime.datetime.now().isoformat()
            }
            
            # Try to use Google Calendar API if available and not in mock mode
            if self.service and not self.use_mock:
                try:
                    # Parse date and time
                    start_datetime = date
                    end_datetime = date
                    
                    if time:
                        # Convert time to datetime format
                        start_datetime = f"{date}T{time}:00"
                        # Default event duration: 1 hour
                        hour, minute = time.split(":")
                        hour = int(hour) + 1
                        if hour >= 24:
                            hour = 23
                            minute = 59
                        end_datetime = f"{date}T{hour:02d}:{minute}:00"
                    else:
                        # All-day event
                        start_datetime = date
                        # Parse date to add one day for end date (exclusive)
                        year, month, day = map(int, date.split("-"))
                        end_date = datetime.date(year, month, day) + datetime.timedelta(days=1)
                        end_datetime = end_date.isoformat()
                    
                    # Create Google Calendar event
                    google_event = {
                        'summary': title,
                        'location': location or '',
                        'description': description or '',
                        'start': {
                            'dateTime': start_datetime if time else None,
                            'date': start_datetime if not time else None,
                            'timeZone': 'UTC',
                        },
                        'end': {
                            'dateTime': end_datetime if time else None,
                            'date': end_datetime if not time else None,
                            'timeZone': 'UTC',
                        },
                        'reminders': {
                            'useDefault': True,
                        },
                    }
                    
                    # Remove None values
                    if 'dateTime' in google_event['start'] and google_event['start']['dateTime'] is None:
                        del google_event['start']['dateTime']
                    if 'date' in google_event['start'] and google_event['start']['date'] is None:
                        del google_event['start']['date']
                    if 'dateTime' in google_event['end'] and google_event['end']['dateTime'] is None:
                        del google_event['end']['dateTime']
                    if 'date' in google_event['end'] and google_event['end']['date'] is None:
                        del google_event['end']['date']
                    
                    # Add event to Google Calendar
                    google_result = self.service.events().insert(calendarId='primary', body=google_event).execute()
                    
                    # Update local event with Google Calendar event ID
                    event['google_calendar_id'] = google_result.get('id')
                    
                    logger.info(f"Event added to Google Calendar: {title}")
                    
                    # Also store event locally as backup
                    self._store_event_locally(event)
                    
                    return {
                        "status": "success",
                        "message": "Event added to Google Calendar",
                        "event": event,
                        "google_event_id": google_result.get('id'),
                        "google_event_link": google_result.get('htmlLink')
                    }
                    
                except Exception as e:
                    logger.error(f"Error adding event to Google Calendar: {str(e)}")
                    # Fall back to other methods
            
            # If Google Calendar failed or not available, try external API
            if self.api_url and self.api_key:
                try:
                    response = requests.post(
                        f"{self.api_url}/events",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        json=event
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Event added to external calendar API: {title}")
                        return {
                            "status": "success",
                            "message": "Event added to calendar",
                            "event": event
                        }
                    else:
                        logger.error(f"Error adding event to external calendar: {response.text}")
                        # Fall back to local storage
                except Exception as e:
                    logger.error(f"Error connecting to external calendar API: {str(e)}")
                    # Fall back to local storage
            
            # If all else fails, store event locally
            return self._store_event_locally(event)
                
        except Exception as e:
            logger.error(f"Error in add_event: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding event to calendar: {str(e)}"
            }
            
    def _store_event_locally(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Store an event in the local JSON file
        
        Args:
            event: Event object to store
            
        Returns:
            Dictionary with status and event details
        """
        try:
            with open(self.events_file, 'r') as f:
                data = json.load(f)
            
            data["events"].append(event)
            
            with open(self.events_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Event added to local calendar: {event.get('title')}")
            return {
                "status": "success",
                "message": "Event added to calendar",
                "event": event
            }
        except Exception as e:
            logger.error(f"Error adding event to local calendar: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding event to calendar: {str(e)}",
                "event": event
            }
    
    def get_events(self, date: Optional[str] = None) -> Dict[str, Any]:
        """
        Get events from the calendar
        
        Args:
            date: Optional date filter (in format YYYY-MM-DD)
            
        Returns:
            Dictionary with events
        """
        try:
            # If API URL and key are provided, try to use external API
            if self.api_url and self.api_key:
                try:
                    params = {}
                    if date:
                        params["date"] = date
                        
                    response = requests.get(
                        f"{self.api_url}/events",
                        headers={"Authorization": f"Bearer {self.api_key}"},
                        params=params
                    )
                    
                    if response.status_code == 200:
                        return {
                            "status": "success",
                            "events": response.json()["events"]
                        }
                    else:
                        logger.error(f"Error getting events from external calendar: {response.text}")
                        # Fall back to local storage
                except Exception as e:
                    logger.error(f"Error connecting to external calendar API: {str(e)}")
                    # Fall back to local storage
            
            # Get events from local storage
            try:
                with open(self.events_file, 'r') as f:
                    data = json.load(f)
                
                events = data["events"]
                
                # Filter by date if provided
                if date:
                    events = [event for event in events if event["date"] == date]
                
                return {
                    "status": "success",
                    "events": events
                }
            except Exception as e:
                logger.error(f"Error getting events from local calendar: {str(e)}")
                return {
                    "status": "error",
                    "message": f"Error getting events from calendar: {str(e)}",
                    "events": []
                }
                
        except Exception as e:
            logger.error(f"Error in get_events: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting events from calendar: {str(e)}",
                "events": []
            }
