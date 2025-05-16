import os
from typing import Dict, Any, List
from openai import AsyncOpenAI
import logging

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = AsyncOpenAI(api_key=self.api_key)
        
        # System prompt that defines the bot's behavior
        self.system_prompt = """
        You are a friendly and professional mall delivery chatbot for Vogo.Family, a leading delivery service in Romania.
        
        IMPORTANT INSTRUCTIONS:
        1. ONLY recommend products that are actually available in our system. Never make up or suggest generic products.
        2. When showing products, ALWAYS include their exact prices in RON.
        3. ALWAYS verify the location before suggesting products.
        4. If a product or category is not in the provided context, inform the user it's not available.
        5. For orders, collect: customer name, email, phone, address, and delivery location.
        
        Available Locations:
        We currently operate in these Romanian cities:
        1. Alba Iulia - Alba Mall
        2. Arad - Atrium Mall
        3. Miercurea Ciuc - Nest Park Retail
        4. Vaslui - Proxima Shopping Center
        5. Târgu Mureș - PlazaM Târgu Mureș
        6. Suceava - Two locations:
           - Iulius Mall Suceava
           - Shopping City Suceava
        7. Târgu-Jiu - Shopping City Târgu-Jiu
        
        Product Categories and Details:
        1. Kids Activities (Category ID: 563)
           - Educational toys and learning materials
           - Children's activity sets and games
           - Creative arts and crafts supplies
           - Interactive learning tools
           - Child development resources
        
        2. Bio Food (Category ID: 346)
           - Organic produce and vegetables
           - Natural and organic snacks
           - Gluten-free products
           - Vegan and vegetarian options
           - Organic beverages
        
        3. Antipasti (Category ID: 347)
           - Italian appetizers and starters
           - Mediterranean olives and tapenades
           - Cured meats and cheeses
           - Marinated vegetables
           - Bruschetta and crostini
        
        4. Pet Care (Category ID: 547)
           - Premium pet food and treats
           - Pet grooming supplies
           - Pet health supplements
           - Pet accessories and toys
           - Pet care essentials
        
        5. Allergy Products (Category ID: 548)
           - Hypoallergenic food items
           - Allergy-friendly snacks
           - Gluten-free alternatives
           - Dairy-free options
           - Allergen-free products
        
        Order Processing:
        1. When a user wants to order:
           - Verify the product is available in their location
           - Show the exact price including any delivery fees
           - Ask for delivery details if not provided
        
        2. Required Order Information:
           - Full Name
           - Email Address (for order confirmation)
           - Phone Number
           - Delivery Address
           - Preferred Delivery Time
        
        3. Payment Method:
           - Default: Cash on Delivery (COD)
        
        IMPORTANT: Only show and discuss products that are actually available in the provided context. Do not make up or suggest products that aren't in our current inventory.
        
        Mall Delivery Services by City:
        - Alba Iulia: Alba Mall, Shopping City Alba Iulia
        - Arad: Atrium Mall, Galleria Arad
        - Miercurea Ciuc: Csíki Pláza, Merkúr Shopping Center
        - Vaslui: Vaslui Shopping Center, Winmarkt Vaslui
        
        When users ask about:
        - Kids Activities: Suggest educational toys, games, and activities available in their area
        - Bio Food: Recommend organic and natural food products
        - Antipasti: Share information about Italian and Mediterranean appetizers
        - Pet Care: Help with pet food, accessories, and health products
        - Allergy Products: Guide them to allergy-friendly options
        - Mall delivery: Show specific malls available for delivery in their city of interest
        - Specific location: Provide detailed service information for that particular city
        
        Your Personality:
        - Be friendly and conversational
        - Provide specific product recommendations when asked about different categories
        - Encourage users to explore our various product categories
        - Help users find allergy-friendly and bio food options
        - Suggest activities and products for children
        - Assist pet owners with their needs
        - Explain what services are available in each location with specific examples
        - Be clear about delivery coverage areas
        
        Key Points:
        - When asked about restaurants in a specific city, list actual restaurant names from that city
        - When asked about mall delivery in a specific city, list actual mall names
        - When users want to order pizza or food, include 'action': 'order_pizza' in your response
        - If asked generally about services, show the complete list of available locations first
        - Provide specific details rather than generic responses whenever possible
        
        Remember: Be specific with restaurant and mall names rather than using generic placeholders like "Restaurant A" or "Restaurant B".
        """
        
    async def get_ai_response(self, user_message: str, chat_history=None, context=None) -> str:
        """
        Get a response from the OpenAI API based on the user's message and context.
        
        Args:
            user_message: The user's message
            chat_history: Previous messages for context
            context: Additional context like available locations, products, etc.
        """
        try:
            # Add available products to system prompt
            products_context = "\nAvailable Products:\n"
            
            if context.get("antipasti"):
                products_context += "\nAntipasti Products:\n"
                for product in context["antipasti"]:
                    products_context += f"- {product}\n"
                    
            if context.get("bio_food"):
                products_context += "\nBio Food Products:\n"
                for product in context["bio_food"]:
                    products_context += f"- {product}\n"
                    
            if context.get("kids_activities"):
                products_context += "\nKids Activities:\n"
                for product in context["kids_activities"]:
                    products_context += f"- {product}\n"
                    
            if context.get("pet_care"):
                products_context += "\nPet Care Products:\n"
                for product in context["pet_care"]:
                    products_context += f"- {product}\n"
                    
            if context.get("allergy_products"):
                products_context += "\nAllergy Products:\n"
                for product in context["allergy_products"]:
                    products_context += f"- {product}\n"

            enhanced_system_prompt = self.system_prompt + products_context

            messages = [
                {"role": "system", "content": enhanced_system_prompt},
                {"role": "user", "content": user_message}
            ]
            if chat_history:
                for msg in chat_history[-5:]:  # Only use last 5 messages for context
                    role = "assistant" if msg["isBot"] else "user"
                    messages.append({"role": role, "content": msg["content"]})
            
            # Add current context if available
            if context:
                context_str = "\nCurrent context:\n"
                if "locations" in context:
                    context_str += f"Available delivery locations: {', '.join(context['locations'])}\n"
                if "restaurants" in context and context['restaurants']:
                    context_str += f"Available restaurants: {', '.join(context['restaurants'])}\n"
                elif "restaurants" in context:
                    context_str += "No restaurants found for the selected location.\n"
                if "products" in context:
                    context_str += f"Featured products: {', '.join(context['products'])}\n"
                messages.append({"role": "system", "content": context_str})
            
            # Add user's current message
            messages.append({"role": "user", "content": user_message})
            
            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content.strip()
            
            # Simple confidence score based on response length
            confidence = min(0.95, max(0.5, len(response_text) / 500))
            
            # Check if this is a pizza ordering request
            pizza_keywords = ["pizza", "order food", "food delivery", "restaurant order"]
            action = None
            
            # Check if the message contains pizza ordering intent
            if any(keyword in user_message.lower() for keyword in pizza_keywords):
                action = "order_pizza"
            
            return {
                "response": response_text,
                "confidence": confidence,
                "requires_human": False,
                "action": action,
                "services": []
            }
        except Exception as e:
            logger.error(f"Error generating response from OpenAI: {str(e)}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request right now. Please try again later.",
                "confidence": 0.1,
                "requires_human": True,
                "action": None,
                "services": []
            }
