import logging
from typing import Dict, Any, List, Optional, Tuple
from openai import OpenAI
import os
import json
from app.services.woocommerce_service import WooCommerceService, CATEGORY_MALL_DELIVERY, CATEGORY_KIDS_ACTIVITIES, CATEGORY_BIO_FOOD, CATEGORY_ANTIPASTI, CATEGORY_PET_CARE, CATEGORY_ALLERGIES

logger = logging.getLogger(__name__)

# Intent to category mapping
INTENT_TO_CATEGORY = {
    "mall_delivery": CATEGORY_MALL_DELIVERY,
    "kids_activities": CATEGORY_KIDS_ACTIVITIES,
    "bio_food": CATEGORY_BIO_FOOD,
    "antipasti": CATEGORY_ANTIPASTI,
    "pet_care": CATEGORY_PET_CARE,
    "allergies": CATEGORY_ALLERGIES
}

class IntentDetectionService:
    def __init__(self, woocommerce_service: WooCommerceService = None):
        """Initialize the intent detection service with WooCommerce integration"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.woocommerce_service = woocommerce_service or WooCommerceService()
        
        # Cache products to reduce API calls
        self.product_cache = {}
    
    def detect_intent(self, user_message: str) -> Dict[str, Any]:
        """
        Detect the user's intent from their message
        
        Returns:
            Dict containing:
            - primary_intent: The main detected intent
            - location: Any detected location
            - product_type: Type of product they're looking for
            - confidence: Confidence score of the intent detection
        """
        try:
            messages = [
                {
                    "role": "system", 
                    "content": """You are an intent detection system for an e-commerce chatbot.
                    Extract the following information from user messages:
                    1. primary_intent: One of [browse_products, search_product, order_product, get_location, customer_support, general_query]
                    2. location: Any mentioned Romanian city or shopping mall
                    3. product_type: The category of products they're interested in [mall_delivery, kids_activities, bio_food, antipasti, pet_care, allergies]
                    4. search_terms: Specific product terms or keywords they're searching for
                    
                    Respond ONLY with a valid JSON object containing these fields. If a field is not found, use null."""
                },
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.1,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            
            intent_data = json.loads(response.choices[0].message.content)
            logger.info(f"Detected intent: {intent_data}")
            return intent_data
        
        except Exception as e:
            logger.error(f"Error detecting intent: {str(e)}")
            # Return default intent on error
            return {
                "primary_intent": "general_query",
                "location": None,
                "product_type": None,
                "search_terms": None,
                "confidence": 0.5
            }
    
    def get_products_by_intent(self, intent_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get products based on the detected intent"""
        
        # Extract relevant information from intent
        product_type = intent_data.get("product_type")
        location = intent_data.get("location")
        search_terms = intent_data.get("search_terms")
        
        # Default to empty list
        products = []
        
        try:
            # Case 1: If product type is specified, use the corresponding category
            if product_type and product_type in INTENT_TO_CATEGORY:
                category_id = INTENT_TO_CATEGORY[product_type]
                
                # Check if we have it in cache first
                cache_key = f"{product_type}_{location}_{search_terms}"
                if cache_key in self.product_cache:
                    return self.product_cache[cache_key]
                
                # Get products by category
                params = {
                    "category": category_id,
                    "per_page": 10
                }
                
                # Add location filter if specified
                if location:
                    params["search"] = location
                    
                # Add search terms if specified
                if search_terms:
                    params["search"] = f"{params.get('search', '')} {search_terms}".strip()
                
                # Make the API request
                success, response = self.woocommerce_service._make_request("products", params=params)
                if success and isinstance(response, list):
                    products = self._format_products(response)
                    self.product_cache[cache_key] = products
            
            # Case 2: If no specific product type but we have search terms
            elif search_terms:
                # Check cache first
                cache_key = f"search_{location}_{search_terms}"
                if cache_key in self.product_cache:
                    return self.product_cache[cache_key]
                
                # Search across all products
                params = {
                    "search": search_terms,
                    "per_page": 10
                }
                
                # Add location filter if specified
                if location:
                    params["search"] = f"{params.get('search', '')} {location}".strip()
                
                # Make the API request
                success, response = self.woocommerce_service._make_request("products", params=params)
                if success and isinstance(response, list):
                    products = self._format_products(response)
                    self.product_cache[cache_key] = products
            
            # Case 3: Just location specified, show mall delivery for that location
            elif location:
                services = self.woocommerce_service.get_mall_delivery_services(location)
                if services.get("status") == "success":
                    products = services.get("services", [])
            
            return products
            
        except Exception as e:
            logger.error(f"Error getting products by intent: {str(e)}")
            return []
    
    def _format_products(self, products: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format the raw WooCommerce products for the chatbot response"""
        formatted_products = []
        
        for product in products:
            formatted_product = {
                "id": product.get("id"),
                "name": product.get("name", ""),
                "description": product.get("short_description", product.get("description", "")),
                "price": product.get("price", ""),
                "images": [img["src"] for img in product.get("images", [])],
                "categories": [cat["name"] for cat in product.get("categories", [])],
                "tags": [tag["name"] for tag in product.get("tags", [])]
            }
            formatted_products.append(formatted_product)
        
        return formatted_products
    
    def process_user_message(self, user_message: str) -> Dict[str, Any]:
        """
        Process a user message to detect intent and find relevant products
        
        Returns:
            Dict containing:
            - intent: The detected intent
            - products: List of relevant products
            - response: AI-generated response
            - location: Detected location (if any)
        """
        # Step 1: Detect user intent
        intent_data = self.detect_intent(user_message)
        
        # Step 2: Get relevant products based on intent
        products = self.get_products_by_intent(intent_data)
        
        # Step 3: Generate AI response based on intent and products
        response = self._generate_response(user_message, intent_data, products)
        
        return {
            "intent": intent_data,
            "products": products,
            "response": response,
            "location": intent_data.get("location")
        }
    
    def _generate_response(self, user_message: str, intent_data: Dict[str, Any], 
                          products: List[Dict[str, Any]]) -> str:
        """Generate a natural language response based on intent and products"""
        try:
            # Prepare product information for the prompt
            product_info = ""
            if products:
                product_info = "Available products:\n"
                for i, product in enumerate(products[:5], 1):  # Limit to 5 products for the prompt
                    price = product.get("price", "")
                    price_str = f"{price} RON" if price else "Price not available"
                    product_info += f"{i}. {product['name']} - {price_str}\n"
            else:
                product_info = "No products found matching the search criteria."
            
            # Create prompt for response generation
            messages = [
                {
                    "role": "system",
                    "content": f"""You are a helpful shopping assistant for a Romanian e-commerce platform.
                    Based on the user's message and the available product information, provide a helpful response.
                    
                    User intent information:
                    - Primary Intent: {intent_data.get('primary_intent')}
                    - Product Type: {intent_data.get('product_type')}
                    - Location Interest: {intent_data.get('location')}
                    - Search Terms: {intent_data.get('search_terms')}
                    
                    {product_info}
                    
                    Keep your response conversational, helpful and focused on helping the user find or understand the products.
                    If there are products available, mention some of them specifically.
                    If no products were found, suggest alternatives or ask for more information."""
                },
                {"role": "user", "content": user_message}
            ]
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Fallback response
            if products:
                return f"I found {len(products)} products that might interest you. Would you like me to show you details?"
            else:
                return "I couldn't find any products matching your request. Could you provide more details about what you're looking for?"
