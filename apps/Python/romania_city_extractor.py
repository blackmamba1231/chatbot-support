#!/usr/bin/env python3
"""
Romanian City Extractor
Extracts all Romanian cities/locations available in the WooCommerce store's products
"""

import os
import json
import requests
from requests_oauthlib import OAuth1
from typing import Dict, Any, List, Set
import dotenv
from pathlib import Path
import re

# Load .env file
env_paths = [
    Path(__file__).parent / ".env",
    Path(__file__).parent.parent.parent / "apps" / "backend" / ".env"
]

for env_path in env_paths:
    if env_path.exists():
        print(f"Loading environment from {env_path}")
        dotenv.load_dotenv(env_path)
        break

# WooCommerce credentials
CONSUMER_KEY = os.environ.get("WP_CONSUMER_KEY", "ck_91e6fa3aac7b5c40ac5a9a1ec0743c0791472e62")
CONSUMER_SECRET = os.environ.get("WP_CONSUMER_SECRET", "cs_28bfe71efc2e7f71269236e79d47a896b96305a2")
BASE_URL = os.environ.get("WP_API_URL", "https://vogo.family")

# API endpoint
PRODUCTS_ENDPOINT = f"{BASE_URL}/wp-json/wc/v3/products"

# Authentication
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)

def fetch_all_products(per_page=100, max_pages=10):
    """Fetch all products, paginated"""
    all_products = []
    
    for page in range(1, max_pages + 1):
        print(f"Fetching products page {page}...")
        params = {"per_page": per_page, "page": page}
        
        try:
            response = requests.get(PRODUCTS_ENDPOINT, auth=auth, params=params)
            response.raise_for_status()
            products = response.json()
            
            if not products:
                break  # No more products
                
            all_products.extend(products)
            
            # If we got fewer products than requested, we've reached the end
            if len(products) < per_page:
                break
                
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            break
    
    print(f"Total products fetched: {len(all_products)}")
    return all_products

def extract_city_from_name(name):
    """Extract city name from product name"""
    # Remove any text after the dash
    if " - " in name:
        city_part = name.split(" - ")[0].strip()
        
        # Handle "Livrare din" prefix
        if city_part.startswith("Livrare din "):
            city_part = city_part.replace("Livrare din ", "")
        elif city_part.startswith("Livrare "):
            city_part = city_part.replace("Livrare ", "")
            
        return city_part
    
    return None

def extract_all_cities(products):
    """Extract all cities from products"""
    cities = set()
    
    for product in products:
        name = product.get("name", "")
        city = extract_city_from_name(name)
        if city:
            cities.add(city)
    
    return sorted(list(cities))

def extract_mall_names(products):
    """Extract all mall names from products"""
    malls = set()
    
    for product in products:
        name = product.get("name", "")
        if " - " in name:
            mall_part = name.split(" - ")[1].strip()
            malls.add(mall_part)
    
    return sorted(list(malls))

def filter_products_by_city(products, city):
    """Filter products by city"""
    city_products = []
    
    for product in products:
        name = product.get("name", "")
        if city in name:
            city_products.append(product)
    
    return city_products

def get_mall_delivery_by_city():
    """Get mall delivery products by city"""
    # Fetch all products
    products = fetch_all_products()
    
    # Filter to mall delivery products
    mall_delivery_products = []
    for product in products:
        categories = product.get("categories", [])
        for category in categories:
            if category.get("id") == 223:  # Mall delivery category ID
                mall_delivery_products.append(product)
                break
    
    print(f"Found {len(mall_delivery_products)} mall delivery products")
    
    # Extract cities
    cities = extract_all_cities(mall_delivery_products)
    print(f"Found {len(cities)} cities: {', '.join(cities)}")
    
    # Extract mall names
    malls = extract_mall_names(mall_delivery_products)
    print(f"Found {len(malls)} malls: {', '.join(malls)}")
    
    # Group products by city
    city_products = {}
    for city in cities:
        city_products[city] = filter_products_by_city(mall_delivery_products, city)
    
    return {
        "cities": cities,
        "malls": malls,
        "products_by_city": city_products,
        "all_products": mall_delivery_products
    }

if __name__ == "__main__":
    print("\n===== EXTRACTING ALL ROMANIAN CITIES & MALLS FROM PRODUCTS =====\n")
    
    result = get_mall_delivery_by_city()
    
    # Print cities and their mall delivery services
    for city in result["cities"]:
        city_products = result["products_by_city"][city]
        print(f"\n{city} ({len(city_products)} mall delivery services):")
        
        for product in city_products:
            print(f"  - {product.get('name')} - {product.get('price', 'N/A')} RON")
    
    # Export city and mall data to JSON
    with open("romania_locations.json", "w", encoding="utf-8") as f:
        json.dump({
            "cities": result["cities"],
            "malls": result["malls"]
        }, f, ensure_ascii=False, indent=2)
    
    print("\nExported city and mall data to romania_locations.json")
