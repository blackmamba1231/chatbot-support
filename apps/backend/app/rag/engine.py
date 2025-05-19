<<<<<<< HEAD
from typing import Dict, Any
from langchain.llms import OpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA

class RAGEngine:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.llm = None
        self.qa_chain = None
=======
from typing import Dict, Any, List, Optional
import json
import os
import random
from datetime import datetime, timedelta
from app.services.woocommerce_service import WooCommerceService

class Document:
    def __init__(self, page_content, metadata=None):
        self.page_content = page_content
        self.metadata = metadata or {}

class RAGEngine:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "demo-key")
        self.llm = None
        self.qa_chain = None
        self.vector_store = None
        self.texts = []
        self.wc_service = WooCommerceService()
>>>>>>> 9c26091 (backend try)
        self.setup_engine()

    def setup_engine(self):
        """Initialize the RAG components"""
<<<<<<< HEAD
        # TODO: Implement full RAG setup
        # This is a placeholder for the initial milestone
        self.llm = OpenAI(api_key=self.api_key)

    async def process_query(self, query: str, language: str = "en") -> Dict[Any, Any]:
        """Process a query through the RAG system"""
        # TODO: Implement full query processing
        # This is a placeholder for the initial milestone
        return {
            "response": "RAG system is being implemented",
            "confidence": 0.5,
            "requires_human": False
        }
=======
        try:
            # Sync the knowledge base with the latest data from WooCommerce
            self.wc_service.sync_knowledge_base()
            
            # Load the synced knowledge base
            kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "knowledge_base", "auto_services.json")
            with open(kb_path, 'r') as f:
                kb_data = json.load(f)
            
            documents = self._prepare_documents(kb_data)
            
            self.texts = documents
            
        except Exception as e:
            print(f"Error setting up RAG engine: {e}")
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
    
    def _find_nearest_services(self, location: Dict[str, float] = None) -> List[Document]:
        """Find services nearest to the user's location"""
        # Get fresh data from WooCommerce
        self.wc_service.sync_knowledge_base()
        
        # In a real implementation, this would use geospatial calculations
        # For demo purposes, we'll just return all services
        return [doc for doc in self.texts if doc.metadata.get("type") == "service"]
    
    def _handle_scheduling(self, query: str, conversation_state: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scheduling-related queries"""
        # Check if we're expecting a date
        if conversation_state.get("expecting") == "date":
            # Parse the date from the query
            date = self._parse_date(query)
            return {
                "response": f"Great! I've noted {date}. What time would you prefer for your appointment?",
                "confidence": 0.9,
                "requires_human": False,
                "expecting": "time",
                "date": date
            }
        
        # Check if we're expecting a time
        elif conversation_state.get("expecting") == "time":
            # Parse the time from the query
            time = self._parse_time(query)
            date = conversation_state.get("date", "the specified date")
            
            return {
                "response": f"Perfect! I'll schedule your appointment for {date} at {time}. I'll add this to your calendar and send a confirmation email.",
                "confidence": 0.9,
                "requires_human": False,
                "action": "calendar_add",
                "time": time
            }
        
        # Initial scheduling request
        else:
            return {
                "response": "I can help you schedule an appointment. When would you like to schedule it?",
                "confidence": 0.9,
                "requires_human": False,
                "expecting": "date"
            }
    
    def _parse_date(self, query: str) -> str:
        """Parse date from user query"""
        query = query.lower()
        today = datetime.now()
        
        if "today" in query:
            return "today"
        elif "tomorrow" in query:
            return "tomorrow"
        elif "next week" in query:
            return (today + timedelta(days=7)).strftime("%A, %B %d")
        elif "day after tomorrow" in query:
            return (today + timedelta(days=2)).strftime("%A, %B %d")
        else:
            # Try to extract a date if mentioned
            # For simplicity, we'll just return the query
            return query
    
    def _parse_time(self, query: str) -> str:
        """Parse time from user query"""
        query = query.lower()
        
        # Simple time parsing for demo
        if "am" in query or "pm" in query:
            return query
        elif any(str(hour) in query for hour in range(1, 13)):
            # Extract the hour
            for hour in range(1, 13):
                if str(hour) in query:
                    # Assume AM if hour is 8-12, PM otherwise
                    suffix = "AM" if 8 <= hour <= 12 else "PM"
                    return f"{hour} {suffix}"
        
        return "the specified time"
    
    def _handle_location_query(self, query: str, location: Dict[str, float] = None) -> Dict[str, Any]:
        """Handle location-based queries"""
        services = self._find_nearest_services(location)
        
        response = "Here are auto services located near your location:\n\n"
        
        for doc in services[:2]:  # Limit to 2 services for readability
            service_info = doc.page_content.split("\n")
            service_name = service_info[0].replace("Service Name: ", "")
            service_location = service_info[2].replace("Location: ", "")
            service_website = service_info[4].replace("Website: ", "")
            response += f"- {service_name} located at {service_location}\n  Link: {service_website}\n\n"
        
        return {
            "response": response,
            "confidence": 0.9,
            "requires_human": False,
            "services": [doc.metadata.get("id") for doc in services[:2] if doc.metadata.get("id")]
        }
    
    def _handle_brake_issue(self, query: str) -> Dict[str, Any]:
        """Handle brake-related issues"""
        relevant_docs = self._simple_search(query)
        
        if relevant_docs:
            response = "Based on your brake issue, here are some services that can help:\n\n"
            
            service_docs = [doc for doc in relevant_docs if doc.metadata.get("type") == "service"]
            for doc in service_docs:
                service_info = doc.page_content.split("\n")
                service_name = service_info[0].replace("Service Name: ", "")
                service_location = service_info[2].replace("Location: ", "")
                response += f"- {service_name} located at {service_location}\n"
            
            issue_docs = [doc for doc in relevant_docs if doc.metadata.get("category") == "brake_problems"]
            if issue_docs:
                response += "\nCommon brake problems include squeaking noises, soft pedal, and pulling to one side when braking."
                
            response += "\n\nWould you like to schedule an appointment with one of these services?"
            
            return {
                "response": response,
                "confidence": 0.8,
                "requires_human": False,
                "services": [doc.metadata.get("id") for doc in service_docs if doc.metadata.get("id")]
            }
        else:
            return {
                "response": "I understand you're having a brake problem. Could you provide more details about the issue?",
                "confidence": 0.6,
                "requires_human": False
            }
    
    def _handle_human_agent_request(self, query: str) -> Dict[str, Any]:
        """Handle requests for a human agent"""
        return {
            "response": "I'll connect you with a human agent who can assist you further. Please provide a brief description of your issue while I transfer you.",
            "confidence": 0.9,
            "requires_human": True
        }

    async def process_query(self, query: str, language: str = "en", location: Dict[str, float] = None, conversation_state: Dict[str, Any] = None) -> Dict[Any, Any]:
        """Process a query through the RAG system"""
        try:
            # Default empty conversation state if none provided
            if conversation_state is None:
                conversation_state = {}
            
            # Check if we're in the middle of a scheduling flow
            if conversation_state.get("expecting") in ["date", "time"]:
                return self._handle_scheduling(query, conversation_state)
            
            # Check for different query types
            query_lower = query.lower()
            
            # Human agent request
            if "human" in query_lower or "agent" in query_lower or "person" in query_lower:
                return self._handle_human_agent_request(query)
            
            # Brake problem query
            elif "brake" in query_lower or "break" in query_lower:
                return self._handle_brake_issue(query)
            
            # Location-based query
            elif "location" in query_lower or "near" in query_lower or "autoservice" in query_lower:
                return self._handle_location_query(query, location)
            
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
            
            # Default response for unrecognized queries
            else:
                return {
                    "response": "I'm here to help with auto service needs. Do you need assistance finding a service center, diagnosing a problem, or scheduling an appointment?",
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
>>>>>>> 9c26091 (backend try)
