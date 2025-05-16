#!/usr/bin/env python
import os
import requests
from requests_oauthlib import OAuth1
import json

# Load credentials - you can replace these with your environment variables
CONSUMER_KEY = "ck_91e6fa3aac7b5c40ac5a9a1ec0743c0791472e62"
CONSUMER_SECRET = "cs_28bfe71efc2e7f71269236e79d47a896b96305a2"
BASE_URL = "https://vogo.family"

# Create OAuth1 authentication
auth = OAuth1(CONSUMER_KEY, CONSUMER_SECRET)

# Test 1: Get Products
print("Testing WooCommerce Products API...")
products_url = f"{BASE_URL}/wp-json/wc/v3/products"
response = requests.get(products_url, auth=auth)

print(f"Response Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Successfully retrieved products!")
    # Print first product as example
    products = response.json()
    if products and len(products) > 0:
        print(f"Found {len(products)} products")
        print(f"First product: {products[0]['name']}")
    else:
        print("No products found")
else:
    print("❌ Failed to retrieve products")
    print(f"Response: {response.text}")

# Test 2: Get Categories
print("\nTesting WooCommerce Categories API...")
categories_url = f"{BASE_URL}/wp-json/wc/v3/products/categories"
response = requests.get(categories_url, auth=auth)

print(f"Response Status Code: {response.status_code}")
if response.status_code == 200:
    print("✅ Successfully retrieved categories!")
    # Print first few categories as example
    categories = response.json()
    if categories and len(categories) > 0:
        print(f"Found {len(categories)} categories")
        for cat in categories[:5]:  # Print first 5 categories
            print(f"- {cat['name']} (ID: {cat['id']})")
    else:
        print("No categories found")
else:
    print("❌ Failed to retrieve categories")
    print(f"Response: {response.text}")

# Test getting products from a specific category
mall_delivery_id = 223  # Mall delivery category ID
print(f"\nTesting products from category {mall_delivery_id}...")
category_products_url = f"{BASE_URL}/wp-json/wc/v3/products?category={mall_delivery_id}"
response = requests.get(category_products_url, auth=auth)

print(f"Response Status Code: {response.status_code}")
if response.status_code == 200:
    products = response.json()
    print(f"✅ Found {len(products)} products in category {mall_delivery_id}")
    if products and len(products) > 0:
        print("Product examples:")
        for p in products[:3]:  # Show first 3 products
            print(f"- {p['name']}")
else:
    print("❌ Failed to retrieve category products")
    print(f"Response: {response.text}")
