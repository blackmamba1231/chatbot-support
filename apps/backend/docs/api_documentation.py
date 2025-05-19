import requests
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# WooCommerce API credentials
WP_API_URL = os.getenv("WP_API_URL", "https://vogo.family/wp-json/")
WP_CONSUMER_KEY = os.getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = os.getenv("WP_CONSUMER_SECRET")

def test_endpoint(endpoint, method="GET", params=None, data=None):
    """Test a WooCommerce API endpoint and return formatted results"""
    url = f"{WP_API_URL}wc/v3/{endpoint}"
    auth = (WP_CONSUMER_KEY, WP_CONSUMER_SECRET)
    
    try:
        if method == "GET":
            response = requests.get(url, auth=auth, params=params)
        elif method == "POST":
            response = requests.post(url, json=data, auth=auth)
        
        return {
            "endpoint": endpoint,
            "method": method,
            "url": url,
            "status_code": response.status_code,
            "response": response.json() if response.status_code == 200 else response.text
        }
        
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "url": url,
            "error": str(e)
        }

def generate_api_documentation():
    """Generate comprehensive API documentation"""
    
    docs = {
        "generated_at": datetime.now().isoformat(),
        "base_url": WP_API_URL,
        "authentication": {
            "type": "Basic Auth",
            "parameters": {
                "consumer_key": "WP_CONSUMER_KEY environment variable",
                "consumer_secret": "WP_CONSUMER_SECRET environment variable"
            }
        },
        "endpoints": {}
    }
    
    # Test Products API
    product_endpoints = {
        "list_products": {
            "endpoint": "products",
            "params": None
        },
        "restaurants": {
            "endpoint": "products",
            "params": {"category": "restaurante"}
        },
        "mall_delivery": {
            "endpoint": "products",
            "params": {"category": 223}  # Using known category ID for consistency
        },
        "mall_products": {
            "endpoint": "products",
            "params": {"category": 793}  # Products directly under Mall category
        },
        "alba_iulia_services": {
            "endpoint": "products",
            "params": {"tag": "alba-iulia"}
        }
    }
    
    docs["endpoints"]["products"] = {}
    for name, config in product_endpoints.items():
        result = test_endpoint(config["endpoint"], params=config["params"])
        docs["endpoints"]["products"][name] = result
    
    # Test Categories API
    category_endpoints = {
        "list_categories": {
            "endpoint": "products/categories",
            "params": None
        },
        "mall_parent_category": {
            "endpoint": "products/categories/793",  # Mall category ID
            "params": None
        },
        "mall_subcategories": {
            "endpoint": "products/categories",
            "params": {"parent": 793}  # Get all subcategories under Mall
        },
        "restaurant_category": {
            "endpoint": "products/categories",
            "params": {"slug": "restaurante"}  # Updated to use Romanian slug
        }
    }
    
    docs["endpoints"]["categories"] = {}
    for name, config in category_endpoints.items():
        result = test_endpoint(config["endpoint"], params=config["params"])
        docs["endpoints"]["categories"][name] = result
    
    # Test Orders API
    order_endpoints = {
        "list_orders": {
            "endpoint": "orders",
            "params": {"status": "processing"}
        }
    }
    
    docs["endpoints"]["orders"] = {}
    for name, config in order_endpoints.items():
        result = test_endpoint(config["endpoint"], params=config["params"])
        docs["endpoints"]["orders"][name] = result
    
    # Save documentation
    os.makedirs("docs", exist_ok=True)
    with open("docs/api_documentation.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, indent=2, ensure_ascii=False)
    
    # Generate markdown documentation
    generate_markdown_docs(docs)

def generate_markdown_docs(docs):
    """Generate markdown documentation from the API test results"""
    
    md = f"""# Vogo.Family WooCommerce API Documentation
Generated at: {docs['generated_at']}

## Base URL
{docs['base_url']}

## Authentication
- Type: {docs['authentication']['type']}
- Parameters:
  - consumer_key: {docs['authentication']['parameters']['consumer_key']}
  - consumer_secret: {docs['authentication']['parameters']['consumer_secret']}

## Endpoints

"""
    
    for category, endpoints in docs["endpoints"].items():
        md += f"### {category.title()}\n\n"
        
        for name, result in endpoints.items():
            md += f"#### {name.replace('_', ' ').title()}\n"
            md += f"- Method: {result['method']}\n"
            md += f"- Endpoint: `{result['endpoint']}`\n"
            
            if isinstance(result.get('response'), list) and len(result['response']) > 0:
                md += "- Response Structure:\n```json\n"
                md += json.dumps(result['response'][0], indent=2)
                md += "\n```\n\n"
            elif isinstance(result.get('response'), dict):
                md += "- Response Structure:\n```json\n"
                md += json.dumps(result['response'], indent=2)
                md += "\n```\n\n"
    
    with open("docs/api_documentation.md", "w", encoding="utf-8") as f:
        f.write(md)

if __name__ == "__main__":
    print("Generating API documentation...")
    generate_api_documentation()
    print("Documentation generated in docs/api_documentation.json and docs/api_documentation.md")
