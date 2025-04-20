from typing import Dict, Any
import httpx
import os
from datetime import datetime

class TicketService:
    def __init__(self):
        self.api_key = os.getenv("TICKET_SYSTEM_API_KEY", "")
        self.api_url = os.getenv("TICKET_SYSTEM_URL", "https://api.vogo.family/tickets")

    async def create_ticket(self, booking_details: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ticket in the ticketing system"""
        try:
            ticket_data = {
                "type": "service_booking",
                "status": "new",
                "priority": "normal",
                "subject": f"Service Booking - {booking_details['service_name']}",
                "description": f"""
                    Service: {booking_details['service_name']}
                    Date: {booking_details['date']}
                    Time: {booking_details['time']}
                    Location: {booking_details['location']}
                    Issue: {booking_details['issue']}
                    
                    Customer Contact: {booking_details.get('customer_contact', 'Not provided')}
                """,
                "created_at": datetime.utcnow().isoformat(),
                "metadata": {
                    "source": "chatbot",
                    "booking_details": booking_details
                }
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json=ticket_data,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                ticket = response.json()

            return {
                'status': 'success',
                'ticket_id': ticket['id'],
                'ticket_url': ticket['url']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }

    async def assign_to_human_operator(self, ticket_id: str) -> Dict[str, Any]:
        """Assign ticket to human operator queue"""
        try:
            update_data = {
                "status": "assigned",
                "queue": "human_operator",
                "updated_at": datetime.utcnow().isoformat()
            }

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.api_url}/{ticket_id}",
                    json=update_data,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                ticket = response.json()

            return {
                'status': 'success',
                'ticket_id': ticket['id'],
                'assigned_to': ticket['assigned_to']
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }
