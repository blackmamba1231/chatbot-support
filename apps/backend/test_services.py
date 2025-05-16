import asyncio
import os
from dotenv import load_dotenv
from app.services.product_service import ProductService
from app.services.woocommerce_service import WooCommerceService

# Load test environment variables
load_dotenv('test.env')

async def test_services():
    """Test the updated services"""
    print("\n=== Testing WooCommerce Integration ===")
    
    # Initialize services
    wc_service = WooCommerceService()
    product_service = ProductService(woocommerce_service=wc_service)
    
    # Test getting categories
    print("\nTesting get_categories...")
    categories = product_service.get_product_categories()
    print(f"Found {len(categories)} categories")
    
    # Test getting restaurants in Alba Iulia
    print("\nTesting get_restaurants in Alba Iulia...")
    restaurants = product_service.get_restaurants(location="alba-iulia")
    print(f"\nRestaurants response: {restaurants}")
    if restaurants["status"] == "success":
        print(f"Found {len(restaurants['restaurants'])} restaurants")
        if restaurants['restaurants']:
            print("\nExample restaurant:")
            restaurant = restaurants['restaurants'][0]
            print(f"Name: {restaurant['name']}")
            print(f"Description: {restaurant['short_description']}")
            print(f"Price: {restaurant['price']}")
        else:
            print("No restaurants found in Alba Iulia")
    else:
        print(f"Error: {restaurants['message']}")
    
    # Test getting mall delivery services
    print("\nTesting get_mall_services...")
    mall_services = product_service.get_mall_services()
    if mall_services["status"] == "success":
        print(f"Found {len(mall_services['services'])} mall delivery services")
        if mall_services['services']:
            print("\nExample mall service:")
            service = mall_services['services'][0]
            print(f"Name: {service['name']}")
            print(f"Description: {service['short_description']}")
            print(f"Price: {service['price']}")
        else:
            print("No mall delivery services found")
    else:
        print(f"Error: {mall_services['message']}")
    
    # Test getting locations
    print("\nTesting get_locations...")
    locations = product_service.get_locations()
    print(f"Available locations: {', '.join(locations)}")

if __name__ == "__main__":
    asyncio.run(test_services())
