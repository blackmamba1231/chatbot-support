from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional, Any
from src.services.woocommerce_service import WooCommerceService

# Define router
product_router = APIRouter()

@product_router.get("/")
async def get_products(
    category_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    woocommerce: WooCommerceService = Depends()
):
    """
    Get products from WooCommerce with optional filtering.
    
    Args:
        category_id: Filter by category ID
        page: Page number (starts at 1)
        per_page: Number of products per page (max 100)
        search: Search query string
        
    Returns:
        List of products matching the criteria
    """
    try:
        products = await woocommerce.get_products(
            category_id=category_id,
            page=page,
            per_page=per_page,
            search=search
        )
        
        # Extract location information
        for product in products:
            product["location"] = woocommerce.extract_location_from_product(product)
            product["mall"] = woocommerce.extract_mall_from_product(product)
            
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch products: {str(e)}")

@product_router.get("/categories")
async def get_categories(
    woocommerce: WooCommerceService = Depends()
):
    """
    Get all product categories from WooCommerce.
    
    Returns:
        List of product categories
    """
    try:
        return await woocommerce.get_categories()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch categories: {str(e)}")

@product_router.get("/mall-delivery")
async def get_mall_delivery_products(
    woocommerce: WooCommerceService = Depends()
):
    """
    Get mall delivery products (category ID: 223).
    
    Returns:
        List of mall delivery products
    """
    try:
        products = await woocommerce.get_mall_delivery_products()
        
        # Extract location information
        for product in products:
            product["location"] = woocommerce.extract_location_from_product(product)
            product["mall"] = woocommerce.extract_mall_from_product(product)
            
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch mall delivery products: {str(e)}")

@product_router.get("/locations")
async def get_locations(
    woocommerce: WooCommerceService = Depends()
):
    """
    Get all available delivery locations extracted from product names.
    
    Returns:
        List of available locations
    """
    try:
        # Get mall delivery products
        products = await woocommerce.get_products(category_id=223)  # Mall delivery category
        
        # Extract locations from product names
        locations = set()
        for product in products:
            location = woocommerce.extract_location_from_product(product)
            if location:
                locations.add(location)
        
        return list(locations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch locations: {str(e)}")
            
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch mall delivery products: {str(e)}")

@product_router.get("/restaurants")
async def get_restaurant_products(
    woocommerce: WooCommerceService = Depends()
):
    """
    Get restaurant products (category ID: 546).
    
    Returns:
        List of restaurant products
    """
    try:
        products = await woocommerce.get_restaurant_products()
        
        # Extract location information
        for product in products:
            product["location"] = woocommerce.extract_location_from_product(product)
            
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch restaurant products: {str(e)}")

@product_router.get("/pet-supplies")
async def get_pet_products(
    woocommerce: WooCommerceService = Depends()
):
    """
    Get pet products (category ID: 547).
    
    Returns:
        List of pet products
    """
    try:
        products = await woocommerce.get_pet_products()
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch pet products: {str(e)}")

@product_router.get("/all-services")
async def get_all_services(
    woocommerce: WooCommerceService = Depends()
):
    """
    Get all available services across all categories.
    
    Returns:
        List of all services/products
    """
    try:
        products = await woocommerce.get_all_services()
        
        # Extract location information
        for product in products:
            product["location"] = woocommerce.extract_location_from_product(product)
            product["mall"] = woocommerce.extract_mall_from_product(product)
            
        return products
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch all services: {str(e)}")

@product_router.get("/locations")
async def get_available_locations(
    woocommerce: WooCommerceService = Depends()
):
    """
    Get all available locations from products.
    
    Returns:
        List of unique locations
    """
    try:
        # Get mall delivery products
        products = await woocommerce.get_mall_delivery_products()
        
        # Extract locations
        locations = []
        for product in products:
            location = woocommerce.extract_location_from_product(product)
            if location and location not in locations:
                locations.append(location)
                
        return sorted(locations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch locations: {str(e)}")

@product_router.get("/{product_id}")
async def get_product(
    product_id: int,
    woocommerce: WooCommerceService = Depends()
):
    """
    Get a specific product by ID.
    
    Args:
        product_id: WooCommerce product ID
        
    Returns:
        Product details
    """
    try:
        product = await woocommerce.get_product(product_id)
        
        # Add extracted location info
        product["location"] = woocommerce.extract_location_from_product(product)
        product["mall"] = woocommerce.extract_mall_from_product(product)
        
        return product
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch product: {str(e)}")
