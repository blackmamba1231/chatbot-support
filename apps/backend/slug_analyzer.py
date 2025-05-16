#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv
from app.services.enhanced_woocommerce_service import EnhancedWooCommerceService
from app.services.product_service import ProductService

# Load environment variables
load_dotenv()

def print_section(title):
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80)

def main():
    # Initialize services
    woo_service = EnhancedWooCommerceService()
    product_service = ProductService()
    
    print_section("TESTING CATEGORY SLUGS")
    
    # Get categories using ProductService
    print("Fetching categories...")
    categories_result = product_service.get_product_categories()
    
    if isinstance(categories_result, dict) and categories_result.get("status") == "error":
        print(f"Error: {categories_result.get('message')}")
        categories = []
    else:
        categories = categories_result
    
    if not categories:
        print("No categories found!")
    else:
        print(f"Found {len(categories)} categories")
        for i, category in enumerate(categories[:5], 1):  # Show first 5
            print(f"\n{i}. Category: {category.get('name', 'Unknown')}")
            print(f"   - ID: {category.get('id')}")
            print(f"   - Slug: {category.get('slug', 'No slug')}")
            print(f"   - Count: {category.get('count', 0)} products")
    
    print_section("TESTING PRODUCT SLUGS")
    
    # Get products using ProductService
    print("Fetching products...")
    products_result = product_service.get_products(limit=10)
    
    if products_result.get("status") == "error":
        print(f"Error: {products_result.get('message')}")
        products = []
    else:
        products = products_result.get("products", [])
    
    if not products:
        print("No products found!")
    else:
        print(f"Found {len(products)} products")
        for i, product in enumerate(products[:5], 1):  # Show first 5
            print(f"\n{i}. Product: {product.get('name', 'Unknown')}")
            print(f"   - ID: {product.get('id')}")
            print(f"   - Slug: {product.get('slug', 'No slug')}")
            print(f"   - Categories: {', '.join([c.get('name', 'Unknown') for c in product.get('categories', [])])}")
            
            # Show category slugs for this product
            cat_slugs = [c.get('slug', 'Unknown') for c in product.get('categories', [])]
            print(f"   - Category Slugs: {', '.join(cat_slugs)}")
    
    print_section("TESTING BASIC SEARCH")
    
    # Test search terms - focus on terms that might match slugs
    search_terms = ["pizza", "auto", "bio", "mall", "antipasti"]
    
    for term in search_terms:
        print(f"\nSearching for '{term}'...")
        
        # Current search functionality
        results = product_service.search_products(term)
        
        if results.get("status") == "success":
            products_found = results.get("products", [])
            print(f"Found {len(products_found)} products")
            
            for i, product in enumerate(products_found[:3], 1):  # Show first 3
                print(f"\n{i}. Product: {product.get('name', 'Unknown')}")
                
                # Check if term is in name
                name = product.get('name', '').lower()
                if term.lower() in name:
                    print(f"   - MATCH IN NAME: '{term}' found in '{name}'")
                
                # Check if term is in slug
                slug = product.get('slug', '').lower()
                print(f"   - Slug: {slug}")
                if term.lower() in slug:
                    print(f"   - MATCH IN SLUG: '{term}' found in '{slug}'")
                else:
                    print(f"   - NO MATCH in slug")
                
                # Check category slugs
                cat_slugs = [c.get('slug', '').lower() for c in product.get('categories', [])]
                print(f"   - Category Slugs: {', '.join(cat_slugs)}")
                matching_cats = [s for s in cat_slugs if term.lower() in s]
                if matching_cats:
                    print(f"   - MATCH IN CATEGORY SLUGS: '{term}' found in {', '.join(matching_cats)}")
                else:
                    print(f"   - NO MATCH in category slugs")
        else:
            print(f"Search failed: {results.get('message', 'Unknown error')}")
    
    print_section("COMPLETE")

if __name__ == "__main__":
    main()
