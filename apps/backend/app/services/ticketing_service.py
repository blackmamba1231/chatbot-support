import os
import logging
import datetime
import json
import uuid
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class TicketingService:
    """Service for managing support tickets"""
    
    def __init__(self):
        """Initialize the ticketing service"""
        # For demo purposes, we'll use a local file to store tickets
        self.tickets_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "knowledge_base", 
            "support_tickets.json"
        )
        
        # Create tickets file if it doesn't exist
        if not os.path.exists(self.tickets_file):
            with open(self.tickets_file, 'w') as f:
                json.dump({"tickets": []}, f)
    
    def create_ticket(self, 
                     subject: str, 
                     description: str, 
                     customer_name: Optional[str] = None,
                     customer_email: Optional[str] = None,
                     priority: str = "medium",
                     category: Optional[str] = None,
                     conversation_history: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a new support ticket
        
        Args:
            subject: Ticket subject
            description: Ticket description
            customer_name: Customer name (optional)
            customer_email: Customer email (optional)
            priority: Ticket priority (default: "medium")
            category: Ticket category (optional)
            conversation_history: Chat conversation history (optional)
            
        Returns:
            Dictionary with ticket details and status
        """
        try:
            # Generate ticket ID
            ticket_id = f"TICKET-{uuid.uuid4().hex[:8].upper()}"
            
            # Create ticket object
            ticket = {
                "id": ticket_id,
                "subject": subject,
                "description": description,
                "customer_name": customer_name,
                "customer_email": customer_email,
                "priority": priority,
                "category": category,
                "status": "open",
                "created_at": datetime.datetime.now().isoformat(),
                "updated_at": datetime.datetime.now().isoformat(),
                "conversation_history": conversation_history or [],
                "notes": [],
                "assigned_to": None
            }
            
            # Load existing tickets
            with open(self.tickets_file, 'r') as f:
                data = json.load(f)
            
            # Add new ticket
            data["tickets"].append(ticket)
            
            # Save tickets
            with open(self.tickets_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Created ticket {ticket_id}: {subject}")
            return {
                "status": "success",
                "message": "Ticket created successfully",
                "ticket": ticket
            }
            
        except Exception as e:
            logger.error(f"Error creating ticket: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating ticket: {str(e)}"
            }
    
    def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """
        Get a ticket by ID
        
        Args:
            ticket_id: Ticket ID
            
        Returns:
            Dictionary with ticket details and status
        """
        try:
            # Load tickets
            with open(self.tickets_file, 'r') as f:
                data = json.load(f)
            
            # Find ticket
            for ticket in data["tickets"]:
                if ticket["id"] == ticket_id:
                    logger.info(f"Retrieved ticket {ticket_id}")
                    return {
                        "status": "success",
                        "ticket": ticket
                    }
            
            logger.warning(f"Ticket {ticket_id} not found")
            return {
                "status": "error",
                "message": f"Ticket {ticket_id} not found"
            }
            
        except Exception as e:
            logger.error(f"Error getting ticket: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting ticket: {str(e)}"
            }
    
    def update_ticket_status(self, ticket_id: str, status: str) -> Dict[str, Any]:
        """
        Update a ticket's status
        
        Args:
            ticket_id: Ticket ID
            status: New status
            
        Returns:
            Dictionary with status and details
        """
        try:
            # Load tickets
            with open(self.tickets_file, 'r') as f:
                data = json.load(f)
            
            # Find and update ticket
            ticket_found = False
            for ticket in data["tickets"]:
                if ticket["id"] == ticket_id:
                    ticket["status"] = status
                    ticket["updated_at"] = datetime.datetime.now().isoformat()
                    ticket_found = True
                    break
            
            if not ticket_found:
                logger.warning(f"Ticket {ticket_id} not found")
                return {
                    "status": "error",
                    "message": f"Ticket {ticket_id} not found"
                }
            
            # Save tickets
            with open(self.tickets_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Updated ticket {ticket_id} status to {status}")
            return {
                "status": "success",
                "message": f"Ticket status updated to {status}",
                "ticket_id": ticket_id
            }
            
        except Exception as e:
            logger.error(f"Error updating ticket status: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating ticket status: {str(e)}"
            }
    
    def add_note_to_ticket(self, ticket_id: str, note: str, author: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a note to a ticket
        
        Args:
            ticket_id: Ticket ID
            note: Note content
            author: Note author (optional)
            
        Returns:
            Dictionary with status and details
        """
        try:
            # Load tickets
            with open(self.tickets_file, 'r') as f:
                data = json.load(f)
            
            # Find ticket and add note
            ticket_found = False
            for ticket in data["tickets"]:
                if ticket["id"] == ticket_id:
                    note_obj = {
                        "id": f"note_{uuid.uuid4().hex[:8]}",
                        "content": note,
                        "author": author,
                        "created_at": datetime.datetime.now().isoformat()
                    }
                    
                    if "notes" not in ticket:
                        ticket["notes"] = []
                        
                    ticket["notes"].append(note_obj)
                    ticket["updated_at"] = datetime.datetime.now().isoformat()
                    ticket_found = True
                    break
            
            if not ticket_found:
                logger.warning(f"Ticket {ticket_id} not found")
                return {
                    "status": "error",
                    "message": f"Ticket {ticket_id} not found"
                }
            
            # Save tickets
            with open(self.tickets_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Added note to ticket {ticket_id}")
            return {
                "status": "success",
                "message": "Note added to ticket",
                "ticket_id": ticket_id
            }
            
        except Exception as e:
            logger.error(f"Error adding note to ticket: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding note to ticket: {str(e)}"
            }
    
    def get_all_tickets(self, status: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all tickets, optionally filtered by status
        
        Args:
            status: Filter tickets by status (optional)
            
        Returns:
            Dictionary with tickets and status
        """
        try:
            # Load tickets
            with open(self.tickets_file, 'r') as f:
                data = json.load(f)
            
            tickets = data["tickets"]
            
            # Filter by status if provided
            if status:
                tickets = [ticket for ticket in tickets if ticket["status"] == status]
            
            logger.info(f"Retrieved {len(tickets)} tickets")
            return {
                "status": "success",
                "tickets": tickets
            }
            
        except Exception as e:
            logger.error(f"Error getting tickets: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting tickets: {str(e)}",
                "tickets": []
            }
