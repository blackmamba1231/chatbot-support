from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import json
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import services
from services.woocommerce_service import WooCommerceService
from services.intent_service import IntentService
from services.voice_service import VoiceService
from services.response_service import ResponseService

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
WOOCOMMERCE_URL = os.environ.get("WOOCOMMERCE_URL", "https://vogo.family")
WOOCOMMERCE_CONSUMER_KEY = os.environ.get("WOOCOMMERCE_CONSUMER_KEY")
WOOCOMMERCE_CONSUMER_SECRET = os.environ.get("WOOCOMMERCE_CONSUMER_SECRET")

# Look for backend .env file if keys not found
if not WOOCOMMERCE_CONSUMER_KEY or not WOOCOMMERCE_CONSUMER_SECRET:
    backend_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', '.env')
    if os.path.exists(backend_env_path):
        logger.info(f"Loading environment variables from backend .env: {backend_env_path}")
        from dotenv import load_dotenv
        load_dotenv(backend_env_path)
        WOOCOMMERCE_URL = os.environ.get("WOOCOMMERCE_URL", "https://vogo.family")
        WOOCOMMERCE_CONSUMER_KEY = os.environ.get("WOOCOMMERCE_CONSUMER_KEY")
        WOOCOMMERCE_CONSUMER_SECRET = os.environ.get("WOOCOMMERCE_CONSUMER_SECRET")

# Initialize services
woocommerce_service = WooCommerceService(WOOCOMMERCE_URL, WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)
intent_service = IntentService()
voice_service = VoiceService()
response_service = ResponseService()

# Create the FastAPI app
app = FastAPI(title="AI Shopping Assistant API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Request models
class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    voice_input: Optional[bool] = False
    conversation_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    conversation_state: Optional[Dict[str, Any]] = None

class ProductSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    category_id: Optional[int] = None
    limit: Optional[int] = 10

# Response models
class ProductResponse(BaseModel):
    id: Any
    name: str
    description: str = ""
    price: str = ""
    image_url: Optional[str] = None
    location: Optional[str] = None
    categories: List[str] = []

class ProductSearchResponse(BaseModel):
    status: str
    products: List[ProductResponse]
    detected_intent: Optional[str] = None
    detected_location: Optional[str] = None
    message: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float = 0.9
    requires_human: bool = False
    products: Optional[List[ProductResponse]] = None
    services: Optional[List[str]] = None
    expecting: Optional[str] = None
    action: Optional[str] = None
    detected_intent: Optional[str] = None
    detected_location: Optional[str] = None

class LocationResponse(BaseModel):
    status: str = "success"
    locations: List[str]

# API routes
@app.get("/")
async def root():
    return {"message": "AI Shopping Assistant API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process a chat message and return an AI response with relevant products"""
    try:
        message = request.message
        
        # Extract location if provided
        location = None
        if request.location:
            if isinstance(request.location, dict) and "city" in request.location:
                location = request.location["city"]
            elif isinstance(request.location, str):
                location = request.location
        
        # Detect intent from message
        intent_data = intent_service.detect_intent(message)
        
        # If location is specified in request but not detected in message, use the request location
        if location and not intent_data.get("location"):
            intent_data["location"] = location
        
        # Get products based on intent
        product_type = intent_data.get("product_type")
        detected_location = intent_data.get("location")
        
        products = []
        
        # Get products based on detected intent
        if product_type == "mall_delivery":
            products = woocommerce_service.get_products_by_category(223, location=detected_location)
        elif product_type == "kids_activities":
            products = woocommerce_service.get_products_by_category(563, location=detected_location)
        elif product_type == "bio_food":
            products = woocommerce_service.get_products_by_category(346, location=detected_location)
        elif product_type == "antipasti":
            products = woocommerce_service.get_products_by_category(347, location=detected_location)
        elif product_type == "pet_care":
            products = woocommerce_service.get_products_by_category(547, location=detected_location)
        elif product_type == "allergy":
            products = woocommerce_service.get_products_by_category(548, location=detected_location)
        
        # If no specific category was detected but location is known, get mall delivery products
        if not products and detected_location:
            products = woocommerce_service.get_products_by_category(223, location=detected_location)
        
        # Format products for response
        product_responses = []
        for product in products[:10]:  # Limit to 10 products
            product_responses.append(
                ProductResponse(
                    id=product.get("id"),
                    name=product.get("name", ""),
                    description=product.get("description", ""),
                    price=product.get("price", ""),
                    image_url=product.get("images", [None])[0],
                    location=detected_location,
                    categories=product.get("categories", [])
                )
            )
        
        # Generate AI response
        response_text = response_service.generate_response(
            user_message=message,
            intent_data=intent_data,
            products=products[:5]  # Send top 5 products to influence response
        )
        
        # Determine action based on intent
        action = None
        if product_type == "mall_delivery":
            action = "show_malls"
        elif product_type == "kids_activities":
            action = "show_kids_activities"
        elif product_type == "bio_food":
            action = "show_bio_food"
        elif product_type == "antipasti":
            action = "show_antipasti"
        elif product_type == "pet_care":
            action = "show_pet_care"
        elif product_type == "allergy":
            action = "show_allergy_products"
        
        # Determine if we're expecting a location
        expecting = None
        if not detected_location and (
            intent_data.get("primary_intent") in ["browse_products", "search_product", "product_info"] or
            product_type is not None
        ):
            expecting = "location"
            
        # Create services list (names of products/services)
        services = [p.get("name", "") for p in products[:5] if p.get("name")]
        
        return ChatResponse(
            response=response_text,
            confidence=0.9,
            requires_human=False,
            products=product_responses if product_responses else None,
            services=services if services else None,
            expecting=expecting,
            action=action,
            detected_intent=intent_data.get("primary_intent"),
            detected_location=detected_location
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai-shopping/chat", response_model=ChatResponse)
async def ai_shopping_chat(request: ChatRequest):
    """Alias for /chat endpoint for compatibility with frontend"""
    return await chat(request)

@app.post("/api/ai-shopping/search", response_model=ProductSearchResponse)
async def product_search(request: ProductSearchRequest):
    """Search for products using AI intent detection"""
    try:
        # Detect intent
        intent_data = intent_service.detect_intent(request.query)
        
        # If location is specified in request but not detected in query, use the request location
        if request.location and not intent_data.get("location"):
            intent_data["location"] = request.location
            
        # If category is specified in request, override detected category
        if request.category_id:
            # Map category ID to product type
            category_map = {
                223: "mall_delivery",
                563: "kids_activities",
                346: "bio_food",
                347: "antipasti",
                547: "pet_care",
                548: "allergy"
            }
            if request.category_id in category_map:
                intent_data["product_type"] = category_map[request.category_id]
        
        # Get products based on intent
        product_type = intent_data.get("product_type")
        detected_location = intent_data.get("location")
        limit = request.limit or 10
        
        products = []
        
        # Get products based on detected intent
        if product_type == "mall_delivery":
            products = woocommerce_service.get_products_by_category(223, location=detected_location, limit=limit)
        elif product_type == "kids_activities":
            products = woocommerce_service.get_products_by_category(563, location=detected_location, limit=limit)
        elif product_type == "bio_food":
            products = woocommerce_service.get_products_by_category(346, location=detected_location, limit=limit)
        elif product_type == "antipasti":
            products = woocommerce_service.get_products_by_category(347, location=detected_location, limit=limit)
        elif product_type == "pet_care":
            products = woocommerce_service.get_products_by_category(547, location=detected_location, limit=limit)
        elif product_type == "allergy":
            products = woocommerce_service.get_products_by_category(548, location=detected_location, limit=limit)
        
        # If no specific category was detected but we have search terms, try a general search
        if not products and intent_data.get("search_terms"):
            products = woocommerce_service.search_products(
                query=intent_data.get("search_terms"),
                location=detected_location,
                limit=limit
            )
        
        # Format products for response
        product_responses = []
        for product in products[:limit]:
            product_responses.append(
                ProductResponse(
                    id=product.get("id"),
                    name=product.get("name", ""),
                    description=product.get("description", ""),
                    price=product.get("price", ""),
                    image_url=product.get("images", [None])[0],
                    location=detected_location,
                    categories=product.get("categories", [])
                )
            )
            
        return ProductSearchResponse(
            status="success",
            products=product_responses,
            detected_intent=intent_data.get("primary_intent"),
            detected_location=detected_location
        )
        
    except Exception as e:
        logger.error(f"Error in product search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai-shopping/mall-delivery", response_model=ProductSearchResponse)
async def mall_delivery_products(location: Optional[str] = None, limit: int = 20):
    """Get mall delivery products, optionally filtered by location"""
    try:
        products = woocommerce_service.get_products_by_category(223, location=location, limit=limit)
        
        # Format products for response
        product_responses = []
        for product in products[:limit]:
            product_responses.append(
                ProductResponse(
                    id=product.get("id"),
                    name=product.get("name", ""),
                    description=product.get("description", ""),
                    price=product.get("price", ""),
                    image_url=product.get("images", [None])[0],
                    location=location,
                    categories=product.get("categories", [])
                )
            )
            
        return ProductSearchResponse(
            status="success",
            products=product_responses,
            detected_location=location
        )
        
    except Exception as e:
        logger.error(f"Error fetching mall delivery products: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ai-shopping/categories/{category_id}/products", response_model=ProductSearchResponse)
async def category_products(
    category_id: int,
    location: Optional[str] = None,
    limit: int = 20
):
    """Get products by category ID, optionally filtered by location"""
    try:
        products = woocommerce_service.get_products_by_category(category_id, location=location, limit=limit)
        
        # Format products for response
        product_responses = []
        for product in products[:limit]:
            product_responses.append(
                ProductResponse(
                    id=product.get("id"),
                    name=product.get("name", ""),
                    description=product.get("description", ""),
                    price=product.get("price", ""),
                    image_url=product.get("images", [None])[0],
                    location=location,
                    categories=product.get("categories", [])
                )
            )
        
        # Category name map for detected_intent
        category_intent_map = {
            223: "mall_delivery",
            563: "kids_activities",
            346: "bio_food",
            347: "antipasti",
            547: "pet_care",
            548: "allergy"
        }
            
        return ProductSearchResponse(
            status="success",
            products=product_responses,
            detected_intent=category_intent_map.get(category_id),
            detected_location=location
        )
        
    except Exception as e:
        logger.error(f"Error fetching products by category: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mobile/mall-delivery/locations", response_model=LocationResponse)
async def mall_delivery_locations():
    """Get available locations for mall delivery"""
    try:
        # Get mall delivery products
        products = woocommerce_service.get_products_by_category(223, limit=100)
        
        # Extract unique locations
        locations = set()
        for product in products:
            if product.get("location"):
                locations.add(product.get("location"))
        
        # If no locations found, return default list
        if not locations:
            locations = ["Alba Iulia", "Arad", "Bacău", "Baia Mare", "Bistrița", "Botoșani", 
                         "Brașov", "Brăila", "București", "Buzău", "Cluj-Napoca", "Ploiești", 
                         "Suceava", "Timișoara", "Târgu Mureș"]
        
        return LocationResponse(
            locations=sorted(list(locations))
        )
        
    except Exception as e:
        logger.error(f"Error fetching locations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/mobile/mall-delivery/products")
async def legacy_mall_delivery_products(location: Optional[str] = None):
    """Legacy endpoint for compatibility with older frontend versions"""
    try:
        products = woocommerce_service.get_products_by_category(223, location=location, limit=50)
        
        return {
            "status": "success",
            "services": products
        }
        
    except Exception as e:
        logger.error(f"Error in legacy mall delivery products: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
