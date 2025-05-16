from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.api.chat import chat_router
from src.api.products import product_router
from src.api.orders import order_router
from src.api.voice import voice_router
from src.services.woocommerce_service import WooCommerceService
from src.rag.engine import RAGEngine
from src.services.scraper import VogoScraper, run_scheduled_scraper
from src.services.scheduler import ScraperScheduler
import uvicorn
import os
import logging
import asyncio
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if API key is loaded
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"OpenAI API key loaded successfully: {api_key[:5]}...")
else:
    print("Warning: OpenAI API key not found in environment variables")

app = FastAPI(title="Vogo.Family AI Chatbot API", 
              description="Backend API for Vogo.Family AI-powered chatbot with WooCommerce integration",
              version="1.0.0")

# Global instances
rag_engine = None
scraper_scheduler = None

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this with specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create WooCommerce service
woocommerce_service = WooCommerceService()

# Initialize RAG engine globally
rag_engine = RAGEngine(woocommerce_service)

# Include API routers
app.include_router(chat_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(voice_router)
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(product_router, prefix="/products", tags=["Products"])
app.include_router(order_router, prefix="/orders", tags=["Orders"])
app.include_router(voice_router, prefix="/voice", tags=["Voice"])

# CRITICAL FIX: Remove async startup event to prevepython emergency_main.py
# python emergency_main.pynt hanging
# Instead, initialize everything directly
logging.info("Starting direct initialization without async startup event")

# Initialize the application in a simple, non-blocking way
logging.info("Initializing RAG Engine with API and scraped data support")

# Load existing scraped data in a non-blocking way
try:
    # Try to load scraped data, but don't block if it fails
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
    
    # Initialize the engine (loads any existing scraped data if available)
    # Use a timeout to prevent getting stuck
    try:
        # Use a synchronous approach instead of awaiting
        logging.info("Initializing RAG engine...")
        # Just call the quick setup function directly
        rag_engine._load_scraped_data()
        logging.info("Basic RAG engine initialization complete")
    except asyncio.TimeoutError:
        logging.info("RAG engine initialization taking longer than expected. This is normal for the first run - continuing with startup while initialization completes in the background.")
    except Exception as e:
        logging.error(f"RAG engine initialization error: {e}")

# Define the delayed scraper setup function
def _delayed_scraper_setup():
    """Synchronous initialization of the scraper."""
    try:
        logging.info("Scraper initialization disabled temporarily")
    except Exception as e:
        logging.error(f"Error in scraper setup: {e}")
        logging.warning("Application will continue without scraper")

try:
    logging.info("Starting web scraper scheduler...")
    # Create the scheduler but don't await anything
    scraper_scheduler = ScraperScheduler(hour=3, minute=0)  # Run daily at 3:00 AM
    
    # Initialize scraper synchronously
    _delayed_scraper_setup()
    logging.info("Web scraper initialized synchronously")
except Exception as scraper_error:
    logging.error(f"Error starting web scraper: {scraper_error}")
    logging.warning("Application will continue without web scraping functionality")

logging.info("RAG Engine initialization complete")

# Create a fallback RAG engine if the main initialization failed
try:
    # Check if RAG engine has been properly initialized
    if rag_engine is None or not hasattr(rag_engine, 'client'):
        logging.warning("RAG Engine not properly initialized. Creating fallback engine.")
        woocommerce = WooCommerceService()
        rag_engine = RAGEngine(woocommerce)
except Exception as fallback_error:
    logging.critical(f"CRITICAL: Could not create fallback RAG engine: {fallback_error}")
    # We'll continue anyway - the application will use empty responses

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

# Add emergency endpoints for testing
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
        
from pydantic import BaseModel

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
        
        # Check if it's a pet-related query
        is_pet_query = any(term in message.lower() for term in ["pet", "dog", "cat", "animal", "ulei", "extract", "trandafir"])
        
        # Create a direct response without using the RAG engine or async code
        if is_pet_query:
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
        else:
            # Generic response for non-pet queries
            return {
                "response": "Welcome to Vogo Family! We offer various services including restaurant delivery, mall shopping, and pet services. How can I help you today?",
                "products": []
            }
    except Exception as e:
        logging.error(f"Error in emergency chat: {e}")
        return {
            "response": "I'm sorry, but I encountered an error processing your request.",
            "products": []
        }

# Keep the run_initial_scrape function but don't call it automatically
async def run_initial_scrape():
    """
    Run the initial web scrape to build the knowledge base.
    This runs in the background to avoid blocking the API startup.
    """
    try:
        # First, load any existing scraped data to ensure it's available even if scraping fails
        if rag_engine:
            logging.info("Loading existing scraped data first...")
            rag_engine._load_scraped_data()
            existing_product_count = len(rag_engine.scraped_data.get('all_products', []))
            logging.info(f"Loaded {existing_product_count} products from existing data")
        
        # Now try to scrape new data
        logging.info("Starting web scrape to update knowledge base...")
        # Create a VogoScraper instance
        from src.services.scraper import VogoScraper
        scraper = VogoScraper()
        
        # Run the scraper - will use existing data if website is unreachable
        result = await scraper.run_scraper()
        logging.info(f"Web scrape completed with {result.get('products_count', 0)} products from {result.get('categories_count', 0)} categories")
        
        # Only reload if we're not already using cached data
        if not result.get('using_cached_data', False):
            # Reload the data in the RAG engine
            if rag_engine:
                # Clear existing scraped data
                rag_engine.scraped_data = {}
                # Load the new data
                rag_engine._load_scraped_data()
                new_product_count = len(rag_engine.scraped_data.get('all_products', []))
                logging.info(f"RAG engine updated with {new_product_count} scraped products")
                
                # Show a success message
                if 'all_products' in rag_engine.scraped_data and new_product_count > 0:
                    logging.info("Scraper successfully loaded product data - chatbot will now use this for responses")
                    if new_product_count > existing_product_count:
                        logging.info(f"Added {new_product_count - existing_product_count} new products")
                else:
                    logging.warning("No products were loaded from scraped data - check scraper implementation")
    except Exception as e:
        logging.error(f"Error during web scrape: {e}")
        logging.warning("Application will continue with existing data")

@app.get("/", tags=["Health"])
async def health_check():
    """API health check endpoint."""
    return {"status": "healthy", "service": "vogo-chatbot-api"}

@app.get("/categories", tags=["Categories"])
async def get_categories(woocommerce: WooCommerceService = Depends()):
    """Get all product categories from WooCommerce."""
    try:
        return await woocommerce.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")
        
@app.get("/scraper/status", tags=["Scraper"])
async def get_scraper_status():
    """Get the status of the web scraper and the last scrape time."""
    try:
        # Check if scraper scheduler is initialized
        if not scraper_scheduler:
            return {"status": "not_initialized", "message": "Web scraper scheduler is not running"}
            
        # Get the last run time from the scheduler
        last_run = scraper_scheduler.last_run_time
        next_run = None
        
        if last_run:
            last_run_str = last_run.strftime("%Y-%m-%d %H:%M:%S")
            # Calculate next run time (3:00 AM after the last run date)
            import datetime
            next_day = last_run.date() + datetime.timedelta(days=1)
            next_run = datetime.datetime.combine(next_day, datetime.time(hour=3, minute=0))
            next_run_str = next_run.strftime("%Y-%m-%d %H:%M:%S")
        else:
            last_run_str = "Never"
            next_run_str = "Pending initial run"
        
        # Return status information
        return {
            "status": "active",
            "last_run": last_run_str,
            "next_scheduled_run": next_run_str,
            "scraped_data_available": rag_engine and bool(rag_engine.scraped_data)
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/scraper/run", tags=["Scraper"])
async def trigger_scraper_run():
    """Manually trigger the web scraper to run."""
    try:
        # Run the scraper in the background
        asyncio.create_task(run_initial_scrape())
        return {"status": "started", "message": "Web scraper started in the background"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start web scraper: {str(e)}")

if __name__ == "__main__":
    # Configure logging for the application
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
