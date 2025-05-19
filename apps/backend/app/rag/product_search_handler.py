from typing import Dict, Any, List, Optional
import logging
import re
from app.services.product_service import ProductService

logger = logging.getLogger(__name__)

def handle_product_search_query(query: str, product_service: ProductService) -> Dict[str, Any]:
    """
    Handle product search queries by using the enhanced product search
    that looks at names, descriptions, slugs, and categories.
    
    Args:
        query: The user's query
        product_service: The product service to use for searching
        
    Returns:
        Dict with response text and any additional data
    """
    # Clean up the query - remove common phrases that aren't part of the search
    clean_query = clean_search_query(query)
    
    # Search for products using our enhanced search
    search_result = product_service.search_products(clean_query, limit=10)
    
    if search_result.get("status") == "error":
        return {
            "response": f"I'm sorry, I couldn't find any products matching '{clean_query}'. Would you like to try a different search?",
            "action": None,
            "data": None
        }
    
    products = search_result.get("products", [])
    match_summary = search_result.get("match_summary", {})
    
    # If no products found
    if not products:
        return {
            "response": f"I couldn't find any products matching '{clean_query}'. Would you like to try a different search?",
            "action": None,
            "data": None
        }
    
    # Generate human-like response based on search results
    response = generate_human_response(clean_query, products, match_summary)
    
    return {
        "response": response,
        "action": "product_search_results",
        "data": {
            "products": products[:5],  # Limit to 5 products for display
            "match_summary": match_summary,
            "search_term": clean_query,
            "total_results": len(products)
        }
    }

def clean_search_query(query: str) -> str:
    """
    Clean up a search query by removing common phrases that aren't part of the search
    
    Args:
        query: The original query
        
    Returns:
        Cleaned search query
    """
    # List of phrases to remove
    phrases_to_remove = [
        r"^(can you |could you |would you |please |find me |search for |look for |i want |i need |i'd like |i would like |show me |get me )",
        r"(products?|items?|goods|things)",
        r"(related to|about|for|that are)",
        r"(thank you|thanks)",
    ]
    
    clean_query = query.lower()
    
    # Apply each regex pattern
    for pattern in phrases_to_remove:
        clean_query = re.sub(pattern, " ", clean_query)
    
    # Remove extra spaces and trim
    clean_query = " ".join(clean_query.split())
    
    return clean_query

def generate_human_response(query: str, products: List[Dict[str, Any]], match_summary: Dict[str, Any]) -> str:
    """
    Generate a natural, human-like response based on search results
    
    Args:
        query: The search query
        products: The list of products found
        match_summary: Summary of match types
        
    Returns:
        Natural language response
    """
    total = match_summary.get("total", 0)
    
    # Get information about how products matched
    primary_match_reason = match_summary.get("primary_match_reason", "products")
    categories = match_summary.get("categories", {})
    locations = match_summary.get("locations", {})
    
    # Start building response
    if total == 0:
        return f"I couldn't find any products matching '{query}'. Would you like to try a different search term?"
    
    # Single product result
    if total == 1:
        product = products[0]
        name = product.get("name", "product")
        response = f"I found 1 product matching '{query}': {name}."
        
        # Add description if available
        if product.get("short_description"):
            # Clean HTML tags from description
            description = re.sub(r'<[^>]+>', '', product.get("short_description", ""))
            if description:
                response += f" {description}"
        
        return response
    
    # Multiple product results
    top_products = [p.get("name") for p in products[:3]]
    
    # Start with primary finding
    response = f"I found {total} products matching '{query}'. "
    
    # If we found by category, mention that
    if categories and len(categories) == 1:
        category = list(categories.keys())[0]
        response = f"I found {total} products in the '{category}' category that match '{query}'. "
    
    # If locations are consistent (like mall delivery services)
    if locations:
        if len(locations) == 1:
            location = list(locations.keys())[0]
            response = f"I found {total} products available in {location} that match '{query}'. "
        elif len(locations) <= 3:  
            location_list = ", ".join(list(locations.keys()))
            response = f"I found {total} products in {location_list} that match '{query}'. "
    
    # Add top product examples
    response += f"Here are a few examples: {', '.join(top_products)}."
    
    # Add call to action
    if total > 3:
        response += f" Would you like to see more products matching '{query}'?"
    
    return response
