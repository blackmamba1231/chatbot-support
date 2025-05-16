#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv
from app.services.product_service import ProductService

# Load environment variables
load_dotenv()

def print_section(title):
    print("\n" + "="*80)
    print(f" {title} ".center(80, "="))
    print("="*80)

def main():
    print_section("TESTING ENHANCED PRODUCT SEARCH")
    
    # Initialize product service
    product_service = ProductService()
    
    # Test search terms
    search_terms = [
        "mall", 
        "shopping", 
        "pizza",
        "delivery",
        "Suceava",
        "bio",
        "antipasti"
    ]
    
    # Test each search term
    for term in search_terms:
        print_section(f"SEARCHING FOR: '{term}'")
        
        # Search for products
        result = product_service.search_products(term, limit=5)
        
        if result.get("status") != "success":
            print(f"Error: {result.get('message', 'Unknown error')}")
            continue
        
        # Get results
        products = result.get("products", [])
        match_summary = result.get("match_summary", {})
        
        # Print summary
        print(f"Found {len(products)} products")
        print(f"Primary match reason: {match_summary.get('primary_match_reason', 'Unknown')}")
        print(f"Match counts:")
        print(f"  Name matches: {match_summary.get('name_matches', 0)}")
        print(f"  Slug matches: {match_summary.get('slug_matches', 0)}")
        print(f"  Description matches: {match_summary.get('description_matches', 0)}")
        print(f"  Category matches: {match_summary.get('category_matches', 0)}")
        print(f"  Category slug matches: {match_summary.get('category_slug_matches', 0)}")
        
        # Print categories
        categories = match_summary.get("categories", {})
        if categories:
            print("\nMatching categories:")
            for cat, count in categories.items():
                print(f"  {cat}: {count} products")
        
        # Print locations
        locations = match_summary.get("locations", {})
        if locations:
            print("\nMatching locations:")
            for loc, count in locations.items():
                print(f"  {loc}: {count} products")
        
        # Print products
        print("\nTop matching products:")
        for i, product in enumerate(products[:3], 1):
            match_info = product.get("match_info", {})
            print(f"\n{i}. {product.get('name', 'Unknown')}")
            print(f"   Slug: {product.get('slug', 'No slug')}")
            
            # Show match reasons
            match_reasons = []
            if match_info.get("name_match"):
                match_reasons.append("name")
            if match_info.get("slug_match"):
                match_reasons.append("slug")
            if match_info.get("description_match"):
                match_reasons.append("description")
            if match_info.get("category_match"):
                match_reasons.append("category name")
            if match_info.get("category_slug_match"):
                match_reasons.append("category slug")
                
            if match_reasons:
                print(f"   Matched in: {', '.join(match_reasons)}")
            
            # Show price if available
            if "price" in product:
                print(f"   Price: {product.get('price')}")
                
            # Show categories
            cats = [c.get("name") for c in product.get("categories", [])]
            if cats:
                print(f"   Categories: {', '.join(cats)}")

if __name__ == "__main__":
    main()
