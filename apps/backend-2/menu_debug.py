"""
Special debugging script for the Italian menu data.
Run this script directly to test and debug the menu loading without going through the API.
"""

import os
import json
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Path to scraped data
base_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(base_dir, "scraped_data")

def load_italian_menu():
    """Direct load and formatting of Italian menu data"""
    logging.info("DIRECT DEBUG: Loading Italian menu data")
    
    italian_path = os.path.join(data_dir, "meniu_italian.json")
    italian_detailed_path = os.path.join(data_dir, "meniu_italian_detailed.json")
    
    # Check which files exist and log their details
    for path in [italian_path, italian_detailed_path]:
        if os.path.exists(path):
            file_size = os.path.getsize(path)
            logging.info(f"File exists: {path} (Size: {file_size} bytes)")
            
            # Try to read the first few lines to debug
            try:
                with open(path, "r", encoding="utf-8") as f:
                    first_lines = [next(f) for _ in range(5)]
                    logging.info(f"First few lines: {first_lines}")
            except Exception as e:
                logging.error(f"Could not read file: {e}")
        else:
            logging.error(f"File does not exist: {path}")
    
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
                            "src": item.get("image_url", "https://vogo.family/wp-content/uploads/2025/02/italian-default.jpg")
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

def check_all_json_files():
    """List and check all JSON files in the scraped_data directory"""
    logging.info(f"Checking all JSON files in {data_dir}")
    
    if not os.path.exists(data_dir):
        logging.error(f"Directory does not exist: {data_dir}")
        return
    
    json_files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    logging.info(f"Found {len(json_files)} JSON files: {json_files}")
    
    # Check each file for basic JSON validity
    for json_file in json_files:
        file_path = os.path.join(data_dir, json_file)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    logging.info(f"{json_file}: Valid JSON array with {len(data)} items")
                elif isinstance(data, dict):
                    logging.info(f"{json_file}: Valid JSON object with {len(data.keys())} keys")
                else:
                    logging.warning(f"{json_file}: Valid JSON but unexpected type: {type(data)}")
        except json.JSONDecodeError as e:
            logging.error(f"{json_file}: Invalid JSON: {str(e)}")
        except Exception as e:
            logging.error(f"{json_file}: Error reading file: {str(e)}")

if __name__ == "__main__":
    # Check all JSON files in the directory
    check_all_json_files()
    
    # Test loading the Italian menu
    print("\n=== ITALIAN MENU DEBUG ===")
    italian_menu = load_italian_menu()
    
    # Print the results
    if italian_menu:
        print(f"Successfully loaded {len(italian_menu)} Italian menu items:")
        for item in italian_menu:
            print(f" - {item['name']} ({item['price']})")
    else:
        print("Failed to load Italian menu items. Check the logs for details.")
