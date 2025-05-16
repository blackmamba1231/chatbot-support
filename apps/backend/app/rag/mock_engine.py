from typing import Dict, Any, List, Optional, Union
import json
import os
import random
import logging
import re
from datetime import datetime, timedelta
import openai
import translators as ts
from app.services.woocommerce_service import WooCommerceService
from app.services.product_service import ProductService
from app.services.voice_service import VoiceService
from app.services.calendar_integration_service import CalendarIntegrationService
from app.services.shopping_list_service import ShoppingListService
from app.services.email_notification_service import EmailNotificationService
from app.services.ticketing_service import TicketingService
from app.rag.language_utils import detect_language, translate_text
from app.rag.shopping_list_handler import handle_shopping_list_request
from app.rag.product_search_handler import handle_product_search_query

logger = logging.getLogger(__name__)

class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

class RAGEngine:
    def __init__(self, api_key: str = None):
        """Initialize a RAG engine"""
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "demo-key")
        self.texts = []
        
        # Initialize all services
        self.wc_service = WooCommerceService()  # WooCommerce service
        self.product_service = ProductService()  # Product service with enhanced search
        self.voice_service = VoiceService()  # Voice recognition service
        self.calendar_service = CalendarIntegrationService()  # Calendar integration
        self.shopping_list_service = ShoppingListService()  # Shopping list management
        self.email_service = EmailNotificationService()  # Email notifications
        self.ticket_service = TicketingService()  # Ticketing system
        
        # Initialize OpenAI client
        try:
            logger.info(f"Initializing OpenAI client with API key: {self.api_key[:5]}...")
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            logger.error(f"API key used: {self.api_key[:5]}...")
            self.client = None
        
        # Supported languages
        self.supported_languages = {
            "en": "English",
            "ro": "Romanian",
            "fr": "French"
        }
        
        # Default language
        self.default_language = "en"
            
        self.setup_engine()

    def setup_engine(self):
        """Initialize the RAG components with data from WooCommerce"""
        try:
            # Try to sync WooCommerce data first
            try:
                self.wc_service.sync_data()
            except Exception as e:
                logger.error(f"Error syncing WooCommerce data: {e}")
            
            # Load the knowledge base
            kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", "auto_services.json")
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    kb_data = json.load(f)
            else:
                # Create a basic knowledge base structure if it doesn't exist
                kb_data = {
                    "services": [],
                    "common_issues": {
                        "brake_problems": [
                            "Squeaking or grinding noises when braking",
                            "Soft or spongy brake pedal",
                            "Vehicle pulling to one side when braking",
                            "Vibration when braking",
                            "Brake warning light on dashboard"
                        ],
                        "recommended_maintenance": {
                            "brake_pads": "Every 30,000 to 70,000 miles depending on driving conditions",
                            "brake_fluid": "Every 2 years or 30,000 miles",
                            "rotors": "Usually replaced with brake pads if worn or damaged"
                        }
                    }
                }
                
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(kb_path), exist_ok=True)
                
                # Save the knowledge base
                with open(kb_path, 'w') as f:
                    json.dump(kb_data, f, indent=2)
            
            # Prepare documents from the knowledge base
            documents = self._prepare_documents(kb_data)
            self.texts = documents
            
        except Exception as e:
            logger.error(f"Error setting up RAG engine: {e}")
            self.texts = []
    
    def _prepare_documents(self, kb_data: Dict) -> List[Document]:
        """Convert knowledge base data to Document objects"""
        documents = []
        
        for service in kb_data.get("services", []):
            content = f"Service Name: {service['name']}\n"
            content += f"Description: {service['description']}\n"
            content += f"Location: {service['location']}\n"
            content += f"Contact: {service['contact']}\n"
            content += f"Website: {service['website']}\n"
            content += f"Specialties: {', '.join(service['specialties'])}\n"
            content += f"Hours: {service['hours']}\n"
            
            doc = Document(
                page_content=content,
                metadata={"type": "service", "id": service["id"]}
            )
            documents.append(doc)
        
        if "common_issues" in kb_data:
            brake_problems = kb_data["common_issues"].get("brake_problems", [])
            if brake_problems:
                content = "Common Brake Problems:\n"
                for problem in brake_problems:
                    content += f"- {problem}\n"
                
                doc = Document(
                    page_content=content,
                    metadata={"type": "issues", "category": "brake_problems"}
                )
                documents.append(doc)
            
            recommended_maintenance = kb_data["common_issues"].get("recommended_maintenance", {})
            if recommended_maintenance:
                content = "Recommended Brake Maintenance:\n"
                for part, schedule in recommended_maintenance.items():
                    content += f"- {part.replace('_', ' ').title()}: {schedule}\n"
                
                doc = Document(
                    page_content=content,
                    metadata={"type": "maintenance", "category": "recommended_maintenance"}
                )
                documents.append(doc)
        
        return documents

    def _simple_search(self, query: str) -> List[Document]:
        """Simple keyword-based search for demo purposes"""
        results = []
        query_terms = query.lower().split()
        
        for doc in self.texts:
            content = doc.page_content.lower()
            score = sum(1 for term in query_terms if term in content)
            if score > 0:
                results.append((doc, score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [doc for doc, _ in results[:3]]
    
    def process_voice_input(self, audio_data: bytes, language: str = None) -> Dict[str, Any]:
        """Process voice input using the voice service
        
        Args:
            audio_data: Binary audio data
            language: Language code (optional)
            
        Returns:
            Dictionary with transcribed text and detected language
        """
        try:
            # Use the voice service to transcribe audio
            if not language:
                # If language not specified, default to English
                language = self.default_language
                
            transcribed_text = self.voice_service.transcribe_audio(audio_data, language)
            
            if not transcribed_text:
                return {
                    "status": "error",
                    "message": "Failed to transcribe audio",
                    "text": "",
                    "language": language
                }
                
            # Detect language if not specified
            detected_language = language
            if language == self.default_language:
                detected_language = detect_language(transcribed_text, self.default_language)
                
            return {
                "status": "success",
                "text": transcribed_text,
                "language": detected_language
            }
        except Exception as e:
            logger.error(f"Error processing voice input: {str(e)}")
            return {
                "status": "error",
                "message": f"Error processing voice input: {str(e)}",
                "text": "",
                "language": language or self.default_language
            }
    
    def _find_nearest_services(self, location: Dict[str, float] = None) -> List[Document]:
        """Find services nearest to the user's location using WooCommerce data"""
        try:
            # Get products from WooCommerce service - using the mall-delivery category that exists on the site
            products = self.wc_service.get_products(category="mall-delivery")
            
            # Convert products to Document objects
            documents = []
            for product in products:
                # Extract location information from the product name and description
                location_text = product.get('name', 'Unknown Location')
                description = product.get('short_description', '') or product.get('description', '')
                
                # Extract contact information if available
                contact = ""
                if "whatsapp" in description.lower():
                    # Try to extract phone number
                    import re
                    phone_match = re.search(r'\d{10}', description)
                    if phone_match:
                        contact = phone_match.group(0)
                
                # Create content string for the delivery service
                content = f"Service Name: Mall Delivery - {product['name']}\n"
                content += f"Description: Mall delivery service available at this location\n"
                content += f"Details: {description.strip()}\n"
                content += f"Location: {location_text}\n"
                if contact:
                    content += f"Contact: {contact}\n"
                content += f"Price: {product.get('price_html', '')}\n"
                content += f"Website: {product.get('permalink', '')}\n"
                
                # Extract specialties from tags
                specialties = [tag["name"] for tag in product.get("tags", [])]
                content += f"Specialties: {', '.join(specialties)}\n"
                
                doc = Document(
                    page_content=content,
                    metadata={"type": "service", "id": f"service_{product['id']}"}
                )
                documents.append(doc)
            
            # If we got products from WooCommerce, return those
            if documents:
                return documents
            
            # Fallback to existing documents if no products found
            return [doc for doc in self.texts if doc.metadata.get("type") == "service"]
            
        except Exception as e:
            logger.error(f"Error finding nearest services: {e}")
            # Fallback to existing documents
            return [doc for doc in self.texts if doc.metadata.get("type") == "service"]
    
    def _handle_scheduling(self, query: str, conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduling-related queries"""
        # Check if we're expecting a date or time
        if conversation_state.get("expecting") == "date":
            # User provided a date
            return {
                "response": "What time would you prefer for your appointment?",
                "confidence": 0.9,
                "requires_human": False,
                "expecting": "time",
                "date": query
            }
        elif conversation_state.get("expecting") == "time":
            # User provided a time
            return {
                "response": "Great! I'll add that to your calendar. Your appointment has been scheduled.",
                "confidence": 0.9,
                "requires_human": False,
                "action": "calendar_add",
                "time": query,
                "date": conversation_state.get("date", "tomorrow")
            }
        else:
            # Initial scheduling request
            service_docs = self._simple_search(query)
            
            if service_docs:
                service = service_docs[0]
                service_name = service.page_content.split('\n')[0].replace('Service Name: ', '')
                
                return {
                    "response": f"I'd be happy to help you schedule an appointment for {service_name}. When would you like to schedule your appointment?",
                    "confidence": 0.9,
                    "requires_human": False,
                    "expecting": "date",
                    "services": [doc.metadata.get("id") for doc in service_docs if doc.metadata.get("id")]
                }
            else:
                return {
                    "response": "I'd be happy to help you schedule an appointment. When would you like to schedule your appointment?",
                    "confidence": 0.8,
                    "requires_human": False,
                    "expecting": "date"
                }
    
    def _parse_date(self, query: str) -> str:
        """Parse date from user query"""
        query_lower = query.lower()
        
        if "today" in query_lower:
            return "today"
        elif "tomorrow" in query_lower:
            return "tomorrow"
        elif "next week" in query_lower:
            return "next week"
        elif any(day in query_lower for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
            for day in ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]:
                if day in query_lower:
                    return day.capitalize()
        
        return query
    
    def _parse_time(self, query: str) -> str:
        """Parse time from user query"""
        query_lower = query.lower()
        
        if "morning" in query_lower:
            return "9:00 AM"
        elif "afternoon" in query_lower:
            return "2:00 PM"
        elif "evening" in query_lower:
            return "5:00 PM"
        elif "am" in query_lower or "pm" in query_lower:
            return query
        
        return query
    
    def _handle_location_query(self, query: str, location: Dict[str, float] = None) -> Dict[str, Any]:
        """Handle location-based queries using real WooCommerce data"""
        # Get fresh service data from WooCommerce
        service_docs = self._find_nearest_services(location)
        
        if service_docs:
            response = "Here are the bakery service centers near you:\n\n"
            
            for i, doc in enumerate(service_docs[:3], 1):
                lines = doc.page_content.split('\n')
                name = lines[0].replace('Service Name: ', '')
                location_line = next((line for line in lines if line.startswith('Location: ')), 'Location: Not specified')
                location_text = location_line.replace('Location: ', '')
                
                response += f"{i}. {name} - {location_text}\n"
            
            return {
                "response": response,
                "confidence": 0.9,
                "requires_human": False,
                "services": [doc.metadata.get("id") for doc in service_docs if doc.metadata.get("id")]
            }
        else:
            return {
                "response": "I couldn't find any auto service centers in your area. Could you provide more information about your location?",
                "confidence": 0.7,
                "requires_human": False
            }
    
    def _handle_bread_delivery(self, query: str) -> Dict[str, Any]:
        """Handle mall delivery requests"""
        # Get mall delivery services from WooCommerce
        service_docs = self._find_nearest_services()
        
        if service_docs:
            response = "Based on your request, we offer mall delivery services from various locations. "
            response += "We can deliver products from shopping malls directly to your location. "
            response += "\n\n"
            
            response += "Here are our available mall delivery services:\n"
            for i, doc in enumerate(service_docs[:3], 1):
                lines = doc.page_content.split('\n')
                name = next((line for line in lines if line.startswith('Service Name: ')), 'Service: Not specified').replace('Service Name: ', '')
                location_line = next((line for line in lines if line.startswith('Location: ')), 'Location: Not specified')
                location_text = location_line.replace('Location: ', '')
                price_line = next((line for line in lines if line.startswith('Price: ')), 'Price: Not specified')
                price_text = price_line.replace('Price: ', '')
                
                response += f"{i}. {name} - {location_text} - {price_text}\n"
            
            return {
                "response": response,
                "confidence": 0.9,
                "requires_human": False,
                "services": [doc.metadata.get("id") for doc in service_docs if doc.metadata.get("id")]
            }
        elif self.client:  # Try to use OpenAI if available
            try:
                logger.info(f"Using OpenAI for mall delivery query: {query}")
                # Get available services
                services = self._find_nearest_services()
                services_text = "\n\n".join([doc.page_content for doc in services]) if services else ""
                
                # Prepare system message with context
                system_message = f"""You are Kodee, a helpful AI assistant for Vogo.Family mall delivery services. 
                Your role is to help customers with mall delivery services, answering questions about how the service works, 
                available malls for delivery, pricing, and other related information.
                
                Here is information about our available mall delivery services:
                {services_text}
                
                Respond in a friendly, helpful manner. Keep responses concise and focused on mall delivery services.
                If you don't know something, it's okay to say so and offer to connect the user with a human agent."""
                
                # Call OpenAI API with GPT-3.5-turbo model instead of o3-mini
                logger.info("Calling OpenAI API with GPT-3.5-turbo model for mall delivery")
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",  # Using GPT-3.5-turbo model as o3-mini is not available
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": query}
                    ],
                    temperature=0.7,
                    max_tokens=300
                )
                
                # Extract response text
                ai_response = response.choices[0].message.content.strip()
                
                return {
                    "response": ai_response,
                    "confidence": 0.9,
                    "requires_human": False,
                    "ai_powered": True
                }
            except Exception as e:
                logger.error(f"Error using OpenAI for mall delivery: {str(e)}")
                import traceback
                logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Default response if no services found and OpenAI fails
        return {
            "response": "We offer mall delivery services from various shopping centers. Would you like to know more about our available locations or how the service works?",
            "confidence": 0.7,
            "requires_human": False
        }
    
    def handle_calendar_request(self, query: str, conversation_state: Dict[str, Any] = None) -> Dict[str, Any]:
        """Handle calendar-related requests
        
        Args:
            query: User query
            conversation_state: Current conversation state
            
        Returns:
            Response with calendar action results
        """
        try:
            conversation_state = conversation_state or {}
            
            # Check for event details in the query or conversation state
            event_title = None
            event_date = None
            event_time = None
            event_location = None
            
            # Extract date if present in query
            date_result = self._parse_date(query)
            if date_result["found"]:
                event_date = date_result["date"]
            elif "date" in conversation_state:
                event_date = conversation_state["date"]
                
            # Extract time if present in query
            time_result = self._parse_time(query)
            if time_result["found"]:
                event_time = time_result["time"]
            elif "time" in conversation_state:
                event_time = conversation_state["time"]
                
            # Check for location in query (simple approach)
            location_keywords = ["in", "at", "near"]
            for keyword in location_keywords:
                if f" {keyword} " in query:
                    parts = query.split(f" {keyword} ")
                    if len(parts) > 1:
                        event_location = parts[1].split(".")[0].strip()
                        break
            
            # Check for event title in conversation state
            if "service_name" in conversation_state:
                event_title = conversation_state["service_name"]
            elif "mall_service" in conversation_state:
                event_title = f"Mall delivery from {conversation_state['mall_service']}"
                
            # If we have enough information, add the event to the calendar
            if event_title and event_date:
                result = self.calendar_service.add_event(
                    title=event_title,
                    date=event_date,
                    time=event_time,
                    location=event_location
                )
                
                # Send email notification if we have a service name
                if "service_name" in conversation_state:
                    self.email_service.send_reservation_notification(
                        service_name=conversation_state["service_name"],
                        date=event_date,
                        time=event_time or "Not specified",
                        location=event_location,
                        additional_details=f"Requested via chatbot: {query}"
                    )
                    
                if result["status"] == "success":
                    # Format the response
                    date_str = event_date
                    time_str = f" at {event_time}" if event_time else ""
                    location_str = f" in {event_location}" if event_location else ""
                    
                    response = f"I've added '{event_title}' to your calendar for {date_str}{time_str}{location_str}."
                    
                    # Clear relevant conversation state
                    if "date" in conversation_state:
                        del conversation_state["date"]
                    if "time" in conversation_state:
                        del conversation_state["time"]
                        
                    return {
                        "response": response,
                        "action": "calendar_event_added",
                        "event_details": result["event"]
                    }
                else:
                    return {
                        "response": f"I couldn't add the event to your calendar. {result.get('message', '')}",
                        "action": "calendar_event_failed"
                    }
            else:
                # We need more information
                missing = []
                if not event_title:
                    missing.append("what event you'd like to schedule")
                if not event_date:
                    missing.append("the date")
                
                missing_str = " and ".join(missing)
                return {
                    "response": f"I'd be happy to add this to your calendar. Could you please tell me {missing_str}?",
                    "action": "request_more_info",
                    "missing_info": missing
                }
                
        except Exception as e:
            logger.error(f"Error handling calendar request: {str(e)}")
            return {
                "response": "I'm having trouble processing your calendar request. Could you try again?",
                "action": "error",
                "error": str(e)
            }
    
    def _handle_human_agent_request(self, query: str) -> Dict[str, Any]:
        """Handle requests for a human agent"""
        # Create a support ticket
        ticket_result = self.ticket_service.create_ticket(
            subject="Human Agent Request",
            description=f"User requested human assistance: {query}"
        )
        
        return {
            "response": "I'll connect you with a human agent shortly. Please wait a moment.",
            "action": "transfer_to_human",
            "ticket": ticket_result.get("ticket", {})
        }

    def _get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """Get a service by ID"""
        try:
            return self.wc_service.get_service_by_id(service_id)
        except Exception as e:
            logger.error(f"Error getting service by ID: {e}")
            return None
            
    def _handle_mall_delivery_request(self, query_text: str, conversation_state: Dict) -> Optional[Dict[str, Any]]:
        """Handle mall delivery related queries"""
        query_lower = query_text.lower()
        
        # Check if this is a mall-related query
        if any(keyword in query_lower for keyword in ["mall", "shopping", "delivery", "order", "product", "browse", "available malls", "show malls"]):
            # If asking about available malls
            if any(keyword in query_lower for keyword in ["available malls", "show malls", "list malls", "what malls", "which malls"]):
                return self._get_available_malls(conversation_state)
                
            # If asking about products
            elif any(keyword in query_lower for keyword in ["products", "browse products", "show products", "what products"]):
                # If location is specified in the query
                location_match = re.search(r"in\s+([\w\s]+)", query_lower)
                location = location_match.group(1) if location_match else None
                
                # If location is in conversation state
                if not location and "selected_location" in conversation_state:
                    location = conversation_state["selected_location"]
                    
                if location:
                    return self._get_products_by_location(location, conversation_state)
                else:
                    # Ask for location
                    locations = self._get_all_locations()
                    location_options = ", ".join(locations)
                    return {
                        "response": f"Please select a location to browse products. Available locations are: {location_options}",
                        "action": "select_location",
                        "data": {"locations": locations}
                    }
            
            # If asking about restaurant services
            elif any(keyword in query_lower for keyword in ["restaurant", "food", "eat", "dining"]):
                # If location is specified in the query
                location_match = re.search(r"in\s+([\w\s]+)", query_lower)
                location = location_match.group(1) if location_match else None
                
                # If location is in conversation state
                if not location and "selected_location" in conversation_state:
                    location = conversation_state["selected_location"]
                    
                if location:
                    return self._get_restaurants_by_location(location, conversation_state)
                else:
                    # Ask for location
                    locations = self._get_all_locations()
                    location_options = ", ".join(locations)
                    return {
                        "response": f"Please select a location to browse restaurant services. Available locations are: {location_options}",
                        "action": "select_location",
                        "data": {"locations": locations}
                    }
            
        # If the query is a location name, it might be a response to our location question
        elif "waiting_for_location" in conversation_state and conversation_state["waiting_for_location"]:
            locations = self._get_all_locations()
            if any(location.lower() in query_lower for location in locations):
                # Find the matching location
                selected_location = next((location for location in locations if location.lower() in query_lower), None)
                if selected_location:
                    # Update conversation state
                    conversation_state["selected_location"] = selected_location
                    conversation_state["waiting_for_location"] = False
                    
                    # Check what we were waiting for
                    if conversation_state.get("pending_action") == "browse_products":
                        return self._get_products_by_location(selected_location, conversation_state)
                    elif conversation_state.get("pending_action") == "restaurant_services":
                        return self._get_restaurants_by_location(selected_location, conversation_state)
                    else:
                        # Default to showing products
                        return self._get_products_by_location(selected_location, conversation_state)
        
        return None
        
    def _get_available_malls(self, conversation_state: Dict) -> Dict[str, Any]:
        """Get available malls for delivery"""
        try:
            # Get all locations
            locations = self._get_all_locations()
            
            # Set conversation state
            conversation_state["waiting_for_location"] = True
            conversation_state["pending_action"] = "browse_malls"
            
            location_list = "\n".join([f"- {location}" for location in locations])
            return {
                "response": f"Here are the available malls for delivery:\n{location_list}\n\nPlease select a location to see more details.",
                "action": "show_malls",
                "data": {"locations": locations}
            }
        except Exception as e:
            logger.error(f"Error getting available malls: {e}")
            return {
                "response": "I'm sorry, I couldn't retrieve the list of available malls at the moment. Please try again later.",
                "action": None
            }
    
    def _get_all_locations(self) -> List[str]:
        """Get all available locations"""
        try:
            # Get locations from WooCommerce service
            locations = self.wc_service.get_locations()
            if not locations:
                # Fallback to hardcoded locations
                return ["Alba Iulia", "Arad", "Miercurea Ciuc", "Vaslui", "Targu Mures"]
            return locations
        except Exception as e:
            logger.error(f"Error getting locations: {e}")
            # Fallback to hardcoded locations
            return ["Alba Iulia", "Arad", "Miercurea Ciuc", "Vaslui", "Targu Mures"]
    
    def _handle_product_search(self, query: str, conversation_state: Dict) -> Dict[str, Any]:
        """
        Handle product search queries using the enhanced product search functionality.
        This method analyzes user queries to determine if they're asking about products,
        and if so, uses the enhanced product search that checks names, descriptions, slugs,
        and categories.
        
        Args:
            query: User's query text
            conversation_state: Current conversation state
            
        Returns:
            Dictionary with response and any related data if it's a product search,
            otherwise None
        """
        # Check if this is a product search query
        search_terms = ["find", "search", "show", "products", "product", "items", "mall"]
        query_lower = query.lower()
        
        # Product-specific keywords that strongly indicate a product search
        product_keywords = ["mall", "antipasti", "bio", "food", "pet", "allergy", "pizza", "shop", "buy"]
        
        # Search patterns
        search_patterns = [
            r"(find|show|search|get|give me) (\w+)( products| items)?\b",
            r"(looking for|need|want|buy) (\w+)\b",
            r"(where (can|do) i (get|find|buy)|how (can|do) i (get|order|find|buy))",
            r"(show|find) .* (from|in|at) (\w+)\b"
        ]
        
        # Check if query contains search terms or matches search patterns
        is_search_query = any(term in query_lower for term in search_terms)
        
        # Check for product-specific keywords
        has_product_keyword = any(keyword in query_lower for keyword in product_keywords)
        
        # Check for search patterns
        matches_pattern = any(re.search(pattern, query_lower) for pattern in search_patterns)
        
        if is_search_query or has_product_keyword or matches_pattern:
            # This looks like a product search query - use our enhanced search handler
            return handle_product_search_query(query, self.product_service)
            
        return None
        
    def _get_products_by_location(self, location: str, conversation_state: Dict) -> Dict[str, Any]:
        """Get products available at a specific location"""
        try:
            # Get products from WooCommerce service
            products = self.wc_service.get_mall_delivery_services(location)
            
            if not products:
                return {
                    "response": f"I couldn't find any products available in {location}. Would you like to check another location?",
                    "action": None
                }
            
            # Format product list
            product_list = "\n".join([f"- {product['name']}" for product in products[:5]])
            
            return {
                "response": f"Here are some products available in {location}:\n{product_list}\n\nYou can browse all products in the mall delivery section.",
                "action": "browse_products",
                "data": {
                    "location": location,
                    "products": products
                }
            }
        except Exception as e:
            logger.error(f"Error getting products by location: {e}")
            return {
                "response": f"I'm sorry, I couldn't retrieve the products for {location} at the moment. Please try again later.",
                "action": None
            }
    
    def _get_restaurants_by_location(self, location: str, conversation_state: Dict) -> Dict[str, Any]:
        """Get restaurant services available at a specific location"""
        try:
            # Get restaurants from WooCommerce service
            restaurants = self.wc_service.get_restaurants(location)
            
            if not restaurants:
                return {
                    "response": f"I couldn't find any restaurant services available in {location}. Would you like to check another location?",
                    "action": None
                }
            
            # Format restaurant list
            restaurant_list = "\n".join([f"- {restaurant['name']}" for restaurant in restaurants[:5]])
            
            return {
                "response": f"Here are some restaurant services available in {location}:\n{restaurant_list}\n\nYou can browse all restaurant services in the mall delivery section.",
                "action": "restaurant_services",
                "data": {
                    "location": location,
                    "restaurants": restaurants
                }
            }
        except Exception as e:
            logger.error(f"Error getting restaurants by location: {e}")
            return {
                "response": f"I'm sorry, I couldn't retrieve the restaurant services for {location} at the moment. Please try again later.",
                "action": None
            }           # Load the knowledge base
            kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", "auto_services.json")
            if os.path.exists(kb_path):
                with open(kb_path, 'r') as f:
                    kb_data = json.load(f)
            else:
                # Create a basic knowledge base structure if it doesn't exist
                kb_data = {
                    "services": [],
                    "common_issues": {
                        "brake_problems": [
                            "Squeaking or grinding noises when braking",
                            "Soft or spongy brake pedal",
                            "Vehicle pulling to one side when braking",
                            "Vibration when braking",
                            "Brake warning light on dashboard"
                        ],
                        "recommended_maintenance": {
                            "brake_pads": "Every 30,000 to 70,000 miles depending on driving conditions",
                            "brake_fluid": "Every 2 years or 30,000 miles",
                            "rotors": "Usually replaced with brake pads if worn or damaged"
                        }
                    }
                }
                
                # Create the directory if it doesn't exist
                os.makedirs(os.path.dirname(kb_path), exist_ok=True)
                
                # Save the knowledge base
                with open(kb_path, 'w') as f:
                    json.dump(kb_data, f, indent=2)
            
            # Prepare documents from the knowledge base
            documents = self._prepare_documents(kb_data)
            self.texts = documents
            
        except Exception as e:
            print(f"Error setting up RAG engine: {e}")
            self.texts = []
     
    async def process_query(self, query: str, language: str = "en", location: Dict[str, float] = None, conversation_state: Dict[str, Any] = None, audio_data: bytes = None) -> Dict[str, Any]:
        """Process a query through the RAG system
        
        Args:
            query: User query text (can be empty if audio_data is provided)
            language: Language code
            location: User location coordinates
            conversation_state: Current conversation state
            audio_data: Optional binary audio data for voice input
            
        Returns:
            Dictionary with response and any actions taken
        """
        try:
            # Default empty conversation state if none provided
            if conversation_state is None:
                conversation_state = {}
                
            # Process voice input if provided
            if audio_data and not query:
                voice_result = self.process_voice_input(audio_data, language)
                if voice_result["status"] == "success":
                    query = voice_result["text"]
                    language = voice_result["language"]
                else:
                    return {
                        "response": "I couldn't understand the audio. Could you try again?",
                        "action": "voice_processing_failed"
                    }
            
            # Detect language if not specified
            if language == self.default_language:
                detected_language = detect_language(query)
                if detected_language != language:
                    logger.info(f"Detected language '{detected_language}' differs from specified '{language}'")
                    language = detected_language
        
            # Check for mall delivery related queries
            mall_delivery_result = self._handle_mall_delivery_request(query, conversation_state)
            if mall_delivery_result:
                # Translate response if needed
                if language != "en":
                    mall_delivery_result["response"] = translate_text(mall_delivery_result["response"], "en", language)
                return mall_delivery_result
            
            # Check for shopping list related queries
            shopping_list_result = handle_shopping_list_request(query, self.shopping_list_service)
            if shopping_list_result:
                # Translate response if needed
                if language != "en":
                    shopping_list_result["response"] = translate_text(shopping_list_result["response"], "en", language)
                return shopping_list_result
                
            # Check for product search queries
            product_search_result = self._handle_product_search(query, conversation_state)
            if product_search_result:
                # Translate response if needed
                if language != "en":
                    product_search_result["response"] = translate_text(product_search_result["response"], "en", language)
                return product_search_result
            
            # Check for different query types
            query_lower = query.lower()
            
            # Human agent request
            if "human" in query_lower or "agent" in query_lower or "person" in query_lower:
                result = self._handle_human_agent_request(query)
                # Translate response back if needed
                if language != "en":
                    result["response"] = translate_text(result["response"], "en", language)
                return result
            
            # Calendar request
            elif "calendar" in query_lower or "schedule" in query_lower or "appointment" in query_lower or "remind" in query_lower:
                result = self.handle_calendar_request(query, conversation_state)
                # Translate response back if needed
                if language != "en":
                    result["response"] = translate_text(result["response"], "en", language)
                return result
            
            # Mall delivery query
            elif "mall" in query_lower or "delivery" in query_lower or "shopping" in query_lower:
                result = self._handle_bread_delivery(query)
                # Translate response back if needed
                if language != "en":
                    result["response"] = translate_text(result["response"], "en", language)
                return result
            
            # Location-based query
            elif "location" in query_lower or "near" in query_lower or "mall" in query_lower:
                result = self._handle_location_query(query, location)
                # Translate response back if needed
                if language != "en":
                    result["response"] = translate_text(result["response"], "en", language)
                return result
            
            # Try to find relevant documents
            docs = self._simple_search(query)
            
            if docs:
                response = docs[0].page_content
                # Translate response back if needed
                if language != "en":
                    response = translate_text(response, "en", language)
                return {
                    "response": response,
                    "confidence": 0.8,
                    "requires_human": False
                }
            
            # Scheduling query
            elif "schedule" in query_lower or "appointment" in query_lower or "book" in query_lower:
                return self._handle_scheduling(query, conversation_state)
            
            # Date response (after being asked when)
            elif any(term in query_lower for term in ["today", "tomorrow", "next week", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]):
                return {
                    "response": "What time would you prefer for your appointment?",
                    "confidence": 0.9,
                    "requires_human": False,
                    "expecting": "time",
                    "date": query
                }
            
            # Time response (after being asked what time)
            elif "am" in query_lower or "pm" in query_lower or any(str(hour) in query for hour in range(1, 13)):
                return {
                    "response": "Great! I'll add that to your calendar. Your appointment has been scheduled.",
                    "confidence": 0.9,
                    "requires_human": False,
                    "action": "calendar_add",
                    "time": query
                }
            
            # Use AI for unrecognized queries
            else:
                # Try to use OpenAI if available
                logger.info(f"Processing query with OpenAI: {query[:30]}...")
                logger.info(f"OpenAI client available: {self.client is not None}")
                if self.client:
                    try:
                        # Get relevant documents based on the query
                        relevant_docs = self._simple_search(query)
                        context = "\n\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
                        
                        # Get available services
                        services = self._find_nearest_services(location)
                        services_text = "\n\n".join([doc.page_content for doc in services]) if services else ""
                        
                        # Prepare system message with context
                        system_message = f"""You are Kodee, a helpful AI assistant for Vogo.Family mall delivery services. 
                        Your role is to help customers with mall delivery services, answering questions about how the service works, 
                        available malls for delivery, pricing, and other related information.
                        
                        Here is information about our available mall delivery services:
                        {services_text}
                        
                        Additional context that might be helpful:
                        {context}
                        
                        Respond in a friendly, helpful manner. Keep responses concise and focused on mall delivery services.
                        If you don't know something, it's okay to say so and offer to connect the user with a human agent."""
                        
                        # Call OpenAI API with O3 mini model
                        logger.info("Calling OpenAI API with O3 mini model")
                        response = self.client.chat.completions.create(
                            model="o3-mini",  # Using O3 mini model
                            messages=[
                                {"role": "system", "content": system_message},
                                {"role": "user", "content": query}
                            ],
                            temperature=0.7,
                            max_tokens=300
                        )
                        logger.info(f"OpenAI API response received: {str(response)[:100]}...")
                        
                        # Extract response text
                        ai_response = response.choices[0].message.content.strip()
                        
                        return {
                            "response": ai_response,
                            "confidence": 0.9,  # Higher confidence for AI-generated responses
                            "requires_human": False,
                            "ai_powered": True  # Flag to indicate this was AI-generated
                        }
                    except Exception as e:
                        logger.error(f"Error using OpenAI: {str(e)}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        # Fall back to default response
                
                # Default fallback response if OpenAI fails or is not available
                return {
                    "response": "I'm here to help with mall delivery services. Would you like to know about our available malls, how the service works, or pricing information?",
                    "confidence": 0.7,
                    "requires_human": False
                }
        except Exception as e:
            print(f"Error processing query: {e}")
            return {
                "response": "I'm having trouble processing your request. Could you try again or rephrase your question?",
                "confidence": 0.3,
                "requires_human": True
            }
