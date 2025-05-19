import os
import logging
import json
import re
import traceback
from typing import List, Dict, Any, Optional, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class RAGEngine:
    """
    Retrieval-Augmented Generation (RAG) engine for AI-powered product recommendations
    and chat responses based solely on scraped data from JSON files.
    """
    
    def __init__(self, woocommerce_service=None):
        """Initialize the RAG engine with data paths and OpenAI configuration.
        
        Note: woocommerce_service parameter is kept for backwards compatibility but not used.
        """
        # OpenAI configuration
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = "gpt-3.5-turbo-0125"  # Use the latest model available
        
        # Path to scraped data directory
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scraped_data")
        logger.info(f"Using scraped data directory: {self.data_dir}")
        
        # System prompts
        self.system_prompt = """
        You are a helpful assistant for vogo.family, a Romanian multi-service app. 
        Respond to customer inquiries about the services we offer. Be friendly, helpful, and concise.
        When asked about products or services, use ONLY the product information provided in the context.
        Don't make up any products or services that aren't mentioned in the context.
        If the relevant information isn't in the context, politely inform the user that we don't have 
        that information available but they can explore options on our website.
        
        You can respond in English or Romanian depending on the language of the user's question.
        Keep responses brief and focused on the products provided in the context.
        """
        
        self.categorization_prompt = """
        Identify which categories of products or services the user is asking about.
        Return ONLY the category names as a comma-separated list without explanation or additional text.
        Available categories are:
        - restaurant (food delivery, restaurant services)
        - asian (asian food, sushi, etc)
        - italian (italian food, pasta, pizza)
        - greek (greek food, gyros, souvlaki)
        - spanish (spanish food, tapas, paella)
        - traditional (romanian traditional food)
        - vegan (vegan food options)
        - sport (sports menu, protein food)
        - mall (mall delivery, shopping)
        - travel (travel services, vacation planning)
        - suport_24h (24/7 support service)
        - vip_assistance (VIP services, concierge)
        - pregatire_scoala (school preparation, tutoring)
        - alimente_bio (organic food products)
        - produse_fara_zahar (sugar-free products)
        - controlul_greutatii (weight control products)
        - ulei_de_masline_bio (organic olive oil)
        - uleiuri_esentiale (essential oils)
        - farma (pharmacy products)
        - copii (children products and services)
        - auto_service (auto repair and maintenance services)
        """
        
        # Initialize OpenAI client
        if not self.api_key:
            logger.error("OpenAI API key not set. The chatbot will not function properly.")
            self.client = None
        else:
            self.client = OpenAI(api_key=self.api_key)
        
        # Cache for loaded data files
        self.data_cache = {}
        
        # Available files mapping
        self.available_files = {}
        
        # Load available files
        self._load_available_files()
        
    def _load_available_files(self):
        """
        Scan the data directory and identify all available JSON files for later use.
        """
        try:
            if not os.path.exists(self.data_dir):
                logger.error(f"Data directory not found: {self.data_dir}")
                return
                
            # Get all JSON files in the data directory
            self.available_files = {
                os.path.basename(f).replace(".json", ""): os.path.join(self.data_dir, f)
                for f in os.listdir(self.data_dir) 
                if f.endswith(".json") and os.path.isfile(os.path.join(self.data_dir, f))
            }
            
            logger.info(f"Found {len(self.available_files)} JSON data files")
        except Exception as e:
            logger.error(f"Error loading available files: {str(e)}")
            self.available_files = {}
    
    def _load_data_file(self, file_name: str) -> List[Dict]:
        """
        Load data from a specific JSON file with caching.
        
        Args:
            file_name: Name of the file without extension (e.g., 'meniu_italian')
            
        Returns:
            List of product dictionaries from the file or empty list if not found
        """
        # Check cache first
        if file_name in self.data_cache:
            return self.data_cache[file_name]
            
        # Try both regular and detailed versions
        for name in [file_name, f"{file_name}_detailed"]:
            if name in self.available_files:
                try:
                    file_path = self.available_files[name]
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Handle both list and single-object JSON files
                        if isinstance(data, dict):
                            data = [data]  # Convert single object to list
                        if isinstance(data, list):
                            # Cache the data
                            self.data_cache[file_name] = data
                            logger.info(f"Loaded {len(data)} items from {name}.json")
                            return data
                except Exception as e:
                    logger.error(f"Error loading {name}.json: {str(e)}")
        
        # If we got here, we couldn't load the file
        logger.warning(f"Could not load data file: {file_name}")
        return []
    
    def _format_products(self, products: List[Dict]) -> List[Dict]:
        """
        Format products from scraped data files to a consistent format.
        
        Args:
            products: List of product dictionaries from scraped data
            
        Returns:
            List of formatted product dictionaries
        """
        formatted_products = []
        
        for product in products:
            # Skip empty products
            if not (product.get("name") or product.get("title")):
                continue
                
            # Special handling for auto service data
            if product.get("category") == "Auto Service":
                formatted_product = {
                    "id": hash(product.get("url", "") + product.get("title", "")),  # Generate unique ID
                    "name": product.get("title", ""),
                    "price": product.get("price", ""),
                    "description": product.get("description", ""),
                    "short_description": product.get("description", ""),  # Auto service uses description for both
                    "permalink": product.get("url", ""),
                    "images": [],  # Auto service data doesn't include images yet
                    "categories": [{"name": "Auto Service"}]
                }
            else:
                formatted_product = {
                    "id": hash(product.get("url", "") + product.get("name", "")),  # Generate unique ID
                    "name": product.get("name", ""),
                    "price": product.get("price", ""),
                    "description": product.get("description", ""),
                    "short_description": product.get("short_description", ""),
                    "permalink": product.get("url", ""),
                    "images": [{"src": product.get("image_url", "")}] if product.get("image_url") else [],
                    "categories": [{"name": product.get("category", "")}] if product.get("category") else []
                }
            
            formatted_products.append(formatted_product)
            
        return formatted_products
    
    def _categorize_query(self, query: str) -> List[str]:
        """
        Use AI to categorize a user query into relevant product categories.
        
        Args:
            query: User message/query
            
        Returns:
            List of category names the query is about
        """
        if not self.client:
            logger.error("OpenAI client not initialized, cannot categorize query")
            return []
            
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.categorization_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,  # Low temperature for more deterministic results
                max_tokens=100
            )
            
            # Parse the categories from the response
            if response.choices and response.choices[0].message.content:
                categories_text = response.choices[0].message.content.strip()
                categories = [cat.strip().lower() for cat in categories_text.split(',')]
                return categories
                
        except Exception as e:
            logger.error(f"Error categorizing query: {str(e)}")
            
        # Default fallback - these are general categories to check
        return ["restaurant", "mall", "travel"]
    
    def _get_category_data(self, category: str) -> List[Dict]:
        """
        Get product data for a specific category.
        
        Args:
            category: Category name (e.g., 'restaurant', 'italian', 'asian')
            
        Returns:
            List of formatted product dictionaries for the category
        """
        # Map category to file name patterns
        category_file_mapping = {
            "restaurant": ["restaurant"],
            "asian": ["meniu_asia"],
            "italian": ["meniu_italian"],
            "greek": ["meniu_grecesc"],
            "spanish": ["meniu_spaniol"],
            "traditional": ["meniu_traditional"],
            "vegan": ["meniu_vegan"],
            "sport": ["meniu_sport"],
            "mall": ["mall", "mall_delivery"],
            "travel": ["travel"],
            "suport_24h": ["suport_24h"],
            "vip_assistance": ["vip_assistance"],
            "pregatire_scoala": ["pregatire_scoala_si_meditatii"],
            "alimente_bio": ["alimente_bio"],
            "produse_fara_zahar": ["produse_fara_zahar"],
            "controlul_greutatii": ["controlul_greutatii"],
            "ulei_de_masline_bio": ["ulei_de_masline_bio"],
            "uleiuri_esentiale": ["uleiuri_esentiale_alimentare_bio"],
            "farma": ["farma"],
            "copii": ["copii"],
            "auto_service": ["auto_service"]
        }
        
        # Get file names for the category
        file_names = category_file_mapping.get(category.lower(), [])
        if not file_names:
            logger.warning(f"No file mapping found for category: {category}")
            return []
            
        # Load and format products from all matching files
        all_products = []
        for file_name in file_names:
            products = self._load_data_file(file_name)
            if products:
                all_products.extend(products)
                
        # Format the products
        formatted_products = self._format_products(all_products)
        logger.info(f"Retrieved {len(formatted_products)} products for category '{category}'")
        
        return formatted_products
    
    def transcribe_audio(self, audio_data) -> Optional[str]:
        """
        Transcribe audio data using OpenAI's Whisper API.
        
        Args:
            audio_data: Audio data in bytes for transcription
            
        Returns:
            Transcribed text or None if transcription failed
        """
        if not self.client:
            logger.error("OpenAI client not initialized, cannot transcribe audio")
            return None
            
        try:
            # Use OpenAI Whisper API to transcribe the audio
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_data,
                language="ro"  # Default to Romanian but Whisper can detect the language
            )
            
            # Return the transcribed text
            return transcription.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            logger.error(traceback.format_exc())
            return None
            
    async def process_voice_request(self, audio_data) -> Dict[str, Any]:
        """
        Process a voice request by transcribing audio and generating a response.
        
        Args:
            audio_data: Audio data in bytes to be transcribed
            
        Returns:
            Dictionary with transcription, response text, and products
        """
        if not self.client:
            logger.error("OpenAI client not initialized, cannot process voice request")
            return {
                "transcription": None,
                "response": "I'm sorry, I'm having trouble accessing my voice processing service. Please try again later or type your message.",
                "products": []
            }
            
        try:
            # Step 1: Transcribe the audio
            transcription = self.transcribe_audio(audio_data)
            if not transcription:
                return {
                    "transcription": None,
                    "response": "I'm sorry, I couldn't understand your voice message. Could you please try again or type your question?",
                    "products": []
                }
                
            logger.info(f"Transcribed voice message: {transcription}")
            
            # Step 2: Process the transcribed text as a regular message
            result = await self.generate_response(transcription)
            
            # Return both the transcription and the response
            return {
                "transcription": transcription,
                "response": result.get("response", ""),
                "products": result.get("products", [])
            }
            
        except Exception as e:
            logger.error(f"Error processing voice request: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "transcription": None,
                "response": "I apologize, but I encountered an error while processing your voice message. Please try again later.",
                "products": []
            }

    async def generate_response(self, query: str) -> Dict[str, Any]:
        """Generate an AI response with relevant product recommendations based on the user query.
        
        Args:
            query: User message/query
            
        Returns:
            Dictionary with response text and relevant products
        """
        if not self.client:
            logger.error("OpenAI client not initialized, cannot generate response")
            return {
                "response": "I'm sorry, I'm having trouble connecting to my AI service. Please try again later.",
                "products": []
            }
            
        try:
            # Step 1: Categorize the query
            categories = self._categorize_query(query)
            logger.info(f"Query categorized as: {categories}")
            
            # Step 2: Retrieve relevant products for each category
            all_products = []
            for category in categories:
                products = self._get_category_data(category)
                if products:
                    all_products.extend(products)
                    
            # Limit to avoid overwhelming the context
            products_to_use = all_products[:10] if len(all_products) > 10 else all_products
            
            # Step 3: Prepare context for the AI
            context = "Available products and services for the user's query:\n"
            if products_to_use:
                category = products_to_use[0]['categories'][0]['name'] if products_to_use[0]['categories'] else 'Unknown'
                
                for idx, product in enumerate(products_to_use, 1):
                    # Get clean product name based on category
                    if category == 'Travel':
                        name = 'Travel Guide and Assistance'
                        location = product['permalink'].split('/')[-2].replace('-', ' ').title().replace('And', 'and')
                        location = location.replace('Travel Guide And Assistance ', '')
                        display_name = f"{name} - {location}"
                    elif category == 'VIP Assistance':
                        name = product['permalink'].split('/')[-2].replace('-', ' ').title()
                        if 'Vogo Personal' in name:
                            display_name = 'VOGO Personal Assistant - Monthly Subscription'
                        elif 'Servicii Avocatiale' in name:
                            display_name = 'Legal Assistance Services'
                        elif 'Personal Assistant' in name:
                            display_name = 'Personal Assistant Services'
                        else:
                            display_name = name
                    else:
                        # For other categories, clean up the product name from permalink
                        name = product['permalink'].split('/')[-2].replace('-', ' ').title()
                        display_name = name
                    
                    context += f"\n{idx}. {display_name}"
                    context += f"\n   Category: {category}"
                    context += f"\n   Price: {product['price']}"
                    if product['description'] or product['short_description']:
                        context += f"\n   Description: {product['short_description'] or product['description'][:150]}"
                    context += "\n"
                
                # Add category-specific guidance for the AI
                context += "\nPlease provide a helpful response about our available services. "
                
                # Food and Restaurant Services
                if category in ['Restaurant', 'Meniu Asia', 'Meniu Italian', 'Meniu Grecesc', 
                              'Meniu Spaniol', 'Meniu Traditional', 'Meniu Vegan', 'Meniu Sport', 'Meniu Arabesc']:
                    context += "Describe our food delivery options and menu specialties. "
                    context += "Mention cuisine type, special dishes, and dietary options. "
                
                # Travel and Support Services
                elif category == 'Travel':
                    context += "Mention the available destinations and travel guide services. "
                    context += "Highlight our local expertise and assistance features. "
                elif category == 'Suport 24h':
                    context += "Explain our 24/7 support services and how we assist customers. "
                elif category == 'VIP Assistance':
                    context += "Highlight our premium personal assistance and professional services. "
                
                # Shopping and Products
                elif category in ['Mall', 'Mall Delivery', 'Magazine']:
                    context += "Explain our shopping and delivery services. "
                    context += "Mention delivery areas and shopping convenience. "
                elif category == 'Alimente Bio':
                    context += "Describe our organic food products and their health benefits. "
                elif category == 'Produse Fara Zahar':
                    context += "Highlight our sugar-free products and their health benefits. "
                elif category == 'Controlul Greutatii':
                    context += "Explain our weight management products and their benefits. "
                elif category == 'Ulei De Masline Bio':
                    context += "Describe our organic olive oil products and their quality. "
                elif category == 'Uleiuri Esentiale Alimentare Bio':
                    context += "Explain our organic essential oils and their uses. "
                
                # Health and Education
                elif category == 'Farma':
                    context += "Describe our pharmacy products and health-related services. "
                elif category == 'Pregatire Scoala Si Meditatii':
                    context += "Explain our tutoring and educational support services. "
                elif category == 'Copii':
                    context += "Describe our children's products and services. "
                elif category == 'Auto Service':
                    context += "Explain our auto repair and maintenance services. "
                    context += "Include information about service locations and availability. "
                
                context += "\nInclude pricing information where available. "
                context += "Be enthusiastic and welcoming! "
                context += "If asked about availability or delivery, suggest contacting our support team for details."

            else:
                context += "\nNo specific products found for this query.\n"
                
            # Step 4: Generate the response
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": f"Context:\n{context}\n\nUser query: {query}"}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract the response text
            response_text = response.choices[0].message.content if response.choices else ""
            
            return {
                "response": response_text,
                "products": products_to_use
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "response": "I apologize, but I encountered an error while processing your request. Please try again later.",
                "products": []
            }
            
    def initialize(self) -> bool:
        """
        Initialize the RAG engine by loading available JSON data files.
        This should be called during application startup.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            logger.info("Initializing RAG Engine...")
            
            # Reload available files in case new ones were added
            self._load_available_files()
            
            # Check if OpenAI API is properly configured
            if not self.api_key or not self.client:
                logger.error("OpenAI API key not configured. The chatbot will have limited functionality.")
                return False
                
            # Check if data directory exists and contains files
            if not os.path.exists(self.data_dir):
                logger.error(f"Data directory not found: {self.data_dir}")
                return False
                
            file_count = len(self.available_files)
            if file_count == 0:
                logger.error("No JSON data files found in the data directory")
                return False
                
            logger.info(f"RAG Engine initialized successfully with {file_count} available data files")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing RAG Engine: {str(e)}")
            logger.error(traceback.format_exc())
            return False
