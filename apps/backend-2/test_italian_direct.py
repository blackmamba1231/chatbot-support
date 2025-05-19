"""
Direct test script for the Italian menu data loading.
This script bypasses the WooCommerce sync and directly tests the Italian data loading.
"""

import os
import json
import logging
from src.rag.engine import RAGEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a simplified mock WooCommerce service
class MockWooCommerceService:
    def __init__(self):
        pass
    
    async def get_products(self, *args, **kwargs):
        return []
    
    async def get_product_categories(self, *args, **kwargs):
        return []

def test_italian_menu_direct():
    """Test the Italian menu loading directly"""
    print("\n===== DIRECT TESTING ITALIAN MENU LOADING =====")
    
    # Initialize minimal RAG engine without full initialization
    rag_engine = RAGEngine(MockWooCommerceService())
    
    # Manually set the data directory
    rag_engine.data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scraped_data")
    
    # Skip the full initialization - just load the scraped data
    rag_engine._load_scraped_data()
    
    # Test the Italian food products method directly
    italian_products = rag_engine._get_italian_food_products()
    
    # Print results
    print(f"\nFound {len(italian_products)} Italian food products:")
    for i, product in enumerate(italian_products, 1):
        print(f"\n--- Product {i} ---")
        print(f"ID: {product.get('id')}")
        print(f"Name: {product.get('name')}")
        print(f"Price: {product.get('price')}")
        print(f"Description: {product.get('description')[:100]}..." if len(product.get('description', '')) > 100 else product.get('description'))
        print(f"Image: {product.get('images', [{}])[0].get('src', 'No image')}")
    
    # Test with some Italian keywords to see if detection works
    test_query = "I want Italian food and pizza"
    query_lower = test_query.lower()
    italian_keywords = ["italian", "italia", "pizza", "pasta", "carbonara", "lasagna", "risotto"]
    is_italian_detected = any(keyword in query_lower for keyword in italian_keywords)
    
    print(f"\nTest Query: '{test_query}'")
    print(f"Italian food detected: {is_italian_detected}")
    
    print("\n===== TEST COMPLETE =====")

if __name__ == "__main__":
    # Run the direct test
    test_italian_menu_direct()
