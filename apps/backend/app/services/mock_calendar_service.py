import os
import json
from typing import Dict, Any
from datetime import datetime, timedelta
import uuid

class CalendarService:
    def __init__(self):
        """Initialize a mock calendar service"""
        # Create the calendar directory if it doesn't exist
        self.calendar_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "calendar")
        os.makedirs(self.calendar_dir, exist_ok=True)
        
        # Path to the calendar database file
        self.calendar_db_path = os.path.join(self.calendar_dir, "events.json")
        
        # Initialize the calendar database if it doesn't exist
        if not os.path.exists(self.calendar_db_path):
            with open(self.calendar_db_path, 'w') as f:
                json.dump({"events": []}, f)
    
    def _load_events(self) -> Dict[str, Any]:
        """Load events from the database file"""
        try:
            with open(self.calendar_db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is corrupted, create a new one
            events_data = {"events": []}
            with open(self.calendar_db_path, 'w') as f:
                json.dump(events_data, f)
            return events_data
    
    def _save_events(self, events_data: Dict[str, Any]) -> None:
        """Save events to the database file"""
        with open(self.calendar_db_path, 'w') as f:
            json.dump(events_data, f, indent=2)
    
    async def add_event(self, service_details: Dict[str, Any], date: str, time: str) -> Dict[str, Any]:
        """Add a new event to the calendar"""
        events_data = self._load_events()
        
        # Generate a unique event ID
        event_id = str(uuid.uuid4())
        
        # Parse date and time
        try:
            # Simple parsing for demo purposes
            event_datetime = datetime.now() + timedelta(days=1)  # Default to tomorrow
            
            if "tomorrow" in date.lower():
                event_datetime = datetime.now() + timedelta(days=1)
            elif "next week" in date.lower():
                event_datetime = datetime.now() + timedelta(days=7)
            
            # Create the event object
            event = {
                "id": event_id,
                "title": f"Service: {service_details.get('name', 'Auto Service')}",
                "description": service_details.get('description', ''),
                "location": service_details.get('location', ''),
                "date": date,
                "time": time,
                "created_at": datetime.now().isoformat(),
                "service_details": service_details
            }
            
            # Add the event to the database
            events_data["events"].append(event)
            self._save_events(events_data)
            
            return {
                "status": "success",
                "message": "Event added to calendar successfully",
                "event_id": event_id,
                "event": event
            }
            
        except Exception as e:
            print(f"Error adding event: {e}")
            return {
                "status": "error",
                "message": f"Failed to add event: {str(e)}"
            }
    
    async def get_events(self, start_date: str = None, end_date: str = None) -> Dict[str, Any]:
        """Get events from the calendar, optionally filtered by date range"""
        events_data = self._load_events()
        
        # For demo purposes, we'll just return all events
        return {
            "status": "success",
            "events": events_data["events"]
        }
    
    async def get_event(self, event_id: str) -> Dict[str, Any]:
        """Get a specific event by ID"""
        events_data = self._load_events()
        
        for event in events_data["events"]:
            if event["id"] == event_id:
                return {
                    "status": "success",
                    "event": event
                }
        
        return {
            "status": "error",
            "message": f"Event with ID {event_id} not found"
        }
    
    async def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an event"""
        events_data = self._load_events()
        
        for i, event in enumerate(events_data["events"]):
            if event["id"] == event_id:
                # Update the event
                for key, value in updates.items():
                    event[key] = value
                
                # Save the changes
                events_data["events"][i] = event
                self._save_events(events_data)
                
                return {
                    "status": "success",
                    "message": "Event updated successfully",
                    "event": event
                }
        
        return {
            "status": "error",
            "message": f"Event with ID {event_id} not found"
        }
    
    async def delete_event(self, event_id: str) -> Dict[str, Any]:
        """Delete an event"""
        events_data = self._load_events()
        
        for i, event in enumerate(events_data["events"]):
            if event["id"] == event_id:
                # Remove the event
                del events_data["events"][i]
                self._save_events(events_data)
                
                return {
                    "status": "success",
                    "message": "Event deleted successfully"
                }
        
        return {
            "status": "error",
            "message": f"Event with ID {event_id} not found"
        }
