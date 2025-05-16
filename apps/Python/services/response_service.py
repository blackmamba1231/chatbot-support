"""
Response Service
This module generates natural language responses based on user intent and available products.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class ResponseService:
    """Service for generating natural language responses"""
    
    def __init__(self, openai_client=None):
        """Initialize the response service"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_client and not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = openai_client or OpenAI(api_key=self.api_key)
        logger.info("Response service initialized")
        
        # System prompt that defines the bot's behavior
        self.system_prompt = """
        You are a friendly and professional mall delivery chatbot for Vogo.Family, a leading delivery service in Romania.
        
        IMPORTANT INSTRUCTIONS:
        1. ONLY recommend products that are actually available in our system. Never make up or suggest generic products.
        2. When showing products, ALWAYS include their exact prices in RON.
        3. ALWAYS verify the location before suggesting products.
        4. If a product or category is not in the provided context, inform the user it's not available.
        5. For orders, collect: customer name, email, phone, address, and delivery location.
        
        Available Mall Delivery Locations:
        We currently operate in these Romanian cities (all mall deliveries cost 99 RON):
        
        1. Alba Iulia:
           - Carolina Mall
           - Mall Alba
           
        2. Arad:
           - Atrium Mall
           
        3. Bacău:
           - Arena Mall Bacău
           - Hello Shopping Park
           
        4. Baia Mare:
           - Vivo Baia Mare
           
        5. Bistrița:
           - B1 Retail Park
           - Bistrița Retail Park
           
        6. Botoșani:
           - Uvertura Mall
           - Botoșani Shopping Center
           
        7. Brașov:
           - Unirea Shopping Center
           - AFI Brașov
           - Eliana Mall
           - Star
           - Coresi Shopping Resort
           - Magnolia Shopping Center
           
        8. Brăila:
           - Brăila Mall
           
        9. București:
           - Plaza Romania
           - Promenada Mall
           - Sun Plaza
           - Băneasa Shopping City
           - AFI Cotroceni
           
        10. Buzău:
            - Shopping City Buzau
            
        11. Cluj-Napoca:
            - Iulius Mall Cluj
            
        12. Ploiești:
            - AFI Ploiesti
            
        13. Suceava:
            - Shopping City Suceava
            
        14. Timișoara:
            - Bega Shopping Center
            
        15. Târgu Mureș:
            - Shopping City
        
        Product Categories:
        1. Mall Delivery (223) - Delivery services from shopping malls
        2. Kids Activities (563) - Educational toys and games for children
        3. Bio Food (346) - Organic produce and natural food products
        4. Antipasti (347) - Italian appetizers and Mediterranean specialties
        5. Pet Care (547) - Products for pets
        6. Allergies (548) - Allergy-friendly products
        
        Your responses should be:
        - Friendly and conversational
        - Specific about products, including exact prices
        - Clear about delivery locations and availability
        - Helpful in guiding users to find what they need
        - Never make up information not provided in the context
        """
    
    def generate_response(self, user_message: str, intent_data: Dict[str, Any], 
                          products: List[Dict[str, Any]]) -> str:
        """
        Generate a natural language response based on user message, intent, and products
        
        Args:
            user_message: The user's message
            intent_data: Intent information from intent detection
            products: List of relevant products
            
        Returns:
            Natural language response
        """
        try:
            logger.info("Generating response...")
            
            # Prepare product information
            product_context = "Available products:\n"
            if products:
                for i, product in enumerate(products[:5], 1):
                    name = product.get("name", "Unknown")
                    price = product.get("price", "N/A")
                    description = product.get("short_description", "") or product.get("description", "")
                    product_context += f"{i}. {name} - {price} RON\n"
                    if description:
                        # Truncate long descriptions
                        if len(description) > 100:
                            description = description[:100] + "..."
                        product_context += f"   Description: {description}\n"
            else:
                product_context = "No products found matching the criteria."
            
            # Format intent information
            intent_context = f"""
            User intent information:
            - Primary intent: {intent_data.get('primary_intent', 'unknown')}
            - Product category: {intent_data.get('product_type', 'unknown')}
            - Location: {intent_data.get('location', 'unknown')}
            - Search terms: {intent_data.get('search_terms', 'none')}
            """
            
            # Combine all context
            full_context = f"{self.system_prompt}\n\n{intent_context}\n\n{product_context}"
            
            # Generate response
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": full_context},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.7,
                max_tokens=300
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"Generated response: {result[:50]}...")
            return result
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Return fallback response
            if products:
                return f"I found {len(products)} products that might interest you. Would you like me to tell you more about them?"
            else:
                return "I couldn't find any products matching your request. Could you provide more details about what you're looking for?"
    
    def explain_product(self, product: Dict[str, Any]) -> str:
        """
        Generate a detailed explanation of a product
        
        Args:
            product: Product information
            
        Returns:
            Natural language explanation
        """
        try:
            # Extract product information
            name = product.get("name", "Unknown product")
            price = product.get("price", "N/A")
            description = product.get("description", "No description available.")
            
            # Format the product information
            product_info = f"""
            Product: {name}
            Price: {price} RON
            Description: {description}
            """
            
            # Generate explanation
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful shopping assistant. Explain the product in a clear, concise way highlighting its key features and benefits."},
                    {"role": "user", "content": f"Please explain this product:\n{product_info}"}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error explaining product: {str(e)}")
            # Return basic information
            return f"{product.get('name', 'Unknown product')} - {product.get('price', 'N/A')} RON: {product.get('short_description', 'No description available.')}"
    
    def generate_order_confirmation(self, order_data: Dict[str, Any]) -> str:
        """
        Generate an order confirmation message
        
        Args:
            order_data: Order information
            
        Returns:
            Order confirmation message
        """
        try:
            # Extract order information
            order_id = order_data.get("id", "Unknown")
            total = order_data.get("total", "0.00")
            items = order_data.get("line_items", [])
            shipping = order_data.get("shipping", {})
            
            # Format items
            items_text = ""
            for item in items:
                items_text += f"- {item.get('name', 'Unknown item')} x{item.get('quantity', 1)} - {item.get('total', '0.00')} RON\n"
            
            # Format shipping address
            address = shipping.get("address", {})
            address_text = f"{address.get('address_1', '')}, {address.get('city', '')}, {address.get('postcode', '')}"
            
            # Build order summary
            order_summary = f"""
            Order ID: {order_id}
            Items:
            {items_text}
            Total: {total} RON
            Shipping Address: {address_text}
            """
            
            # Generate confirmation message
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful shopping assistant. Generate a friendly order confirmation message that thanks the customer and summarizes their order."},
                    {"role": "user", "content": f"Generate an order confirmation message for this order:\n{order_summary}"}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating order confirmation: {str(e)}")
            # Return basic confirmation
            return f"Thank you for your order! Your order number is {order_data.get('id', 'Unknown')} and the total is {order_data.get('total', '0.00')} RON. You'll receive a confirmation email shortly."
