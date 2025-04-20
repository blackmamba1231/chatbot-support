from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
import logging
import os
from datetime import datetime

from app.api.upload_utils import save_upload_file_temp, cleanup_temp_file

from app.rag.mock_engine import RAGEngine
from app.services.voice_service import VoiceService
from app.services.shopping_list_service import ShoppingListService
from app.services.calendar_integration_service import CalendarIntegrationService
from app.services.woocommerce_service import WooCommerceService

# Initialize services
voice_service = VoiceService()
shopping_list_service = ShoppingListService()
calendar_service = CalendarIntegrationService()
woocommerce_service = WooCommerceService()

# Initialize logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/mobile", tags=["mobile"])

# Initialize RAG engine
rag_engine = None

def get_rag_engine():
    global rag_engine
    if rag_engine is None:
        api_key = os.environ.get("OPENAI_API_KEY", "")
        rag_engine = RAGEngine(api_key=api_key)
    return rag_engine

# Chat endpoint for text messages
@router.post("/chat")
async def chat(
    request: Dict[str, Any],
    engine: RAGEngine = Depends(get_rag_engine)
):
    try:
        # Extract message from request (frontend sends 'message' instead of 'query')
        query = request.get("message", request.get("query", ""))
        language = request.get("language", "en")
        location = request.get("location")
        conversation_state = request.get("conversation_state", {})
        
        if not query:
            return JSONResponse(
                status_code=400,
                content={"error": "Message or query is required"}
            )
        
        logger.info(f"Received chat request: {query}")
        logger.info(f"Conversation state: {conversation_state}")
            
        # Process query through RAG engine
        response = await engine.process_query(
            query=query,
            language=language,
            location=location,
            conversation_state=conversation_state
        )
        
        # Log the response for debugging
        logger.info(f"Response: {response}")
        
        return response
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

# Chat endpoint for voice messages
@router.post("/chat/voice")
async def chat_voice(
    audio: UploadFile = File(...),
    language: str = Form("en"),
    engine: RAGEngine = Depends(get_rag_engine)
):
    temp_file_path = None
    try:
        # Save the uploaded audio file temporarily
        temp_file_path = await save_upload_file_temp(audio)
        
        if not temp_file_path:
            return JSONResponse(
                status_code=400,
                content={"error": "Failed to save audio file"}
            )
        
        # Read the audio file
        with open(temp_file_path, "rb") as f:
            audio_data = f.read()
        
        if not audio_data:
            return JSONResponse(
                status_code=400,
                content={"error": "Audio data is required"}
            )
            
        # Process voice input through RAG engine
        response = await engine.process_query(
            query="",  # Empty query since we're using voice
            language=language,
            audio_data=audio_data
        )
        
        return response
    except Exception as e:
        logger.error(f"Error in chat voice endpoint: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )
    finally:
        # Clean up temporary file
        if temp_file_path:
            cleanup_temp_file(temp_file_path)

# Shopping list endpoints
@router.get("/shopping-list")
async def get_shopping_list(list_name: str = "default"):
    try:
        result = shopping_list_service.get_items(list_name)
        return result
    except Exception as e:
        logger.error(f"Error getting shopping list: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@router.post("/shopping-list")
async def add_to_shopping_list(request: Dict[str, Any]):
    try:
        item = request.get("item", "")
        list_name = request.get("list_name", "default")
        
        if not item:
            return JSONResponse(
                status_code=400,
                content={"error": "Item is required"}
            )
            
        result = shopping_list_service.add_item(item, list_name)
        return result
    except Exception as e:
        logger.error(f"Error adding to shopping list: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@router.put("/shopping-list/{item_id}")
async def update_shopping_list_item(
    item_id: str,
    completed: bool,
    list_name: str = "default"
):
    try:
        if completed:
            result = shopping_list_service.mark_item_completed(item_id, list_name)
        else:
            # For now, we don't support unmarking items as completed
            return JSONResponse(
                status_code=400,
                content={"error": "Unmarking items as completed is not supported"}
            )
            
        return result
    except Exception as e:
        logger.error(f"Error updating shopping list item: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

# Calendar endpoints
@router.get("/calendar/events")
async def get_calendar_events(date: Optional[str] = None):
    try:
        if date:
            events = calendar_service.get_events_for_date(date)
        else:
            events = calendar_service.get_upcoming_events()
            
        return {"events": events}
    except Exception as e:
        logger.error(f"Error getting calendar events: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

@router.post("/calendar")
async def add_calendar_event(request: Dict[str, Any]):
    try:
        title = request.get("title", "")
        date = request.get("date", "")
        time = request.get("time")
        location = request.get("location")
        description = request.get("description")
        
        if not title or not date:
            return JSONResponse(
                status_code=400,
                content={"error": "Title and date are required"}
            )
            
        result = calendar_service.add_event(
            title=title,
            date=date,
            time=time,
            location=location,
            description=description
        )
        
        return result
    except Exception as e:
        logger.error(f"Error adding calendar event: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )

# Mall delivery endpoints
@router.get("/mall-delivery/locations")
async def get_mall_delivery_locations():
    """Get all available mall delivery locations"""
    try:
        locations = woocommerce_service.get_locations()
        return {"locations": locations}
    except Exception as e:
        logger.error(f"Error getting mall delivery locations: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error fetching locations: {str(e)}"}
        )

@router.get("/mall-delivery/products")
async def get_mall_delivery_products(location: Optional[str] = None):
    """Get mall delivery products, optionally filtered by location"""
    try:
        # Initialize mall delivery service with woocommerce service
        from app.services.mall_delivery_service import MallDeliveryService
        mall_service = MallDeliveryService(woocommerce_service=woocommerce_service)
        
        # Get products from mall delivery service
        result = mall_service.get_products(location)
        
        # Log the number of products found
        product_count = len(result.get("products", []))
        logger.info(f"Found {product_count} mall delivery products for location: {location or 'all'}")
        
        # Return the result with proper structure for frontend
        return {
            "status": "success",
            "services": result.get("products", [])
        }
    except Exception as e:
        logger.error(f"Error getting mall delivery products: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error fetching products: {str(e)}"}
        )

@router.get("/mall-delivery/restaurants")
async def get_mall_delivery_restaurants(location: Optional[str] = None):
    """Get restaurant services, optionally filtered by location"""
    try:
        # Initialize mall delivery service with woocommerce service
        from app.services.mall_delivery_service import MallDeliveryService
        mall_service = MallDeliveryService(woocommerce_service=woocommerce_service)
        
        # Get restaurant products from WooCommerce
        # Use the enhanced WooCommerce service to get restaurant category products
        from app.services.enhanced_woocommerce_service import EnhancedWooCommerceService
        # Import the service from main instead of creating a new instance
        from main import enhanced_woocommerce_service as enhanced_wc
        
        # Get products from restaurant category
        params = {
            "category": "223",  # Use the same category ID as mall delivery for now
            "per_page": 100
        }
        restaurant_products = enhanced_wc.get_products(**params)
        
        # Filter and format restaurant products
        restaurants = []
        for product in restaurant_products:
            # Skip products that don't match location filter
            product_name = product.get("name", "")
            if location and location.lower() not in product_name.lower():
                continue
                
            restaurants.append({
                "id": str(product.get("id", "")),
                "name": product.get("name", ""),
                "price": str(product.get("price", "0.00")),
                "image": product.get("images", [{}])[0].get("src", "") if product.get("images") else "",
                "description": product.get("short_description", "") or product.get("description", ""),
                "location": location or "All locations"
            })
        
        logger.info(f"Found {len(restaurants)} restaurant products for location: {location or 'all'}")
        
        return {
            "status": "success",
            "restaurants": restaurants
        }
    except Exception as e:
        logger.error(f"Error getting restaurant services: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error fetching restaurants: {str(e)}"}
        )

@router.get("/mall-delivery/categories")
async def get_mall_delivery_categories():
    """Get all product categories for mall delivery"""
    try:
        categories = woocommerce_service.get_categories()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error getting product categories: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error fetching categories: {str(e)}"}
        )

@router.get("/mall-delivery/product/{product_id}")
async def get_mall_delivery_product(product_id: int):
    """Get a specific product by ID"""
    try:
        product = woocommerce_service.get_product(product_id)
        if product:
            return {"product": product}
        return JSONResponse(
            status_code=404,
            content={"error": f"Product with ID {product_id} not found"}
        )
    except Exception as e:
        logger.error(f"Error getting product details: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error fetching product details: {str(e)}"}
        )

@router.post("/mall-delivery/orders")
async def create_mall_delivery_order(request: Dict[str, Any]):
    """Create a new mall delivery order"""
    try:
        order_data = request.get("order_data", {})
        if not order_data:
            return JSONResponse(
                status_code=400,
                content={"error": "Order data is required"}
            )
        
        result = woocommerce_service.create_order(order_data)
        return result
    except Exception as e:
        logger.error(f"Error creating mall delivery order: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error creating order: {str(e)}"}
        )

@router.get("/mall-delivery/orders/{order_id}")
async def get_mall_delivery_order(order_id: int):
    """Get details of a specific order"""
    try:
        order = woocommerce_service.get_order(order_id)
        if order:
            return {"order": order}
        return JSONResponse(
            status_code=404,
            content={"error": f"Order with ID {order_id} not found"}
        )
    except Exception as e:
        logger.error(f"Error getting order details: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": f"Error fetching order details: {str(e)}"}
        )
