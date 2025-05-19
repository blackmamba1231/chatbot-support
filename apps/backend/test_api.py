import requests
import json
import os
import base64
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API base URL
BASE_URL = "http://localhost:8000"

def test_chat_endpoint():
    """Test the chat endpoint"""
    print("\n=== Testing Chat Endpoint ===")
    
    # Test data
    data = {
        "query": "Hello, I need help with mall delivery",
        "language": "en"
    }
    
    # Send request
    response = requests.post(f"{BASE_URL}/api/mobile/chat", json=data)
    
    # Print response
    print(f"Status code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    return response.json()

def test_shopping_list_endpoints():
    """Test the shopping list endpoints"""
    print("\n=== Testing Shopping List Endpoints ===")
    
    # Test adding an item
    add_data = {
        "item": "Milk",
        "list_name": "groceries"
    }
    
    # Send request to add item
    add_response = requests.post(f"{BASE_URL}/api/mobile/shopping-list", json=add_data)
    
    # Print response
    print(f"Add item status code: {add_response.status_code}")
    print(f"Add item response: {json.dumps(add_response.json(), indent=2)}")
    
    # Test getting the shopping list
    get_response = requests.get(f"{BASE_URL}/api/mobile/shopping-list?list_name=groceries")
    
    # Print response
    print(f"Get list status code: {get_response.status_code}")
    print(f"Get list response: {json.dumps(get_response.json(), indent=2)}")
    
    return get_response.json()

def test_calendar_endpoints():
    """Test the calendar endpoints"""
    print("\n=== Testing Calendar Endpoints ===")
    
    # Test adding an event
    add_data = {
        "title": "Test Event",
        "date": "2025-04-20",
        "time": "14:30",
        "location": "Test Location",
        "description": "This is a test event"
    }
    
    # Send request to add event
    add_response = requests.post(f"{BASE_URL}/api/mobile/calendar", json=add_data)
    
    # Print response
    print(f"Add event status code: {add_response.status_code}")
    print(f"Add event response: {json.dumps(add_response.json(), indent=2)}")
    
    # Test getting calendar events
    get_response = requests.get(f"{BASE_URL}/api/mobile/calendar")
    
    # Print response
    print(f"Get events status code: {get_response.status_code}")
    print(f"Get events response: {json.dumps(get_response.json(), indent=2)}")
    
    return get_response.json()

def main():
    """Run all tests"""
    print("=== Testing API Endpoints ===")
    
    # Test chat endpoint
    chat_result = test_chat_endpoint()
    
    # Test shopping list endpoints
    shopping_list_result = test_shopping_list_endpoints()
    
    # Test calendar endpoints
    calendar_result = test_calendar_endpoints()
    
    print("\n=== All Tests Completed ===")

if __name__ == "__main__":
    main()
