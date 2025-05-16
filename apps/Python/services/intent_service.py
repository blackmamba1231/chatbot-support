"""
Intent Service
This module handles intent detection using OpenAI's language models.
"""

import os
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI

logger = logging.getLogger(__name__)

# Intent to category mapping
INTENT_TO_CATEGORY = {
    "mall_delivery": 223,
    "kids_activities": 563,
    "bio_food": 346,
    "antipasti": 347,
    "pet_care": 547,
    "allergies": 548
}

class IntentService:
    """Service for detecting user intent from natural language"""
    
    def __init__(self, openai_client=None):
        """Initialize the intent detection service"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_client and not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = openai_client or OpenAI(api_key=self.api_key)
        logger.info("Intent service initialized")
    
    def detect_intent(self, message: str) -> Dict[str, Any]:
        """
        Detect intent from user message
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary containing intent information
        """
        try:
            logger.info(f"Detecting intent for message: {message}")
            
            # Define available intents and locations
            system_prompt = """You are an intent detection system for a WooCommerce shopping assistant.
            Extract the following information from the user message:
            1. primary_intent: One of [browse_products, search_product, product_info, order_product, get_location, customer_support, general_query]
            2. location: Any Romanian city or shopping mall mentioned (Alba Iulia, Arad, Miercurea Ciuc, Vaslui, Târgu Mureș, Suceava, Târgu-Jiu)
            3. product_type: One of [mall_delivery, kids_activities, bio_food, antipasti, pet_care, allergies]
            4. search_terms: Specific product terms or keywords they're searching for
            
            Respond ONLY with a valid JSON object containing these fields. If a field can't be determined, use null.
            """
            
            # Call OpenAI API for intent detection
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            intent_data = json.loads(response.choices[0].message.content)
            
            # Add confidence score
            intent_data["confidence"] = 0.9
            
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
    
    def analyze_sentiment(self, message: str) -> Dict[str, Any]:
        """
        Analyze sentiment from user message
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary containing sentiment information
        """
        try:
            logger.info(f"Analyzing sentiment for message: {message}")
            
            # Call OpenAI API for sentiment analysis
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Analyze the sentiment of the following message. Respond with a JSON object containing 'sentiment' (positive, negative, or neutral) and 'intensity' (0 to 1)."},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            sentiment_data = json.loads(response.choices[0].message.content)
            
            logger.info(f"Detected sentiment: {sentiment_data}")
            return sentiment_data
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            # Return default sentiment on error
            return {
                "sentiment": "neutral",
                "intensity": 0.5
            }
    
    def extract_entities(self, message: str) -> Dict[str, List[str]]:
        """
        Extract named entities from user message
        
        Args:
            message: The user's message
            
        Returns:
            Dictionary containing lists of different entity types
        """
        try:
            logger.info(f"Extracting entities from message: {message}")
            
            # Call OpenAI API for entity extraction
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract named entities from the following message. Identify locations, product types, brands, and quantities. Respond with a JSON object with these categories as keys and arrays of found entities as values."},
                    {"role": "user", "content": message}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            entities = json.loads(response.choices[0].message.content)
            
            logger.info(f"Extracted entities: {entities}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            # Return empty entities on error
            return {
                "locations": [],
                "product_types": [],
                "brands": [],
                "quantities": []
            }
