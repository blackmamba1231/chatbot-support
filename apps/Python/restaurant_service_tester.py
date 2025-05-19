"""
Restaurant Service Tester
This script tests if pizza and restaurant services are available in the WooCommerce store.
"""

import os
import requests
import json
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Try to load from backend .env
backend_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend', '.env')
if os.path.exists(backend_env_path):
    print(f"Loading environment variables from backend .env: {backend_env_path}")
    load_dotenv(backend_env_path)

# WooCommerce API credentials
WOOCOMMERCE_URL = os.environ.get("WOOCOMMERCE_URL", "https://vogo.family")

# Since we can't directly view the .env file, let's use the test data from our existing sample
# These are the credentials used in our memory for the working mall delivery integration
WOOCOMMERCE_CONSUMER_KEY = os.environ.get("WOOCOMMERCE_CONSUMER_KEY", "ck_a9901152e8757c14a54215a8c50265dae15c8d72")
WOOCOMMERCE_CONSUMER_SECRET = os.environ.get("WOOCOMMERCE_CONSUMER_SECRET", "cs_ae2c9f99ebbe31c40c3dfa7da904ca9986f40b56")

print(f"Using WooCommerce URL: {WOOCOMMERCE_URL}")
print(f"Using consumer key: {WOOCOMMERCE_CONSUMER_KEY[:5]}...")

# Verify credentials are available
if not WOOCOMMERCE_CONSUMER_KEY or not WOOCOMMERCE_CONSUMER_SECRET:
    print("Error: WooCommerce API credentials not found. Please set WOOCOMMERCE_CONSUMER_KEY and WOOCOMMERCE_CONSUMER_SECRET.")
    exit(1)

# Endpoints
API_URL = f"{WOOCOMMERCE_URL.rstrip('/')}/wp-json/wc/v3"
PRODUCTS_ENDPOINT = f"{API_URL}/products"
CATEGORIES_ENDPOINT = f"{API_URL}/products/categories"

# OAuth1 authentication
auth = OAuth1(WOOCOMMERCE_CONSUMER_KEY, WOOCOMMERCE_CONSUMER_SECRET)

def fetch_data(url, params=None):
    """Fetch data from the WooCommerce API"""
    try:
        print(f"Making request to {url} with params: {params}")
        response = requests.get(url, params=params, auth=auth)
        response.raise_for_status()
        data = response.json()
        return data
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return None

def format_products(products):
    """Format product data for display"""
    return [{
        "id": p.get("id"),
        "name": p.get("name", "Unknown"),
        "price": p.get("price", "N/A"),
        "categories": [cat.get("name") for cat in p.get("categories", [])],
        "description": p.get("short_description", "") or p.get("description", "")[:100] + "..." if p.get("description", "") else ""
    } for p in products]

def search_for_category(keyword):
    """Search for a category by name"""
    print(f"\n===== SEARCHING FOR CATEGORY: {keyword} =====")
    categories = fetch_data(CATEGORIES_ENDPOINT, {"per_page": 100})
    
    if not categories:
        print("No categories found")
        return None
        
    matching_categories = [cat for cat in categories if keyword.lower() in cat.get("name", "").lower()]
    
    if matching_categories:
        print(f"Found {len(matching_categories)} matching categories:")
        for cat in matching_categories:
            print(f"ID: {cat.get('id')} | Name: {cat.get('name')} | Count: {cat.get('count')} products")
        return matching_categories
    else:
        print(f"No categories matching '{keyword}' found")
        return None

def search_for_products(keyword, category_id=None):
    """Search for products by keyword"""
    print(f"\n===== SEARCHING FOR PRODUCTS: {keyword} =====")
    params = {"search": keyword, "per_page": 20}
    
    if category_id:
        params["category"] = category_id
        
    products = fetch_data(PRODUCTS_ENDPOINT, params)
    
    if not products:
        print("No products found")
        return None
        
    if products:
        print(f"Found {len(products)} products matching '{keyword}':")
        formatted = format_products(products)
        for i, product in enumerate(formatted, 1):
            print(f"{i}. {product.get('name')} - {product.get('price')} RON")
            if product.get("categories"):
                print(f"   Categories: {', '.join(product.get('categories'))}")
        return products
    else:
        print(f"No products matching '{keyword}' found")
        return None

def main():
    print("======== RESTAURANT SERVICE TESTER ========")
    print(f"Testing WooCommerce API at: {WOOCOMMERCE_URL}\n")
    
    # 1. Check if restaurant or food-related categories exist
    restaurant_categories = search_for_category("restaurant")
    food_categories = search_for_category("food")
    pizza_categories = search_for_category("pizza")
    
    # 2. Search for pizza products
    pizza_products = search_for_products("pizza")
    
    # 3. Search for restaurant products
    restaurant_products = search_for_products("restaurant")
    
    # 4. General food search
    food_products = search_for_products("food")
    
    # 5. Check all products in popular food categories
    if food_categories:
        for category in food_categories[:3]:  # Check first 3 food categories
            category_id = category.get("id")
            category_name = category.get("name")
            print(f"\n===== PRODUCTS IN CATEGORY: {category_name} (ID: {category_id}) =====")
            category_products = fetch_data(PRODUCTS_ENDPOINT, {"category": category_id, "per_page": 20})
            
            if category_products:
                print(f"Found {len(category_products)} products in '{category_name}' category:")
                formatted = format_products(category_products)
                for i, product in enumerate(formatted, 1):
                    print(f"{i}. {product.get('name')} - {product.get('price')} RON")
            else:
                print(f"No products found in '{category_name}' category")
    
    # 6. Check total number of categories and products
    print("\n===== CHECKING TOTAL CATEGORIES =====")
    all_categories = fetch_data(CATEGORIES_ENDPOINT, {"per_page": 100})
    if all_categories:
        print(f"Total categories: {len(all_categories)}")
        # Look for potentially relevant categories
        food_related = [cat for cat in all_categories if any(kw in cat.get("name", "").lower() 
                                                             for kw in ["food", "pizza", "restaurant", "meal", "eat"])]
        if food_related:
            print("\nPotentially food-related categories:")
            for cat in food_related:
                print(f"ID: {cat.get('id')} | Name: {cat.get('name')} | Count: {cat.get('count')} products")
    
    print("\n===== CHECKING TOTAL PRODUCTS =====")
    all_products = fetch_data(PRODUCTS_ENDPOINT, {"per_page": 10})
    if all_products:
        total_products_header = response.headers.get("X-WP-Total")
        if total_products_header:
            print(f"Total products in store: {total_products_header}")
        else:
            print(f"Sample products: {len(all_products)}")
            
    print("\n===== CONCLUSION =====")
    if not (restaurant_categories or food_categories or pizza_categories or pizza_products or restaurant_products):
        print("No restaurant or pizza-related categories or products were found in the WooCommerce store.")
        print("This explains why the chatbot couldn't find any pizza when you asked for it.")
        print("\nNext steps:")
        print("1. Add restaurant categories to the WooCommerce store")
        print("2. Add pizza and other restaurant products to these categories")
        print("3. Update the chatbot to properly handle restaurant-related intents")

if __name__ == "__main__":
    main()
