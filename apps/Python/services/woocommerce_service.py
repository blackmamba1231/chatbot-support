"""
WooCommerce Service
This module handles interactions with the WooCommerce API to fetch products and categories.
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from requests_oauthlib import OAuth1
from dotenv import load_dotenv
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
CATEGORY_PET_CARE = 547  # ID for pet care
CATEGORY_ALLERGIES = 548  # ID for allergies

class WooCommerceService:
    """Service for interacting with the WooCommerce API"""
    
    def __init__(self, base_url: str, consumer_key: str, consumer_secret: str):
        """Initialize the WooCommerce service with API credentials"""
        self.base_url = base_url.rstrip('/')
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        
        # Define API endpoints
        self.api_url = f"{self.base_url}/wp-json/wc/v3/"
        
        # Log configuration
        logger.info(f"Initializing WooCommerce API with URL: {self.api_url}")
        
        # Define standard API endpoints with full URLs
        self.endpoints = {
            'products': f"{self.api_url}products",
            'categories': f"{self.api_url}products/categories",
            'orders': f"{self.api_url}orders",
            'customers': f"{self.api_url}customers"
        }
        
        # Cache settings
        self.cache = {}
        self.cache_expiration = 3600  # 1 hour
        self.last_sync = 0
    
    def _make_request(self, endpoint: str, method: str = 'GET', params: Dict = None) -> Tuple[bool, Any]:
        """Make an authenticated request to the WooCommerce API"""
        # Check if endpoint is a full URL or just a path
        if endpoint.startswith('http'):
            url = endpoint
        else:
            # If it's a known endpoint, use the predefined URL
            if endpoint in self.endpoints:
                url = self.endpoints[endpoint]
            else:
                # Otherwise, construct the URL from the API base URL
                url = f"{self.api_url}{endpoint.lstrip('/')}"
        
        try:
            logger.info(f"Making {method} request to {url} with params: {params}")
            
            # Create OAuth1 auth object
            auth = OAuth1(self.consumer_key, self.consumer_secret)
            
            if method == 'GET':
                response = requests.get(url, params=params, auth=auth)
            elif method == 'POST':
                response = requests.post(url, json=params, auth=auth)
            elif method == 'PUT':
                response = requests.put(url, json=params, auth=auth)
            elif method == 'DELETE':
                response = requests.delete(url, auth=auth)
            else:
                return False, f"Unsupported method: {method}"
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"API response status: {response.status_code}")
            return True, data
        except Exception as e:
            logger.error(f"API request failed: {str(e)}")
            return False, str(e)
    
    def get_products(self, category: Optional[int] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products with optional category filtering"""
        try:
            # Use the cache if it's less than the expiration time
            cache_key = f"products_{category}_{limit}"
            if cache_key in self.cache and time.time() - self.cache[cache_key]['timestamp'] < self.cache_expiration:
                logger.info("Using cached products data")
                return self.cache[cache_key]['data']
            
            # Use the authenticated API
            params = {
                "per_page": limit,
                "status": "publish"
            }
            if category:
                params["category"] = category
            
            success, data = self._make_request("products", params=params)
            if success and isinstance(data, list):
                # Cache the results
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': time.time()
                }
                return data
            
            logger.warning(f"Failed to fetch products: {data}")
            return []
        except Exception as e:
            logger.error(f"Error in get_products: {str(e)}")
            return []
    
    def get_categories(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get all product categories"""
        try:
            cache_key = "categories"
            if use_cache and cache_key in self.cache and time.time() - self.cache[cache_key]['timestamp'] < self.cache_expiration:
                logger.info("Using cached categories data")
                return self.cache[cache_key]['data']
            
            success, data = self._make_request("categories")
            if success and isinstance(data, list):
                # Cache the results
                self.cache[cache_key] = {
                    'data': data,
                    'timestamp': time.time()
                }
                return data
            
            logger.warning(f"Failed to fetch categories: {data}")
            return []
        except Exception as e:
            logger.error(f"Error in get_categories: {str(e)}")
            return []
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID"""
        try:
            success, data = self._make_request(f"products/{product_id}")
            return data if success else None
        except Exception as e:
            logger.error(f"Error in get_product: {str(e)}")
            return None
    
    def get_mall_delivery_services(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get mall delivery services, optionally filtered by location"""
        params = {
            "category": CATEGORY_MALL_DELIVERY,
            "per_page": 100
        }
        
        if location:
            params["search"] = location.lower().replace(" ", "-")
        
        success, response = self._make_request("products", params=params)
        if success and isinstance(response, list):
            services = [{
                "id": item["id"],
                "name": item["name"],
                "description": item.get("description", ""),
                "short_description": item.get("short_description", ""),
                "price": item.get("price", ""),
                "images": [img["src"] for img in item.get("images", [])],
                "categories": [cat["name"] for cat in item.get("categories", [])],
                "tags": [tag["name"] for tag in item.get("tags", [])]
            } for item in response]
            
            return {
                "status": "success",
                "services": services
            }
        return {"status": "error", "message": str(response)}

    def get_products_by_category(self, category_id: int, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Get products by category ID with optional location filtering"""
        try:
            cache_key = f"products_cat_{category_id}_loc_{location}_limit_{limit}"
            if cache_key in self.cache and time.time() - self.cache[cache_key]['timestamp'] < self.cache_expiration:
                logger.info(f"Using cached products for category {category_id}")
                return self.cache[cache_key]['data']
            
            params = {
                "category": category_id,
                "per_page": limit,
                "status": "publish"
            }
            
            if location:
                params["search"] = location
            
            success, response = self._make_request("products", params=params)
            
            if success and isinstance(response, list):
                # Format the data
                products = []
                for item in response:
                    # Extract location from name if available
                    product_location = location
                    if not product_location and "-" in item.get("name", ""):
                        parts = item["name"].split("-", 1)
                        if len(parts) > 1 and parts[0].strip():
                            product_location = parts[0].strip()
                    
                    # Create product object
                    product = {
                        "id": item["id"],
                        "name": item["name"],
                        "description": item.get("description", ""),
                        "short_description": item.get("short_description", ""),
                        "price": item.get("price", ""),
                        "images": [img["src"] for img in item.get("images", [])],
                        "categories": [cat["name"] for cat in item.get("categories", [])],
                        "location": product_location
                    }
                    
                    products.append(product)
                
                # Cache the results
                self.cache[cache_key] = {
                    'data': products,
                    'timestamp': time.time()
                }
                
                return products
            
            logger.warning(f"Failed to fetch products for category {category_id}: {response}")
            return []
        except Exception as e:
            logger.error(f"Error in get_products_by_category: {str(e)}")
            return []
    
    def search_products(self, query: str, location: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for products by keyword with optional location filtering"""
        try:
            cache_key = f"search_{query}_loc_{location}_limit_{limit}"
            if cache_key in self.cache and time.time() - self.cache[cache_key]['timestamp'] < self.cache_expiration:
                logger.info(f"Using cached search results for '{query}'")
                return self.cache[cache_key]['data']
            
            params = {
                "search": query,
                "per_page": limit,
                "status": "publish"
            }
            
            if location:
                # We'll search for products that match both query and location
                params["search"] = f"{query} {location}"
            
            success, response = self._make_request("products", params=params)
            
            if success and isinstance(response, list):
                # Format the data
                products = []
                for item in response:
                    # Create product object
                    product = {
                        "id": item["id"],
                        "name": item["name"],
                        "description": item.get("description", ""),
                        "short_description": item.get("short_description", ""),
                        "price": item.get("price", ""),
                        "images": [img["src"] for img in item.get("images", [])],
                        "categories": [cat["name"] for cat in item.get("categories", [])],
                        "location": location
                    }
                    
                    products.append(product)
                
                # Cache the results
                self.cache[cache_key] = {
                    'data': products,
                    'timestamp': time.time()
                }
                
                return products
            
            logger.warning(f"Failed to search products for '{query}': {response}")
            return []
        except Exception as e:
            logger.error(f"Error in search_products: {str(e)}")
            return []
    
    def get_kids_activities(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get kids activities, optionally filtered by location"""
        params = {
            "category": CATEGORY_KIDS_ACTIVITIES,
            "per_page": 100
        }
        
        if location:
            params["search"] = location
        
        success, products = self._make_request("products", method="GET", params=params)
        if not success:
            return {"status": "error", "message": products}
        
        activities = [
            {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "image_url": product["images"][0]["src"] if product["images"] else None,
            }
            for product in products
        ]
        
        return {
            "status": "success",
            "activities": activities
        }
    
    def get_bio_food(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get bio food products, optionally filtered by location"""
        params = {
            "category": CATEGORY_BIO_FOOD,
            "per_page": 100
        }
        
        if location:
            params["search"] = location
        
        success, products = self._make_request("products", method="GET", params=params)
        if not success:
            return {"status": "error", "message": products}
        
        food_items = [
            {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "image_url": product["images"][0]["src"] if product["images"] else None,
            }
            for product in products
        ]
        
        return {
            "status": "success",
            "food_items": food_items
        }
    
    def get_antipasti(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get antipasti products, optionally filtered by location"""
        params = {
            "category": CATEGORY_ANTIPASTI,
            "per_page": 100
        }
        
        if location:
            params["search"] = location
        
        success, products = self._make_request("products", method="GET", params=params)
        if not success:
            return {"status": "error", "message": products}
        
        antipasti_items = [
            {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "image_url": product["images"][0]["src"] if product["images"] else None,
            }
            for product in products
        ]
        
        return {
            "status": "success",
            "antipasti_items": antipasti_items
        }
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        try:
            success, response = self._make_request("orders", method="POST", params=order_data)
            if success:
                return {"status": "success", "order": response}
            return {"status": "error", "message": str(response)}
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """Get order details by ID"""
        try:
            success, response = self._make_request(f"orders/{order_id}")
            if success:
                return {"status": "success", "order": response}
            return {"status": "error", "message": str(response)}
        except Exception as e:
            logger.error(f"Error getting order: {str(e)}")
            return {"status": "error", "message": str(e)}
