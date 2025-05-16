from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import logging
import os
from app.services.woocommerce_service import WooCommerceService
from openai import OpenAI

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ai-shopping", tags=["AI Shopping"])

# Initialize services
woocommerce_service = WooCommerceService()
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Request models
class ProductSearchRequest(BaseModel):
    query: str
    location: Optional[str] = None
    category_id: Optional[int] = None
    limit: Optional[int] = 10

class ChatRequest(BaseModel):
    message: str
    language: str = "en"
    voice_input: Optional[bool] = False
    conversation_id: Optional[str] = None
    location: Optional[Dict[str, Any]] = None
    conversation_state: Optional[Dict[str, Any]] = None

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

def detect_intent(message: str) -> Dict[str, Any]:
    """Detect user intent from message"""
    try:
        # Define system prompt for intent detection
        system_prompt = """You are an intent detection system for a shopping chatbot.
        Extract the following information from the user message:
        1. primary_intent: One of [browse_products, search_product, product_info, order_product, get_location, customer_support, general_query]
        2. location: Any Romanian city mentioned (Alba Iulia, Arad, Bacău, Baia Mare, Bistrița, Botoșani, Brașov, Brăila, București, Buzău, Cluj-Napoca, Ploiești, Suceava, Timișoara, Târgu Mureș)
        3. product_type: One of [mall_delivery, kids_activities, bio_food, antipasti, pet_care, allergies]
        4. search_terms: Specific product terms they're searching for
        
        Respond with a JSON object containing these fields. If a field can't be determined, use null."""

        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message}
            ],
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        # Parse the AI response as JSON
        import json
        intent_data = json.loads(response.choices[0].message.content)
        logger.info(f"Detected intent: {intent_data}")
        return intent_data
    
    except Exception as e:
        logger.error(f"Error detecting intent: {str(e)}")
        return {
            "primary_intent": "general_query",
            "location": None,
            "product_type": None,
            "search_terms": None
        }

def get_products_by_intent(intent_data: Dict[str, Any], limit: int = 10) -> List[Dict[str, Any]]:
    """Get products based on detected intent"""
    try:
        # Extract relevant data
        product_type = intent_data.get("product_type")
        location = intent_data.get("location")
        search_terms = intent_data.get("search_terms")
        
        products = []
        
        # Intent to category ID mapping
        intent_category_map = {
            "mall_delivery": 223,
            "kids_activities": 563,
            "bio_food": 346,
            "antipasti": 347,
            "pet_care": 547,
            "allergies": 548
        }
        
        # Get category ID based on product type
        category_id = None
        if product_type in intent_category_map:
            category_id = intent_category_map[product_type]
        
        # If we have a category, get products by category
        if category_id:
            if product_type == "mall_delivery":
                result = woocommerce_service.get_mall_delivery_services(location)
                if result.get("status") == "success":
                    products = result.get("services", [])
            elif product_type == "kids_activities":
                result = woocommerce_service.get_kids_activities(location)
                if result.get("status") == "success":
                    products = result.get("activities", [])
            elif product_type == "bio_food":
                result = woocommerce_service.get_bio_food(location)
                if result.get("status") == "success":
                    products = result.get("food_items", [])
            elif product_type == "antipasti":
                result = woocommerce_service.get_antipasti(location)
                if result.get("status") == "success":
                    products = result.get("antipasti_items", [])
            elif product_type == "pet_care":
                result = woocommerce_service.get_pet_care(location)
                if result.get("status") == "success":
                    products = result.get("pet_items", [])
            elif product_type == "allergies":
                result = woocommerce_service.get_allergy_products(location)
                if result.get("status") == "success":
                    products = result.get("allergy_items", [])
        
        # If no products found but we have search terms, try a general search
        if not products and search_terms:
            params = {"search": search_terms, "per_page": limit}
            if location:
                params["search"] = f"{params['search']} {location}"
                
            success, api_products = woocommerce_service._make_request("products", params=params)
            if success and isinstance(api_products, list):
                products = [
                    {
                        "id": p.get("id"),
                        "name": p.get("name", ""),
                        "description": p.get("description", ""),
                        "price": p.get("price", ""),
                        "image_url": p.get("images", [{}])[0].get("src") if p.get("images") else None,
                        "categories": [cat.get("name") for cat in p.get("categories", [])]
                    }
                    for p in api_products
                ]
                
        return products[:limit]
        
    except Exception as e:
        logger.error(f"Error getting products by intent: {str(e)}")
        return []

@router.post("/search", response_model=ProductSearchResponse)
async def ai_product_search(request: ProductSearchRequest):
    """
    Search for products using AI intent detection
    """
    try:
        # Detect intent from query
        intent_data = detect_intent(request.query)
        
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
                548: "allergies"
            }
            if request.category_id in category_map:
                intent_data["product_type"] = category_map[request.category_id]
        
        # Get products based on intent
        products = get_products_by_intent(intent_data, limit=request.limit or 10)
        
        # Convert products to response model format
        product_responses = []
        for product in products:
            product_responses.append(
                ProductResponse(
                    id=product.get("id"),
                    name=product.get("name", ""),
                    description=product.get("description", ""),
                    price=product.get("price", ""),
                    image_url=product.get("image_url"),
                    location=intent_data.get("location"),
                    categories=product.get("categories", [])
                )
            )
        
        return ProductSearchResponse(
            status="success",
            products=product_responses,
            detected_intent=intent_data.get("primary_intent"),
            detected_location=intent_data.get("location")
        )
        
    except Exception as e:
        logger.error(f"Error in AI product search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat", response_model=ChatResponse)
async def ai_chat(request: ChatRequest):
    """
    Process chat message using AI intent detection and generate a response with relevant products
    """
    try:
        # Extract location from request if available
        location = None
        if request.location:
            if isinstance(request.location, dict) and "city" in request.location:
                location = request.location["city"]
            elif isinstance(request.location, str):
                location = request.location
        
        # Detect intent from message
        intent_data = detect_intent(request.message)
        
        # If location is specified in request but not detected in message, use the request location
        if location and not intent_data.get("location"):
            intent_data["location"] = location
            
        # Get products based on intent
        products = get_products_by_intent(intent_data)
        
        # Generate response using GPT
        system_prompt = f"""You are a friendly and professional mall delivery chatbot for Vogo.Family, a leading delivery service in Romania.
        
        Current user intent: {intent_data.get('primary_intent')}
        Detected location: {intent_data.get('location') or 'None specified'}
        Product type of interest: {intent_data.get('product_type') or 'None specified'}
        
        Available Romanian cities for mall delivery: Alba Iulia, Arad, Bacău, Baia Mare, Bistrița, Botoșani, Brașov, Brăila, București, Buzău, Cluj-Napoca, Ploiești, Suceava, Timișoara, Târgu Mureș
        
        Here are the products we found based on the user's request:
        """
        
        if products:
            for i, product in enumerate(products[:5], 1):
                name = product.get("name", "Unknown")
                price = product.get("price", "N/A")
                system_prompt += f"\n{i}. {name} - {price} RON"
        else:
            system_prompt += "\nNo products found matching the request."
            
        system_prompt += """
        
        RESPONSE GUIDELINES:
        1. Be friendly, helpful and conversational
        2. If products were found, mention them specifically by name and price
        3. If no products were found, suggest alternatives or ask for more information
        4. If the user's location is not clear, ask for it
        5. Keep your response concise
        
        Products you should reference and recommend:
        - Mall delivery services from various Romanian malls (category 223)
        - Kids activities and toys (category 563)
        - Bio and organic food (category 346)
        - Antipasti and Mediterranean specialties (category 347)
        - Pet care products (category 547)
        - Allergy-friendly products (category 548)
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Determine if we're expecting a location
        expecting = None
        if not intent_data.get("location") and (
            intent_data.get("primary_intent") in ["browse_products", "search_product", "product_info"] or
            intent_data.get("product_type") is not None
        ):
            expecting = "location"
        
        # Determine action based on intent
        action = None
        if intent_data.get("product_type") == "mall_delivery":
            action = "show_malls"
        elif intent_data.get("product_type") == "kids_activities":
            action = "show_kids_activities"
        elif intent_data.get("product_type") == "bio_food":
            action = "show_bio_food"
        elif intent_data.get("product_type") == "antipasti":
            action = "show_antipasti"
        elif intent_data.get("product_type") == "pet_care":
            action = "show_pet_care"
        elif intent_data.get("product_type") == "allergies":
            action = "show_allergy_products"
        
        # Format product responses
        product_responses = []
        for product in products:
            product_responses.append(
                ProductResponse(
                    id=product.get("id"),
                    name=product.get("name", ""),
                    description=product.get("description", ""),
                    price=product.get("price", ""),
                    image_url=product.get("image_url"),
                    location=intent_data.get("location"),
                    categories=product.get("categories", [])
                )
            )
        
        # Create services list (names of products/services)
        services = [p.get("name", "") for p in products[:5] if p.get("name")]
        
        return ChatResponse(
            response=ai_response,
            confidence=0.9,
            requires_human=False,
            products=product_responses if product_responses else None,
            services=services if services else None,
            expecting=expecting,
            action=action,
            detected_intent=intent_data.get("primary_intent"),
            detected_location=intent_data.get("location")
        )
        
    except Exception as e:
        logger.error(f"Error in AI chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mall-delivery", response_model=ProductSearchResponse)
async def get_mall_delivery_products(location: Optional[str] = None, limit: int = 20):
    """
    Get mall delivery products, optionally filtered by location
    """
    try:
        result = woocommerce_service.get_mall_delivery_services(location)
        
        if result.get("status") != "success":
            return ProductSearchResponse(
                status="error",
                products=[],
                message=result.get("message", "Failed to fetch mall delivery products")
            )
            
        services = result.get("services", [])
        
        # Convert to response model format
        product_responses = []
        for service in services[:limit]:
            product_responses.append(
                ProductResponse(
                    id=service.get("id"),
                    name=service.get("name", ""),
                    description=service.get("description", ""),
                    price=service.get("price", ""),
                    image_url=service.get("images", [""])[0] if service.get("images") else None,
                    location=location,
                    categories=service.get("categories", [])
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

@router.get("/categories/{category_id}/products", response_model=ProductSearchResponse)
async def get_products_by_category(
    category_id: int,
    location: Optional[str] = None,
    limit: int = 20
):
    """
    Get products by category ID, optionally filtered by location
    """
    try:
        params = {
            "category": category_id,
            "per_page": limit,
            "status": "publish"
        }
        
        if location:
            params["search"] = location
            
        success, products = woocommerce_service._make_request("products", params=params)
        
        if not success:
            return ProductSearchResponse(
                status="error",
                products=[],
                message=f"Failed to fetch products for category {category_id}"
            )
            
        # Convert to response model format
        product_responses = []
        for product in products[:limit]:
            product_responses.append(
                ProductResponse(
                    id=product.get("id"),
                    name=product.get("name", ""),
                    description=product.get("description", ""),
                    price=product.get("price", ""),
                    image_url=product.get("images", [{}])[0].get("src") if product.get("images") else None,
                    location=location,
                    categories=[cat.get("name") for cat in product.get("categories", [])]
                )
            )
            
        # Category name map for detected_intent
        category_intent_map = {
            223: "mall_delivery",
            563: "kids_activities",
            346: "bio_food",
            347: "antipasti",
            547: "pet_care",
            548: "allergies"
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
