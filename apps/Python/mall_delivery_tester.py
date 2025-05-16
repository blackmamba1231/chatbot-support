#!/usr/bin/env python3
"""
Mall Delivery WooCommerce Product Tester
A simple script to test fetching mall delivery products from the WooCommerce API
"""

import os
import json
import requests
from requests_oauthlib import OAuth1
from typing import Dict, Any
import dotenv
from pathlib import Path

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

# API endpoints
PRODUCTS_ENDPOINT = f"{BASE_URL}/wp-json/wc/v3/products"
CATEGORIES_ENDPOINT = f"{BASE_URL}/wp-json/wc/v3/products/categories"

# Authentication
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)

def fetch_data(url, params=None):
    """Fetch data from the API"""
    try:
        response = requests.get(url, auth=auth, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def format_products(products):
    """Format products for display"""
    formatted = []
    for product in products:
        # Extract location from product name if available
        location = "Unknown"
        name = product.get("name", "")
        if " - " in name:
            location = name.split(" - ")[0].strip()
            
        # Extract available cities from metadata if available
        available_cities = None
        for meta in product.get("meta_data", []):
            if meta.get("key") == "_available_cities":
                available_cities = meta.get("value")
                break
                
        formatted.append({
            "id": product.get("id"),
            "name": product.get("name"),
            "price": product.get("price", "N/A"),
            "categories": [cat.get("name") for cat in product.get("categories", [])],
            "location": location,
            "available_cities": available_cities
        })
    return formatted

def extract_meta_value(product, key):
    """Extract a value from product metadata"""
    for meta in product.get("meta_data", []):
        if meta.get("key") == key:
            return meta.get("value")
    return None

# Fetch all categories
print("\n===== FETCHING ALL CATEGORIES =====")
categories = fetch_data(CATEGORIES_ENDPOINT)
if categories:
    print(f"Found {len(categories)} categories")
    for cat in categories:
        print(f"- {cat.get('name')} (ID: {cat.get('id')}, Count: {cat.get('count')})")

# Fetch mall delivery products (category ID 223)
print("\n===== FETCHING MALL DELIVERY PRODUCTS (CATEGORY 223) =====")
mall_delivery_params = {"category": 223, "per_page": 20}
mall_products = fetch_data(PRODUCTS_ENDPOINT, mall_delivery_params)
if mall_products:
    print(f"Found {len(mall_products)} mall delivery products:")
    formatted = format_products(mall_products)
    for i, product in enumerate(formatted, 1):
        print(f"{i}. {product.get('name')} - {product.get('price')} RON - Location: {product.get('location')}")

# Define a test location
location = "Vaslui"

print(f"\n===== FETCHING PRODUCTS FOR LOCATION: {location} =====")
location_params = {"search": location, "per_page": 20}
location_products = fetch_data(PRODUCTS_ENDPOINT, location_params)
if location_products:
    print(f"Found {len(location_products)} products in {location}:")
    formatted = format_products(location_products)
    for i, product in enumerate(formatted, 1):
        print(f"{i}. {product.get('name')} - {product.get('price')} RON")
else:
    print(f"No products found in {location}")

# Fetch mall delivery products for specific location
print(f"\n===== FETCHING MALL DELIVERY PRODUCTS IN {location} =====")
specific_params = {"category": 223, "search": location, "per_page": 20}
specific_products = fetch_data(PRODUCTS_ENDPOINT, specific_params)
if specific_products:
    print(f"Found {len(specific_products)} mall delivery products in {location}:")
    formatted = format_products(specific_products)
    for i, product in enumerate(formatted, 1):
        print(f"{i}. {product.get('name')} - {product.get('price')} RON")
else:
    print(f"No mall delivery products found in {location}")

# Try another location
location = "Bacău"
print(f"\n===== FETCHING MALL DELIVERY PRODUCTS IN {location} =====")
specific_params = {"category": 223, "search": location, "per_page": 20}
specific_products = fetch_data(PRODUCTS_ENDPOINT, specific_params)
if specific_products:
    print(f"Found {len(specific_products)} mall delivery products in {location}:")
    formatted = format_products(specific_products)
    for i, product in enumerate(formatted, 1):
        print(f"{i}. {product.get('name')} - {product.get('price')} RON")
        
        # Print meta data for available cities
        available_cities = extract_meta_value(specific_products[i-1], "_available_cities")
        if available_cities:
            print(f"   Available cities: {available_cities}")
else:
    print(f"No mall delivery products found in {location}")

# Fetch pet care products (category ID 547)
print("\n===== FETCHING PET CARE PRODUCTS (CATEGORY 547) =====")
pet_care_params = {"category": 547, "per_page": 20}
pet_products = fetch_data(PRODUCTS_ENDPOINT, pet_care_params)
if pet_products:
    print(f"Found {len(pet_products)} pet care products:")
    formatted = format_products(pet_products)
    for i, product in enumerate(formatted, 1):
        print(f"{i}. {product.get('name')} - {product.get('price')} RON")
else:
    print("No pet care products found")
