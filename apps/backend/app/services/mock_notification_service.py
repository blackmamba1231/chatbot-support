import os
import json
from typing import Dict, Any, List
from datetime import datetime
import uuid

class NotificationService:
    def __init__(self):
        """Initialize a mock notification service"""
        # Create the notifications directory if it doesn't exist
        self.notifications_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "notifications")
        os.makedirs(self.notifications_dir, exist_ok=True)
        
        # Path to the notifications database file
        self.notifications_db_path = os.path.join(self.notifications_dir, "notifications.json")
        
        # Initialize the notifications database if it doesn't exist
        if not os.path.exists(self.notifications_db_path):
            with open(self.notifications_db_path, 'w') as f:
                json.dump({"notifications": []}, f)
    
    def _load_notifications(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load notifications from the database file"""
        try:
            with open(self.notifications_db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is corrupted, create a new one
            notifications_data = {"notifications": []}
            with open(self.notifications_db_path, 'w') as f:
                json.dump(notifications_data, f)
            return notifications_data
    
    def _save_notifications(self, notifications_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save notifications to the database file"""
        with open(self.notifications_db_path, 'w') as f:
            json.dump(notifications_data, f, indent=2)
    
    async def send_booking_confirmation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a booking confirmation notification"""
        notifications_data = self._load_notifications()
        
        # Generate a unique notification ID
        notification_id = str(uuid.uuid4())
        
        # Create the notification object
        notification = {
            "id": notification_id,
            "type": "booking_confirmation",
            "status": "sent",
            "created_at": datetime.now().isoformat(),
            "data": data,
            "message": f"Your appointment for {data.get('service_name', 'Auto Service')} has been confirmed for {data.get('date', 'the requested date')} at {data.get('time', 'the requested time')}."
        }
        
        # Add the notification to the database
        notifications_data["notifications"].append(notification)
        self._save_notifications(notifications_data)
        
        return {
            "status": "success",
            "message": "Booking confirmation sent successfully",
            "notification_id": notification_id
        }
    
    async def send_reminder(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Send a reminder notification"""
        notifications_data = self._load_notifications()
        
        # Generate a unique notification ID
        notification_id = str(uuid.uuid4())
        
        # Create the notification object
        notification = {
            "id": notification_id,
            "type": "reminder",
            "status": "sent",
            "created_at": datetime.now().isoformat(),
            "data": data,
            "message": f"Reminder: Your appointment for {data.get('service_name', 'Auto Service')} is scheduled for {data.get('date', 'the requested date')} at {data.get('time', 'the requested time')}."
        }
        
        # Add the notification to the database
        notifications_data["notifications"].append(notification)
        self._save_notifications(notifications_data)
        
        return {
            "status": "success",
            "message": "Reminder sent successfully",
            "notification_id": notification_id
        }
    
    async def get_notifications(self) -> Dict[str, Any]:
        """Get all notifications"""
        notifications_data = self._load_notifications()
        
        return {
            "status": "success",
            "notifications": notifications_data["notifications"]
        }
    
    async def get_notification(self, notification_id: str) -> Dict[str, Any]:
        """Get a specific notification by ID"""
        notifications_data = self._load_notifications()
        
        for notification in notifications_data["notifications"]:
            if notification["id"] == notification_id:
                return {
                    "status": "success",
                    "notification": notification
                }
        
        return {
            "status": "error",
            "message": f"Notification with ID {notification_id} not found"
        }
