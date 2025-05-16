from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api.chat import chat_router
from src.api.products import product_router
from src.api.orders import order_router
from src.api.voice import voice_router
from src.services.woocommerce_service import WooCommerceService
from src.rag.engine import RAGEngine
from src.services.scraper import VogoScraper
from pydantic import BaseModel
import uvicorn
import os
import json
import logging
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"OpenAI API key loaded successfully: {api_key[:5]}...")
else:
    print("Warning: OpenAI API key not found in environment variables")

# Initialize application
app = FastAPI(title="Vogo.Family AI Chatbot API", 
              description="Backend API for Vogo.Family AI-powered chatbot with WooCommerce integration",
              version="1.0.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services - just create a dummy WooCommerce service but don't actually use it
woocommerce_service = WooCommerceService()
rag_engine = RAGEngine(woocommerce_service)

# Immediately load scraped data instead of trying to fetch from WooCommerce
rag_engine.use_woocommerce = False  # Disable WooCommerce API calls
try:
    # Load the scraped data directly from files
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data")
    logging.info(f"Loading scraped data from {data_dir}")
    rag_engine._load_scraped_data()
    logging.info("Successfully loaded scraped data from files")
except Exception as e:
    logging.error(f"Error loading scraped data: {e}")
    logging.warning("Will use fallback data for responses")

# Include API routers
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(voice_router, prefix="/voice", tags=["Voice"])

# Initialize the basic components without async to avoid hanging
logging.info("Starting direct initialization without async startup event")

# Load existing scraped data in a non-blocking way
try:
    # Try to load scraped data
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data")
    all_products_path = os.path.join(data_dir, "all_products.json")
    
    if os.path.exists(all_products_path):
        with open(all_products_path, 'r', encoding='utf-8') as f:
            all_products = json.load(f)
            if hasattr(rag_engine, 'scraped_data'):
                rag_engine.scraped_data["all_products"] = all_products
                logging.info(f"Direct loading: Loaded {len(all_products)} products")
except Exception as e:
    logging.error(f"Error loading scraped data directly: {e}")

# Simple function to check server health without any async operations
def quick_scraper_setup():
    """
    Emergency replacement for the async scraper setup.
    This is a direct synchronous function to avoid blocking issues.
    """
    try:
        logging.info("EMERGENCY MODE: Quick non-blocking scraper setup")
        
        # Just check if data exists - don't try to scrape
        scraper = VogoScraper()
        data_path = os.path.join(scraper.data_dir, "all_products.json")
        
        if os.path.exists(data_path):
            logging.info(f"Scraper data exists at {data_path} - using existing data only")
        else:
            logging.warning(f"No scraper data found at {data_path} - endpoints will use fallback data")
            
    except Exception as e:
        logging.error(f"Error in quick scraper setup: {e}")

# Run the quick setup instead of scheduling it
quick_scraper_setup()

# Emergency endpoints for testing and basic functionality
@app.get("/")
def root():
    """Basic root endpoint."""
    return {"status": "ok", "service": "Vogo.Family AI Chatbot API"}

@app.get("/emergency-health")
def emergency_health_check():
    """Emergency health check endpoint that uses no async code."""
    return {"status": "ok", "mode": "emergency"}

@app.get("/emergency-pet-data")
def emergency_pet_data():
    """Emergency endpoint to return pet data without async operations."""
    try:
        # Direct file access without rag_engine
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data")
        pet_path = os.path.join(data_dir, "uleiuri_esentiale_alimentare_bio_detailed.json")
        
        if os.path.exists(pet_path):
            with open(pet_path, 'r', encoding='utf-8') as f:
                pet_data = json.load(f)
            return {"status": "ok", "data_count": len(pet_data), "sample": pet_data[0] if pet_data else None}
        return {"status": "no_data", "message": "No pet data found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Request model for emergency chat
class EmergencyChatRequest(BaseModel):
    message: str
    user_id: str = None
    session_id: str = None

@app.post("/emergency-chat")
def emergency_chat(request: EmergencyChatRequest):
    """Emergency non-async chat endpoint."""
    try:
        # Get the message from the request
        message = request.message
        
        # Categorize the query
        # Food query keywords
        food_keywords = ["food", "restaurant", "pizza", "delivery", "meal", "lunch", "dinner", "breakfast"]
        # Pet query keywords
        pet_keywords = ["pet", "dog", "cat", "animal", "ulei", "extract", "trandafir", "veterinary"]
        # Spa keywords
        spa_keywords = ["spa", "massage", "wellness", "relaxation", "facial", "treatment", "temple", "tao"]
        
        is_food_query = any(term in message.lower() for term in food_keywords)
        is_pet_query = any(term in message.lower() for term in pet_keywords)
        is_spa_query = any(term in message.lower() for term in spa_keywords)
        
        # Create a direct response without using the RAG engine or async code
        if is_food_query and not is_pet_query and not is_spa_query:
            # This is a pure food delivery query
            # Create a proper food delivery response with basic restaurant info
            return {
                "response": "We offer food delivery services from various restaurants including pizza, Italian cuisine, traditional Romanian food, and Asian cuisine. For current menu items, prices, and specific restaurant options, please visit our website.",
                "products": [
                    {
                        "id": 9501,
                        "name": "Pizza Delivery Service",
                        "price": "45.00",
                        "description": "Fast pizza delivery from local restaurants to your door in under 30 minutes.",
                        "categories": [{"name": "Restaurant Delivery"}]
                    },
                    {
                        "id": 9502,
                        "name": "Italian Cuisine Delivery",
                        "price": "55.00",
                        "description": "Authentic Italian dishes including pasta, risotto, and more.",
                        "categories": [{"name": "Restaurant Delivery"}]
                    },
                    {
                        "id": 9503,
                        "name": "Romanian Traditional Food",
                        "price": "50.00",
                        "description": "Traditional Romanian dishes including sarmale, mici, and ciorba.",
                        "categories": [{"name": "Restaurant Delivery"}]
                    }
                ]
            }
        elif is_pet_query and not is_food_query:
            # This is a pet-related query
            # Try to get some pet data
            try:
                data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data")
                pet_path = os.path.join(data_dir, "uleiuri_esentiale_alimentare_bio_detailed.json")
                
                if os.path.exists(pet_path):
                    with open(pet_path, 'r', encoding='utf-8') as f:
                        pet_data = json.load(f)
                    
                    # Return some pet products
                    sample_products = pet_data[:3] if len(pet_data) >= 3 else pet_data
                    return {
                        "response": "We offer various pet products including essential oils like the Extract de trandafir alimentar. Here are some of our available products.",
                        "products": sample_products
                    }
            except Exception as inner_e:
                logging.error(f"Error accessing pet data: {inner_e}")
            
            # Fallback for pet queries
            return {
                "response": "We offer various pet products and services including premium pet food, grooming, and veterinary services. We also have essential oils that can be used for pets.",
                "products": []
            }
        elif is_spa_query:
            # This is a spa-related query
            return {
                "response": "We offer various spa and wellness services including the Tao Temple Spa in Bucharest. Our services include massages, facial treatments, and various relaxation therapies. Please visit our website for more details on available services and booking.",
                "products": [
                    {
                        "id": 9601,
                        "name": "Tao Temple Spa Bucuresti",
                        "price": "380.00",
                        "description": "Premium spa services with authentic Asian-inspired treatments and massages.",
                        "categories": [{"name": "Spa & Wellness"}]
                    }
                ]
            }
        else:
            # Generic response for other queries
            return {
                "response": "Welcome to Vogo Family! We offer various services including restaurant delivery, mall shopping, pet services, and spa & wellness treatments. How can I help you today?",
                "products": []
            }
    except Exception as e:
        logging.error(f"Error in emergency chat: {e}")
        return {
            "response": "I'm sorry, but I encountered an error processing your request.",
            "products": []
        }

if __name__ == "__main__":
    # Configure logging for the application
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    uvicorn.run("emergency_main:app", host="0.0.0.0", port=8000, reload=True)
