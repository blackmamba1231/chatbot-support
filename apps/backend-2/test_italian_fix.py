"""
Test script to verify the Italian menu fix.
This restarts the RAG engine and tests the Italian menu directly.
"""

import os
import json
import logging
import asyncio
from src.rag.engine import RAGEngine
from src.services.woocommerce_service import WooCommerceService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_italian_menu():
    """Test the Italian menu detection and response generation"""
    print("\n===== TESTING ITALIAN MENU FIX =====")
    
    # Initialize services
    woocommerce_service = WooCommerceService()
    
    # Create a fresh instance of the RAG engine
    print("\nInitializing fresh RAG engine instance...")
    rag_engine = RAGEngine(woocommerce_service)
    await rag_engine.initialize()
    
    # Test different Italian-related queries
    test_queries = [
        "I want Italian food",
        "Show me Italian menu options",
        "Do you have pizza?",
        "I'd like to order pasta",
        "What Italian dishes do you offer?",
        "_get_italian_food_products",  # Direct method call test
        "meniu_italian",  # Direct category reference
    ]
    
    for query in test_queries:
        print(f"\n\n----- Testing query: '{query}' -----")
        response = await rag_engine.generate_response(query)
        
        print(f"Response message: {response.get('response', 'No response text')}")
        
        # Display product information
        products = response.get('products', [])
        print(f"Number of products returned: {len(products)}")
        
        if products:
            for i, product in enumerate(products[:3], 1):  # Show first 3 products
                print(f"\nProduct {i}:")
                print(f"  Name: {product.get('name', 'Unknown')}")
                print(f"  Price: {product.get('price', 'N/A')}")
                print(f"  Description: {product.get('description', 'No description')[:50]}...")
        else:
            print("No products returned!")
    
    print("\n===== TEST COMPLETE =====")

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_italian_menu())
