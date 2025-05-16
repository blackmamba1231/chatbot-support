#!/usr/bin/env python3
import os
import requests
from base64 import b64encode
import json
from pprint import pprint
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# WooCommerce API credentials from environment
wp_api_url = os.environ.get("WP_API_URL", "https://vogo.family")
consumer_key = os.environ.get("WP_CONSUMER_KEY", "ck_47075e7afebb1ad956d0350ee9ada1c93f3dbbaa")
consumer_secret = os.environ.get("WP_CONSUMER_SECRET", "cs_c264cd481899b999ce5cd3cc3b97ff7cb32aab07")

def print_section(title):
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80)

def try_handle_response(response):
    """Try different ways to handle potentially malformed JSON response"""
    print(f"Status code: {response.status_code}")
    print(f"Response headers: {response.headers}")
    
    # Print raw response first
    print("\nRaw response:")
    print("-" * 50)
    raw_text = response.text[:500]  # First 500 chars to avoid huge output
    print(raw_text)
    print("-" * 50)
    
    # Try to parse as JSON
    try:
        data = response.json()
        print("\nParsed as JSON successfully!")
        return data
    except json.JSONDecodeError as e:
        print(f"\nJSON decode error: {str(e)}")
        
        # Try to find valid JSON by trimming the response
        try:
            # If it starts with a number followed by some character, try removing that
            text = response.text.strip()
            if text and text[0].isdigit():
                for i in range(len(text)):
                    if not text[i].isdigit():
                        trimmed = text[i:].strip()
                        break
                else:
                    trimmed = ""
                
                if trimmed and (trimmed.startswith('{') or trimmed.startswith('[')):
                    print("\nTrying to parse trimmed response...")
                    return json.loads(trimmed)
        except Exception as trim_err:
            print(f"Error while trimming: {str(trim_err)}")
        
        # If all else fails, try to extract anything that looks like JSON
        try:
            text = response.text
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                potential_json = text[start_idx:end_idx+1]
                print("\nExtracted potential JSON object...")
                return json.loads(potential_json)
            
            start_idx = text.find('[')
            end_idx = text.rfind(']')
            
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                potential_json = text[start_idx:end_idx+1]
                print("\nExtracted potential JSON array...")
                return json.loads(potential_json)
        except Exception as extract_err:
            print(f"Error extracting JSON: {str(extract_err)}")
    
    print("\nCould not parse response as JSON.")
    return None

def test_api_index():
    """Test the main WordPress API index"""
    print_section("TESTING WORDPRESS API INDEX")
    url = f"{wp_api_url}/wp-json/"
    
    try:
        response = requests.get(url)
        return try_handle_response(response)
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_woo_endpoints(endpoints=None):
    """Test various WooCommerce endpoints with different authentication methods"""
    if endpoints is None:
        endpoints = [
            "wp-json/wc/v3/products",
            "wp-json/wc/store/v1/products",
            "wp-json/wc/v3/products/categories",
            "wp-json/wc/store/v1/products/categories"
        ]
    
    results = {}
    
    for endpoint in endpoints:
        print_section(f"TESTING ENDPOINT: {endpoint}")
        full_url = f"{wp_api_url}/{endpoint}"
        
        # Method 1: Basic Auth
        print("\n[Testing with Basic Auth]")
        try:
            auth_string = b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
            headers = {"Authorization": f"Basic {auth_string}"}
            response = requests.get(full_url, headers=headers)
            results[f"{endpoint}_basic"] = try_handle_response(response)
        except Exception as e:
            print(f"Error with Basic Auth: {str(e)}")
        
        # Method 2: Query Parameters
        print("\n[Testing with Query Parameters]")
        try:
            params = {
                "consumer_key": consumer_key,
                "consumer_secret": consumer_secret
            }
            response = requests.get(full_url, params=params)
            results[f"{endpoint}_query"] = try_handle_response(response)
        except Exception as e:
            print(f"Error with Query Params: {str(e)}")
        
        # Method 3: OAuth 1.0a
        # OAuth 1.0a is more complex, and requires additional libraries
        # We're sticking with simpler methods for this test
    
    return results

def test_rest_api_discovery():
    """Discover what REST API endpoints are available"""
    print_section("DISCOVERING REST API ENDPOINTS")
    
    # Try to check what namespaces and endpoints are available
    url = f"{wp_api_url}/wp-json/"
    
    try:
        print(f"Checking API root: {url}")
        response = requests.get(url)
        data = try_handle_response(response)
        
        if data and isinstance(data, dict):
            # Check for namespaces
            namespaces = data.get('namespaces', [])
            if namespaces:
                print("\nFound namespaces:")
                for ns in namespaces:
                    print(f"  - {ns}")
            
            # Check for routes
            routes = data.get('routes', {})
            if routes:
                print("\nFound routes:")
                wc_routes = []
                for route, info in routes.items():
                    if 'wc' in route:
                        print(f"  - {route}")
                        wc_routes.append(route)
                
                # If we found WooCommerce routes, test them
                if wc_routes:
                    print("\nTesting discovered WooCommerce endpoints...")
                    test_woo_endpoints(wc_routes)
        
        return data
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    """Main function to run tests"""
    print_section("WOOCOMMERCE API TEST")
    print(f"Testing WooCommerce API at {wp_api_url}")
    print(f"Using consumer key: {consumer_key[:5]}...{consumer_key[-5:]}")
    
    # Test 1: Try to access the main API index
    api_index = test_api_index()
    
    # Test 2: Try specific WooCommerce endpoints
    woo_results = test_woo_endpoints()
    
    # Test 3: Try to discover REST API endpoints
    api_discovery = test_rest_api_discovery()
    
    print_section("TESTING COMPLETE")

if __name__ == "__main__":
    main()
