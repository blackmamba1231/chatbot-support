import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WooCommerce API credentials
WP_API_URL = os.getenv("WP_API_URL", "https://vogo.family/wp-json/")
WP_CONSUMER_KEY = os.getenv("WP_CONSUMER_KEY")
WP_CONSUMER_SECRET = os.getenv("WP_CONSUMER_SECRET")

def test_endpoint(endpoint, method="GET", data=None):
    """Test a WooCommerce API endpoint"""
    url = f"{WP_API_URL}wc/v3/{endpoint}"
    
    # Add authentication
    auth = (WP_CONSUMER_KEY, WP_CONSUMER_SECRET)
    
    print(f"\n=== Testing {method} {url} ===")
    
    try:
        if method == "GET":
            response = requests.get(url, auth=auth)
        elif method == "POST":
            response = requests.post(url, json=data, auth=auth)
        
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"Error: {response.text}")
            
        return response
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def explore_api():
    """Explore available WooCommerce API endpoints"""
    
    # Test basic endpoints
    endpoints = [
        "products",
        "products/categories",
        "orders",
        "customers",
        "coupons",
        "reports",
        "settings",
        "system_status",
        "shipping_methods",
        "payment_gateways",
        "webhooks"
    ]
    
    results = {}
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        response = test_endpoint(endpoint)
        if response:
            results[endpoint] = {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text
            }
    
    # Save results to file
    with open("woocommerce_api_docs.json", "w") as f:
        json.dump(results, f, indent=2)
        print("\nResults saved to woocommerce_api_docs.json")

def test_specific_endpoints():
    """Test specific endpoints that might be relevant for the mall delivery service"""
    
    # Test product categories
    print("\nTesting product categories...")
    test_endpoint("products/categories")
    
    # Test products with category filter
    print("\nTesting products with category filter...")
    test_endpoint("products?category=restaurants")
    
    # Test products with location filter
    print("\nTesting products with location filter...")
    test_endpoint("products?tag=alba-iulia")
    
    # Test custom endpoints if any
    print("\nTesting custom endpoints...")
    custom_endpoints = [
        "mall-delivery/locations",
        "mall-delivery/restaurants",
        "mall-delivery/orders"
    ]
    
    for endpoint in custom_endpoints:
        test_endpoint(endpoint)

if __name__ == "__main__":
    print("Starting WooCommerce API exploration...")
    explore_api()
    print("\nTesting specific endpoints...")
    test_specific_endpoints()
