<<<<<<< HEAD
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Vogo.Family Chatbot API")
=======
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from datetime import datetime
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()
from app.rag.mock_engine import RAGEngine
from app.services.mock_calendar_service import CalendarService
from app.services.mock_notification_service import NotificationService
from app.services.local_ticket_service import LocalTicketService

from app.services.woocommerce_service import WooCommerceService
from app.services.calendar_integration_service import CalendarIntegrationService
from app.services.notification_service import NotificationService
from app.services.ticket_service import TicketService
from app.services.order_service import OrderService
from app.services.email_notification_service import EmailNotificationService
from app.services.ticketing_service import TicketingService

# Import enhanced WooCommerce services
from app.services.enhanced_woocommerce_service import EnhancedWooCommerceService
from app.services.enhanced_order_service import EnhancedOrderService
from app.services.customer_service import CustomerService
from app.services.product_service import ProductService
from app.services.openai_service import OpenAIService
from app.services.intent_detection_service import IntentDetectionService
from app.services.location_service import LocationService
from app.services.mall_delivery_service import MallDeliveryService

# Import API routers
from app.api.mobile_router import router as mobile_router
from app.api.ai_shopping_router import router as ai_shopping_router

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.title = "Vogo.Family Chatbot API"
>>>>>>> 9c26091 (backend try)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD
=======
# Include API routers
app.include_router(mobile_router)
app.include_router(ai_shopping_router)

# Initialize services
rag_engine = RAGEngine()
calendar_service = CalendarService()
notification_service = NotificationService()
ticket_service = LocalTicketService()

woocommerce_service = WooCommerceService()
calendar_integration_service = CalendarIntegrationService()
notification_service = NotificationService()
ticket_service = TicketService()
order_service = OrderService()
email_notification_service = EmailNotificationService()
ticketing_service = TicketingService()

# Initialize enhanced WooCommerce services
enhanced_woocommerce_service = EnhancedWooCommerceService()
enhanced_order_service = EnhancedOrderService(woocommerce_service=enhanced_woocommerce_service)
customer_service = CustomerService(woocommerce_service=enhanced_woocommerce_service)
product_service = ProductService(woocommerce_service=enhanced_woocommerce_service)
mall_delivery_service = MallDeliveryService(woocommerce_service=woocommerce_service)
openai_service = OpenAIService()
location_service = LocationService()
intent_detection_service = IntentDetectionService(woocommerce_service=woocommerce_service)

# Mall delivery locations endpoint
@app.get("/mall-delivery-locations")
async def get_mall_delivery_locations():
    """Get all available mall delivery locations"""
    try:
        locations = location_service.get_locations_by_service("mall_delivery")
        return {"locations": locations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

product_service = ProductService(woocommerce_service=enhanced_woocommerce_service)

from app.services.whisper_service import WhisperService

# Initialize Whisper service
whisper_service = WhisperService()

class Location(BaseModel):
    latitude: float
    longitude: float

>>>>>>> 9c26091 (backend try)
class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "en"
    voice_input: Optional[bool] = False
<<<<<<< HEAD
=======
    conversation_id: Optional[str] = None
    location: Optional[Location] = None
    conversation_state: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    requires_human: bool
    services: Optional[List[str]] = None
    expecting: Optional[str] = None
    action: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
>>>>>>> 9c26091 (backend try)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Vogo.Family Chatbot API is running"}

<<<<<<< HEAD
@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        # TODO: Implement RAG system integration
        # For now, return a mock response
        return {
            "response": "This is a demo response. RAG system integration pending.",
            "confidence": 0.9,
            "requires_human": False
        }
    except Exception as e:
=======
@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        # Extract user message
        user_message = chat_message.message
        
        # Get conversation history if available
        conversation_history = chat_message.conversation_state.get('history', []) if chat_message.conversation_state else []
        
        # Check if location is specified in the request
        location = chat_message.location.city if chat_message.location else None
        
        # Process message using AI-powered intent detection
        result = intent_detection_service.process_user_message(user_message)
        
        # Get intent data
        intent_data = result.get('intent', {})
        primary_intent = intent_data.get('primary_intent', 'general_query')
        detected_location = intent_data.get('location') or location
        
        # Get products based on the detected intent
        products = result.get('products', [])
        
        # Format the products for display
        formatted_products = []
        for product in products:
            formatted_products.append({
                'id': product.get('id'),
                'name': product.get('name', ''),
                'description': product.get('description', ''),
                'price': product.get('price', ''),
                'image_url': product.get('images', [''])[0] if product.get('images') else None
            })
        
        # Determine if human assistance is needed
        requires_human = primary_intent == 'customer_support'
        
        # Get the AI-generated response
        response_text = result.get('response', 'I\'m sorry, I couldn\'t process your request.')
        
        # Create the response
        response = {
            'response': response_text,
            'confidence': 0.9,
            'requires_human': requires_human,
            'products': formatted_products,
            'detected_intent': primary_intent,
            'location': detected_location
        }
        
        # Return in the expected format
        return ChatResponse(
            response=response_text,
            confidence=0.9,
            requires_human=requires_human,
            services=[p['name'] for p in formatted_products[:5]] if formatted_products else None,
            expecting='location' if not detected_location and products else None
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    try:
        # Transcribe the audio using Whisper
        transcription = await whisper_service.transcribe_audio(audio.file)
        
        return {
            "status": "success",
            "text": transcription
        }
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    try:
        # Handle voice input if provided
        if chat_message.voice_input:
            # Convert voice to text using Whisper
            result = whisper_model.transcribe(chat_message.message)
            chat_message.message = result["text"]
        
        # Get active locations for context
        locations = location_service.get_active_locations()
        location_names = [loc["city"] for loc in locations]
        
        # Get restaurants for context
        try:
            # Extract location from message if mentioned
            message_lower = chat_message.message.lower()
            location = None
            for loc in location_names:
                if loc.lower() in message_lower:
                    location = loc
                    break
            
            # Get products from different categories
            kids_activities = woocommerce_service.get_kids_activities(location=location)
            bio_food = woocommerce_service.get_bio_food(location=location)
            antipasti = woocommerce_service.get_antipasti(location=location)
            pet_care = woocommerce_service.get_pet_care(location=location)
            allergy_products = woocommerce_service.get_allergy_products(location=location)

            # Extract product names from each category
            kids_activities_names = [p["name"] for p in kids_activities.get("activities", [])] if kids_activities["status"] == "success" else []
            bio_food_names = [p["name"] for p in bio_food.get("food_items", [])] if bio_food["status"] == "success" else []
            antipasti_names = [p["name"] for p in antipasti.get("antipasti_items", [])] if antipasti["status"] == "success" else []
            pet_care_names = [p["name"] for p in pet_care.get("pet_items", [])] if pet_care["status"] == "success" else []
            allergy_products_names = [p["name"] for p in allergy_products.get("allergy_items", [])] if allergy_products["status"] == "success" else []
        except Exception as e:
            logger.error(f"Error getting products: {str(e)}")
            kids_activities_names = []
            bio_food_names = []
            antipasti_names = []
            pet_care_names = []
            allergy_products_names = []
        
        # Prepare context for AI
        context = {
            "locations": location_names,
            "kids_activities": kids_activities_names[:5],  # Top 5 kids activities
            "bio_food": bio_food_names[:5],  # Top 5 bio food products
            "antipasti": antipasti_names[:5],  # Top 5 antipasti products
            "pet_care": pet_care_names[:5],  # Top 5 pet care products
            "allergy_products": allergy_products_names[:5]  # Top 5 allergy products
        }
        
        # Get AI response
        ai_response = await openai_service.get_ai_response(
            user_message=chat_message.message,
            context=context
        )
        
        # Log the AI response for debugging
        logger.info(f"AI response: {ai_response}")
        
        # Extract the response text from the dictionary
        response_text = ai_response.get("response", "I'm sorry, I couldn't generate a response.")
        confidence = ai_response.get("confidence", 0.5)
        requires_human = ai_response.get("requires_human", False)
        action = ai_response.get("action", None)
        services = ai_response.get("services", [])
        
        return ChatResponse(
            response=response_text,
            confidence=confidence,
            requires_human=requires_human,
            services=services,
            expecting=None,
            action=action,
            date=None,
            time=None
        )
    except Exception as e:
        logger.exception("Error in /chat endpoint")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/kids-activities")
def get_kids_activities(location: Optional[str] = None):
    """Get kids activities, optionally filtered by location"""
    return woocommerce_service.get_kids_activities(location)

@app.get("/bio-food")
def get_bio_food(location: Optional[str] = None):
    """Get bio food products, optionally filtered by location"""
    return woocommerce_service.get_bio_food(location)

@app.get("/antipasti")
def get_antipasti(location: Optional[str] = None):
    """Get antipasti products, optionally filtered by location"""
    return woocommerce_service.get_antipasti(location)

@app.get("/pet-care")
def get_pet_care(location: Optional[str] = None):
    """Get pet care products, optionally filtered by location"""
    return woocommerce_service.get_pet_care(location)

@app.get("/allergy-products")
def get_allergy_products(location: Optional[str] = None):
    """Get allergy-related products, optionally filtered by location"""
    return woocommerce_service.get_allergy_products(location)





@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/calendar")
async def add_to_calendar(data: Dict[str, Any]):
    result = await calendar_service.add_event(
        service_details=data["service_details"],
        date=data["date"],
        time=data["time"]
    )
    
    if result["status"] == "success":
        # Send notification
        await notification_service.send_booking_confirmation({
            "service_name": data["service_details"]["name"],
            "date": data["date"],
            "time": data["time"],
            "location": data["service_details"]["location"],
            "issue": data.get("issue", "Not specified")
        })
        
        # Create ticket
        await ticket_service.create_ticket({
            "service_name": data["service_details"]["name"],
            "date": data["date"],
            "time": data["time"],
            "location": data["service_details"]["location"],
            "issue": data.get("issue", "Not specified")
        })
    
    return result

@app.post("/email")
async def send_email(data: Dict[str, Any]):
    result = await notification_service.send_booking_confirmation(data)
    return result

@app.post("/operator")
async def request_operator(data: Dict[str, Any]):
    try:
        # Create a ticket for human operator
        ticket_result = await ticket_service.create_ticket(data)
        
        if ticket_result["status"] == "success":
            # Assign to human operator
            result = await ticket_service.assign_to_human_operator(ticket_result["ticket_id"])
            return result
        
        return ticket_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-woocommerce")
async def sync_woocommerce(force: bool = False):
    """Manually trigger a sync of the WooCommerce data"""
    try:
        # Use the new sync_data method
        success = woocommerce_service.sync_data(force=force)
        if success:
            # Also sync the knowledge base if needed
            kb_success = woocommerce_service.sync_knowledge_base(force=force)
            # Reload the RAG engine with the updated data
            rag_engine.setup_engine()
            return {"status": "success", "message": "WooCommerce data synced successfully"}
        else:
            return {"status": "error", "message": "Failed to sync WooCommerce data"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/products")
async def get_products(category: Optional[str] = None):
    """Get products from WooCommerce"""
    try:
        products = woocommerce_service.get_products(category=category)
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/orders")
async def create_order(order_data: Dict[str, Any]):
    """Create a new order in WooCommerce"""
    try:
        result = order_service.create_order(order_data)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Error creating order"))
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/{order_id}")
async def get_order(order_id: int):
    """Get order details by ID"""
    try:
        result = order_service.get_order(order_id)
        if result.get("status") == "error":
            raise HTTPException(status_code=404, detail=result.get("message", "Order not found"))
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/orders/customer/{email}")
async def get_customer_orders(email: str):
    """Get orders for a specific customer"""
    try:
        result = order_service.get_customer_orders(email)
        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("message", "Error retrieving orders"))
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets")
async def get_tickets(status: Optional[str] = None):
    """Get all tickets, optionally filtered by status"""
    try:
        tickets = await ticket_service.get_all_tickets(status=status)
        return {"status": "success", "tickets": tickets}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tickets/{ticket_id}")
async def get_ticket(ticket_id: str):
    """Get a specific ticket by ID"""
    try:
        ticket = await ticket_service.get_ticket(ticket_id)
        if ticket:
            return {"status": "success", "ticket": ticket}
        else:
            raise HTTPException(status_code=404, detail=f"Ticket with ID {ticket_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tickets")
async def create_ticket(data: Dict[str, Any]):
    """Create a new ticket"""
    try:
        result = await ticket_service.create_ticket(data)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/tickets/{ticket_id}")
async def update_ticket(ticket_id: str, updates: Dict[str, Any]):
    """Update a ticket"""
    try:
        result = await ticket_service.update_ticket(ticket_id, updates)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tickets/{ticket_id}/close")
async def close_ticket(ticket_id: str, data: Dict[str, Any]):
    """Close a ticket with a resolution"""
    try:
        resolution = data.get("resolution", "Resolved by system")
        result = await ticket_service.close_ticket(ticket_id, resolution)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Test endpoints for API features
@app.get("/test/woocommerce")
async def test_woocommerce():
    try:
        # Test WooCommerce connection
        products = woocommerce_service.get_products(limit=5)
        categories = woocommerce_service.get_product_categories()
        
        return {
            "status": "success",
            "products_count": len(products),
            "categories_count": len(categories),
            "products_sample": products[:2] if products else [],
            "categories_sample": categories[:2] if categories else []
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

# Enhanced WooCommerce API endpoints

# Product endpoints
@app.get("/api/products")
async def get_all_products(category: Optional[str] = None, limit: int = 100):
    """Get all products, optionally filtered by category"""
    try:
        result = product_service.get_products(category=category, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/{product_id}")
async def get_product(product_id: int):
    """Get a specific product by ID"""
    try:
        result = product_service.get_product_by_id(product_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/search")
async def search_products(query: str, category: Optional[str] = None, limit: int = 20):
    """Search for products by name or description"""
    try:
        result = product_service.search_products(query=query, category=category, limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/categories")
async def get_product_categories():
    """Get all product categories"""
    try:
        result = product_service.get_product_categories()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/featured")
async def get_featured_products(limit: int = 10):
    """Get featured products"""
    try:
        result = product_service.get_featured_products(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/sale")
async def get_on_sale_products(limit: int = 10):
    """Get products that are on sale"""
    try:
        result = product_service.get_on_sale_products(limit=limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/products/reviews")
async def get_product_reviews(product_id: Optional[int] = None):
    """Get product reviews, optionally filtered by product ID"""
    try:
        result = product_service.get_product_reviews(product_id=product_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Customer endpoints
@app.post("/api/customers")
async def create_customer(customer_data: Dict[str, Any]):
    """Create a new customer"""
    try:
        result = customer_service.create_customer(customer_data)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}")
async def get_customer(customer_id: int):
    """Get a specific customer by ID"""
    try:
        result = customer_service.get_customer(customer_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/email/{email}")
async def get_customer_by_email(email: str):
    """Get a specific customer by email"""
    try:
        result = customer_service.get_customer_by_email(email)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/customers/{customer_id}")
async def update_customer(customer_id: int, customer_data: Dict[str, Any]):
    """Update a customer"""
    try:
        result = customer_service.update_customer(customer_id, customer_data)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/customers/{customer_id}/address")
async def add_customer_address(customer_id: int, address_data: Dict[str, Any], address_type: str = "billing"):
    """Add a new address to a customer"""
    try:
        result = customer_service.add_customer_address(customer_id, address_data, address_type)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Enhanced Order endpoints
@app.post("/api/orders")
async def create_enhanced_order(order_data: Dict[str, Any]):
    """Create a new order using the enhanced order service"""
    try:
        result = enhanced_order_service.create_order(order_data)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/{order_id}")
async def get_enhanced_order(order_id: int):
    """Get order details by ID using the enhanced order service"""
    try:
        result = enhanced_order_service.get_order(order_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/customer/{customer_id}")
async def get_customer_enhanced_orders(customer_id: int):
    """Get orders for a specific customer using the enhanced order service"""
    try:
        result = enhanced_order_service.get_customer_orders(customer_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/orders/email/{email}")
async def get_customer_orders_by_email(email: str):
    """Get orders for a customer by email using the enhanced order service"""
    try:
        result = enhanced_order_service.get_customer_orders_by_email(email)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/orders/{order_id}/status")
async def update_order_status(order_id: int, status: str):
    """Update order status"""
    try:
        result = enhanced_order_service.update_order_status(order_id, status)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders/{order_id}/notes")
async def add_order_note(order_id: int, note: str, is_customer_note: bool = False):
    """Add a note to an order"""
    try:
        result = enhanced_order_service.add_order_note(order_id, note, is_customer_note)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/orders/{order_id}/cancel")
async def cancel_order(order_id: int, reason: Optional[str] = None):
    """Cancel an order"""
    try:
        result = enhanced_order_service.cancel_order(order_id, reason)
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/coupons/validate")
async def validate_coupon(code: str):
    """Validate a coupon code"""
    try:
        result = enhanced_order_service.validate_coupon(code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Shipping and Payment endpoints
@app.get("/api/shipping/methods")
async def get_shipping_methods():
    """Get available shipping methods"""
    try:
        methods = enhanced_woocommerce_service.get_shipping_methods()
        return {"status": "success", "methods": methods}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/shipping/zones")
async def get_shipping_zones():
    """Get shipping zones"""
    try:
        zones = enhanced_woocommerce_service.get_shipping_zones()
        return {"status": "success", "zones": zones}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/payment/gateways")
async def get_payment_gateways():
    """Get available payment gateways"""
    try:
        gateways = enhanced_woocommerce_service.get_payment_gateways()
        return {"status": "success", "gateways": gateways}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mall delivery product endpoints
@app.get("/mall-delivery")
async def get_mall_delivery_products(location: Optional[str] = None):
    try:
        result = woocommerce_service.get_mall_delivery_services(location)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/categories")
async def get_categories():
    try:
        result = woocommerce_service.get_categories()
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# Create mall delivery order
@app.post("/create-order")
def create_mall_delivery_order(order_data: Dict[str, Any]):
    return mall_delivery_service.create_order(order_data)

# Test endpoint for AI intent detection
@app.post("/test-intent")
async def test_intent_detection(data: Dict[str, Any]):
    """Test the AI-powered intent detection system"""
    try:
        user_message = data.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
            
        result = intent_detection_service.process_user_message(user_message)
        return result
    except Exception as e:
        logger.error(f"Error in test-intent endpoint: {str(e)}")
>>>>>>> 9c26091 (backend try)
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
