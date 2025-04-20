import os
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

class LocalTicketService:
    def __init__(self):
        """Initialize the local ticket service"""
        # Create the tickets directory if it doesn't exist
        self.tickets_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "tickets")
        os.makedirs(self.tickets_dir, exist_ok=True)
        
        # Path to the tickets database file
        self.tickets_db_path = os.path.join(self.tickets_dir, "tickets.json")
        
        # Initialize the tickets database if it doesn't exist
        if not os.path.exists(self.tickets_db_path):
            with open(self.tickets_db_path, 'w') as f:
                json.dump({"tickets": []}, f)
    
    def _load_tickets(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load tickets from the database file"""
        try:
            with open(self.tickets_db_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # If the file doesn't exist or is corrupted, create a new one
            tickets_data = {"tickets": []}
            with open(self.tickets_db_path, 'w') as f:
                json.dump(tickets_data, f)
            return tickets_data
    
    def _save_tickets(self, tickets_data: Dict[str, List[Dict[str, Any]]]) -> None:
        """Save tickets to the database file"""
        with open(self.tickets_db_path, 'w') as f:
            json.dump(tickets_data, f, indent=2)
    
    async def create_ticket(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ticket"""
        tickets_data = self._load_tickets()
        
        # Generate a unique ticket ID
        ticket_id = str(uuid.uuid4())
        
        # Create the ticket object
        ticket = {
            "id": ticket_id,
            "status": "open",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "assigned_to": None,
            "data": data
        }
        
        # Add the ticket to the database
        tickets_data["tickets"].append(ticket)
        self._save_tickets(tickets_data)
        
        return {
            "status": "success",
            "message": "Ticket created successfully",
            "ticket_id": ticket_id
        }
    
    async def get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Get a ticket by ID"""
        tickets_data = self._load_tickets()
        
        for ticket in tickets_data["tickets"]:
            if ticket["id"] == ticket_id:
                return ticket
        
        return None
    
    async def update_ticket(self, ticket_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a ticket"""
        tickets_data = self._load_tickets()
        
        for i, ticket in enumerate(tickets_data["tickets"]):
            if ticket["id"] == ticket_id:
                # Update the ticket
                for key, value in updates.items():
                    if key != "id" and key != "created_at":
                        ticket[key] = value
                
                # Update the updated_at timestamp
                ticket["updated_at"] = datetime.now().isoformat()
                
                # Save the changes
                tickets_data["tickets"][i] = ticket
                self._save_tickets(tickets_data)
                
                return {
                    "status": "success",
                    "message": "Ticket updated successfully",
                    "ticket": ticket
                }
        
        return {
            "status": "error",
            "message": f"Ticket with ID {ticket_id} not found"
        }
    
    async def assign_to_human_operator(self, ticket_id: str) -> Dict[str, Any]:
        """Assign a ticket to a human operator"""
        # In a real system, this would involve finding an available operator
        # For this demo, we'll just mark it as assigned
        
        return await self.update_ticket(ticket_id, {
            "status": "assigned",
            "assigned_to": "human_operator"
        })
    
    async def get_all_tickets(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all tickets, optionally filtered by status"""
        tickets_data = self._load_tickets()
        
        if status:
            return [ticket for ticket in tickets_data["tickets"] if ticket["status"] == status]
        else:
            return tickets_data["tickets"]
    
    async def close_ticket(self, ticket_id: str, resolution: str) -> Dict[str, Any]:
        """Close a ticket with a resolution"""
        return await self.update_ticket(ticket_id, {
            "status": "closed",
            "resolution": resolution,
            "closed_at": datetime.now().isoformat()
        })
