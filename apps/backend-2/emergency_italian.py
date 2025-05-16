"""
Emergency endpoint for Italian menu data.
This creates a separate FastAPI app with a dedicated endpoint just for testing Italian menu retrieval.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
import logging
import uvicorn
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Italian Menu Emergency API", 
              description="Emergency API for testing Italian menu data",
              version="1.0.0")

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Path to scraped data
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "scraped_data")

class ItalianMenuResponse(BaseModel):
    response: str
    products: Optional[List[Dict[str, Any]]] = None

def load_italian_menu():
    """Direct load and formatting of Italian menu data"""
    logging.info("DIRECT LOAD: Loading Italian menu data for emergency endpoint")
    
    italian_path = os.path.join(data_dir, "meniu_italian.json")
    
    # Try to load and format the Italian menu data
    try:
        if os.path.exists(italian_path):
            with open(italian_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                logging.info(f"Successfully loaded {len(raw_data)} items from Italian menu file")
                
                # Format the data for web display
                formatted_data = []
                for i, item in enumerate(raw_data[:5]):  # Limit to 5 items
                    product_id = 11000 + i  # Generate unique ID
                    formatted_data.append({
                        "id": product_id,
                        "name": item.get("name", "Unknown Italian Dish"),
                        "price": item.get("price", "N/A"),
                        "description": item.get("description", "Authentic Italian cuisine"),
                        "short_description": "Italian specialty dish",
                        "permalink": item.get("url", "https://vogo.family"),
                        "images": [{
                            "src": item.get("image_url", "https://vogo.family/wp-content/uploads/2023/04/italian.jpg")
                        }],
                        "categories": [{"name": "Meniu Italian"}]
                    })
                
                logging.info(f"Formatted {len(formatted_data)} Italian food products")
                return formatted_data
                
    except Exception as e:
        logging.error(f"Error loading Italian menu file: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return []

@app.get("/")
def health_check():
    """Basic health check endpoint."""
    return {"status": "OK", "message": "Italian Menu Emergency API is running"}

@app.get("/italian-menu", response_model=ItalianMenuResponse)
def get_italian_menu():
    """Get Italian menu items directly from file."""
    products = load_italian_menu()
    
    if not products:
        raise HTTPException(status_code=500, detail="Failed to load Italian menu data")
    
    return {
        "response": "Here are our Italian menu items:",
        "products": products
    }

if __name__ == "__main__":
    uvicorn.run("emergency_italian:app", host="0.0.0.0", port=8001, reload=True)
