#!/usr/bin/env python3
"""
WooCommerce AI Assistant with Voice Integration
This script implements an AI-powered service that integrates with WooCommerce API
to fetch products and services, with voice recognition capabilities.
"""

import os
import json
import time
import requests
from requests_oauthlib import OAuth1
from typing import Dict, Any, List, Optional, Tuple
import logging
import argparse
import dotenv
from pathlib import Path
from openai import OpenAI

# Import services
from services.woocommerce_service import WooCommerceService
from services.voice_service import VoiceService
from services.intent_service import IntentService
from services.response_service import ResponseService

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def load_environment():
    """Load environment variables from .env file"""
    # Try to load from different possible locations
    env_paths = [
        Path(__file__).parent / ".env",
        Path(__file__).parent.parent.parent / "apps" / "backend" / ".env"
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            logger.info(f"Loading environment from {env_path}")
            dotenv.load_dotenv(env_path)
            return True
    
    logger.warning("No .env file found, using environment variables from system")
    return False

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="WooCommerce AI Assistant with Voice Integration")
    parser.add_argument("--voice", action="store_true", help="Enable voice input")
    parser.add_argument("--text", type=str, help="Text input to process")
    parser.add_argument("--list-products", action="store_true", help="List all available products")
    parser.add_argument("--list-categories", action="store_true", help="List all available categories")
    parser.add_argument("--fetch-all", action="store_true", help="Fetch and display both products and categories")
    parser.add_argument("--category-id", type=int, help="Get products from a specific category ID")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    return parser.parse_args()

def initialize_services():
    """Initialize all required services"""
    # Initialize WooCommerce service
    woocommerce_service = WooCommerceService(
        base_url=os.environ.get("WP_API_URL", "https://vogo.family"),
        consumer_key=os.environ.get("WP_CONSUMER_KEY", "ck_91e6fa3aac7b5c40ac5a9a1ec0743c0791472e62"),
        consumer_secret=os.environ.get("WP_CONSUMER_SECRET", "cs_28bfe71efc2e7f71269236e79d47a896b96305a2")
    )
    
    # Pre-cache products and categories for faster access
    logger.info("Pre-fetching products and categories...")
    woocommerce_service.get_products()  # Cache products
    woocommerce_service.get_categories()  # Cache categories
    
    # Initialize OpenAI client
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    
    # Initialize voice service
    voice_service = VoiceService(openai_client)
    
    # Initialize intent service
    intent_service = IntentService(openai_client)
    
    # Initialize response service
    response_service = ResponseService(openai_client)
    
    return {
        "woocommerce": woocommerce_service,
        "voice": voice_service,
        "intent": intent_service,
        "response": response_service
    }

def list_products(services):
    """List all available products"""
    woocommerce = services["woocommerce"]
    products = woocommerce.get_products()
    
    if products:
        print(f"\nFound {len(products)} products:\n")
        for i, product in enumerate(products[:20], 1):  # Show first 20 products
            name = product.get("name", "Unknown")
            price = product.get("price", "N/A")
            print(f"{i}. {name} - {price} RON")
        
        if len(products) > 20:
            print(f"... and {len(products) - 20} more products")
    else:
        print("No products found")

def list_categories(services):
    """List all available categories"""
    woocommerce = services["woocommerce"]
    categories = woocommerce.get_categories()
    
    if categories:
        print(f"\nFound {len(categories)} categories:\n")
        for i, category in enumerate(categories, 1):
            name = category.get("name", "Unknown")
            id = category.get("id", "N/A")
            product_count = category.get("count", 0)
            slug = category.get("slug", "")
            print(f"{i}. {name} (ID: {id}, Slug: {slug}) - {product_count} products")
            
            # For important categories, show sample products
            if id in [223, 563, 346, 347, 547, 548]:  # Our key category IDs
                print("   Sample products:")
                category_products = woocommerce.get_products(category=id, limit=3)
                if category_products:
                    for j, product in enumerate(category_products[:3], 1):
                        print(f"      {j}. {product.get('name', 'Unknown')} - {product.get('price', 'N/A')} RON")
                else:
                    print("      No products found in this category")
                print()
    else:
        print("No categories found")

def handle_text_input(text, services, speak_responses=False):
    """Process text input and generate a response"""
    intent_service = services["intent"]
    response_service = services["response"]
    voice_service = services["voice"]
    woocommerce = services["woocommerce"]
    
    # Detect intent
    intent_data = intent_service.detect_intent(text)
    
    # Get relevant products based on intent
    products = []
    if intent_data.get("product_type"):
        product_type = intent_data.get("product_type")
        location = intent_data.get("location")
        
        if product_type == "mall_delivery":
            result = woocommerce.get_mall_delivery_services(location)
            if result.get("status") == "success":
                products = result.get("services", [])
        elif product_type == "kids_activities":
            result = woocommerce.get_kids_activities(location)
            if result.get("status") == "success":
                products = result.get("activities", [])
        elif product_type == "bio_food":
            result = woocommerce.get_bio_food(location)
            if result.get("status") == "success":
                products = result.get("food_items", [])
        elif product_type == "antipasti":
            result = woocommerce.get_antipasti(location)
            if result.get("status") == "success":
                products = result.get("antipasti_items", [])
    
    # Generate response
    response = response_service.generate_response(text, intent_data, products)
    
    # Print the response
    print("\n✨ AI Assistant Response:")
    print(response)
    
    # Use text-to-speech if enabled
    if speak_responses:
        print("🔊 Speaking response...")
        voice_service.speak_text(response)
    
    # Display products if available
    if products:
        print(f"\nFound {len(products)} related products:")
        for i, product in enumerate(products[:5], 1):
            name = product.get("name", "Unknown")
            price = product.get("price", "N/A")
            print(f"{i}. {name} - {price} RON")

def run_interactive(services):
    """Run the assistant in interactive mode"""
    voice_service = services["voice"]
    print("\n🤖 WooCommerce AI Assistant with Voice Integration")
    print("--------------------------------------------------")
    print("Type your question about products and services, or use these special commands:")
    print("  'voice' - Use voice input instead of typing")
    print("  'speak' - Toggle text-to-speech responses ON/OFF")
    print("  'exit'  - Quit the assistant")
    print("--------------------------------------------------\n")
    
    # Settings
    speak_responses = False
    
    while True:
        user_input = input("\n👤 You: ")
        
        if user_input.lower() == "exit":
            print("Goodbye! 👋")
            break
            
        elif user_input.lower() == "speak":
            speak_responses = not speak_responses
            status = "ON" if speak_responses else "OFF"
            print(f"🔊 Text-to-speech is now {status}")
            continue
        
        elif user_input.lower() == "voice":
            print("🎤 Listening... (speak now)")
            audio_text = voice_service.listen_and_transcribe()
            print(f"🔊 You said: {audio_text}")
            handle_text_input(audio_text, services, speak_responses)
        else:
            handle_text_input(user_input, services, speak_responses)

def main():
    """Main function"""
    # Load environment variables
    load_environment()
    
    # Parse arguments
    args = parse_args()
    
    # Initialize services
    services = initialize_services()
    
    # Handle different modes
    if args.fetch_all:
        print("\n===== FETCHING ALL PRODUCTS AND CATEGORIES =====\n")
        list_categories(services)
        list_products(services)
    elif args.category_id:
        print(f"\n===== PRODUCTS IN CATEGORY ID {args.category_id} =====\n")
        woocommerce = services["woocommerce"]
        category_products = woocommerce.get_products(category=args.category_id)
        if category_products:
            print(f"Found {len(category_products)} products in category {args.category_id}:")
            for i, product in enumerate(category_products[:20], 1):
                print(f"{i}. {product.get('name', 'Unknown')} - {product.get('price', 'N/A')} RON")
            if len(category_products) > 20:
                print(f"... and {len(category_products) - 20} more products")
        else:
            print(f"No products found in category {args.category_id}")
    elif args.list_products:
        list_products(services)
    elif args.list_categories:
        list_categories(services)
    elif args.text:
        handle_text_input(args.text, services)
    elif args.interactive:
        run_interactive(services)
    else:
        run_interactive(services)

if __name__ == "__main__":
    main()
