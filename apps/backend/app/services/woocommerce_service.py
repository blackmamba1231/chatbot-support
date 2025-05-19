import os
import json
import time
import requests
import logging
from requests_oauthlib import OAuth1
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime

logger = logging.getLogger(__name__)

# Constants for product categories and tags
CATEGORY_MALL_DELIVERY = 223  # ID for mall-delivery category
CATEGORY_MALL_DELIVERY_SLUG = "mall-delivery"  # Slug for mall-delivery category

# Pet Care Categories
CATEGORY_PET_CARE = 547  # ID for pet care
CATEGORY_PET_CARE_SLUG = "animale-de-companie"

# Educational and Activities Categories
CATEGORY_KIDS_ACTIVITIES = 228  # ID for educational activities
CATEGORY_KIDS_ACTIVITIES_SLUG = "copii-educatie-hrana-activitati"

# Restaurant Category
CATEGORY_RESTAURANT = 546  # ID for restaurant category 
CATEGORY_RESTAURANT_SLUG = "restaurante"

# Pharmacy category
CATEGORY_PHARMACY = 794  # ID for pharmacies
CATEGORY_PHARMACY_SLUG = "farmacii-non-stop-in-romania"

# Category for uncategorized
CATEGORY_UNCATEGORIZED = 73
CATEGORY_UNCATEGORIZED_SLUG = "uncategorized"

# Common locations based on the product data
LOCATIONS = [
    "Alba Iulia",
    "Alexandria",
    "Arad",
    "Bacău",
    "Baia Mare",
    "Bistrița",
    "Botoșani",
    "Brașov",
    "Brăila",
    "Bucharest",
    "Buftea",
    "Buzău",
    "Călărași",
    "Cluj-Napoca",
    "Craiova",
    "Miercurea Ciuc",
    "Târgu Mureș",
    "Vaslui",
    # Add more locations from the _available_cities meta field
]

class WooCommerceService:
    def __init__(self):
        """Initialize the WooCommerce API service"""
        # Get credentials from environment variables with default values from the manually tested API call
        self.base_url = os.environ.get("WP_API_URL", "https://vogo.family").rstrip('/')
        self.consumer_key = os.environ.get("WP_CONSUMER_KEY", "ck_91e6fa3aac7b5c40ac5a9a1ec0743c0791472e62")
        self.consumer_secret = os.environ.get("WP_CONSUMER_SECRET", "cs_28bfe71efc2e7f71269236e79d47a896b96305a2")
        
        # Define API endpoints
        self.api_url = f"{self.base_url}/wp-json/wc/v3/"
        
        # Log configuration
        logger.info(f"Initializing WooCommerce API with URL: {self.api_url}")
        logger.info("Using provided API credentials")
        
        # Initialize wcapi attribute for compatibility with code that expects it
        self.wcapi = None  # No longer using session-based auth
        
        # Define standard API endpoints with full URLs
        self.endpoints = {
            'products': f"{self.api_url}products",
            'categories': f"{self.api_url}products/categories",
            'orders': f"{self.api_url}orders",
            'customers': f"{self.api_url}customers"
        }
        
        # Log the endpoints for debugging
        logger.info(f"API endpoints: {self.endpoints}")
        
        # Cache settings
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        self.cache_expiration = 3600  # 1 hour
        
        # Initialize cache
        self.cache = {
            "categories": self._load_cache("categories"),
            "products": self._load_cache("products")
        }
        
        # Use a temporary directory for kb to avoid permission issues
        import tempfile
        # Store cache in a temp file instead of directory
        kb_file = os.path.join(tempfile.gettempdir(), "chatbot_kb.json")
        os.makedirs(os.path.dirname(kb_file), exist_ok=True)
        self.kb_path = kb_file
        logger.info(f"Using knowledge base file: {self.kb_path}")

    def _get_cache_path(self, cache_type: str) -> str:
        """Get the path for a specific cache file"""
        return os.path.join(self.cache_dir, f"{cache_type}_cache.json")
        
    def _get_products_authenticated(self, **params) -> List[Dict[str, Any]]:
        """Get products using authenticated API access
        
        Args:
            **params: Additional parameters to pass to the API
            
        Returns:
            List of product data dictionaries
        """
        success, data = self._make_request('products', params=params)
        if success and isinstance(data, list):
            return data
        return []
    
    def _load_cache(self, cache_type: str) -> Dict[str, Any]:
        """Load cache for a specific type of data"""
        cache_path = self._get_cache_path(cache_type)
        try:
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache = json.load(f)
                if time.time() - cache.get('timestamp', 0) < self.cache_expiration:
                    return cache.get('data', {})
        except Exception as e:
            logger.error(f"Error loading {cache_type} cache: {str(e)}")
        # Try to sync data from API
        success, data = self._make_request(cache_type)
        if success:
            self._save_cache(cache_type, data)
            return data
        return {}
    
    def _save_cache(self, cache_type: str, data: Dict[str, Any]):
        """Save cache for a specific type of data"""
        cache_path = self._get_cache_path(cache_type)
        try:
            cache = {
                'timestamp': time.time(),
                'data': data
            }
            with open(cache_path, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            logger.error(f"Error saving {cache_type} cache: {str(e)}")
            
    def _get_cached_data(self) -> Optional[Dict[str, Any]]:
        """Get all cached data"""
        try:
            # Combine all cached data into a single dictionary
            result = {}
            for cache_type, cache_data in self.cache.items():
                if cache_data:
                    result[cache_type] = cache_data
            return result
        except Exception as e:
            logger.error(f"Error getting cached data: {str(e)}")
            return None
    
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
    
    def get_categories(self, use_cache: bool = True) -> List[Dict[str, Any]]:
        """Get all product categories"""
        if use_cache and self.cache["categories"]:
            return self.cache["categories"]
        
        success, data = self._make_request('categories')
        if success:
            self._save_cache("categories", data)
            return data
        return []
    
    def get_kids_activities(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get kids activities, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_KIDS_ACTIVITIES,
                "per_page": 100,
                "status": "publish"
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
                if self._is_kids_activity(product)
            ]

            return {
                "status": "success",
                "activities": activities
            }

        except Exception as e:
            logger.error(f"Error fetching kids activities: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_bio_food(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get bio food products, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_BIO_FOOD,
                "per_page": 100,
                "status": "publish"
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
                if self._is_bio_food(product)
            ]

            return {
                "status": "success",
                "food_items": food_items
            }

        except Exception as e:
            logger.error(f"Error fetching bio food: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_antipasti(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get antipasti products, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_ANTIPASTI,
                "per_page": 100,
                "status": "publish"
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
                if self._is_antipasti(product)
            ]

            return {
                "status": "success",
                "antipasti_items": antipasti_items
            }

        except Exception as e:
            logger.error(f"Error fetching antipasti: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_pet_care(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get pet care products, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_PET_CARE,
                "per_page": 100,
                "status": "publish"
            }

            if location:
                params["search"] = location

            success, products = self._make_request("products", method="GET", params=params)
            if not success:
                return {"status": "error", "message": products}

            pet_items = [
                {
                    "id": product["id"],
                    "name": product["name"],
                    "description": product["description"],
                    "price": product["price"],
                    "image_url": product["images"][0]["src"] if product["images"] else None,
                }
                for product in products
                if self._is_pet_care(product)
            ]

            return {
                "status": "success",
                "pet_items": pet_items
            }

        except Exception as e:
            logger.error(f"Error fetching pet care items: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_allergy_products(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get allergy-related products, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_ALLERGIES,
                "per_page": 100,
                "status": "publish"
            }

            if location:
                params["search"] = location

            success, products = self._make_request("products", method="GET", params=params)
            if not success:
                return {"status": "error", "message": products}

            allergy_items = [
                {
                    "id": product["id"],
                    "name": product["name"],
                    "description": product["description"],
                    "price": product["price"],
                    "image_url": product["images"][0]["src"] if product["images"] else None,
                }
                for product in products
                if self._is_allergy(product)
            ]

            return {
                "status": "success",
                "allergy_items": allergy_items
            }

        except Exception as e:
            logger.error(f"Error fetching allergy products: {str(e)}")
            return {"status": "error", "message": str(e)}
            
            if location:
                params["search"] = location  # Use search parameter for location filtering
            
            # Make request to WooCommerce API
            success, products = self._make_request('products', params=params)
            
            if success:
                restaurants = []
                
                for item in products:
                    # Filter by location in product name if location is specified
                    if location and location.lower() not in item.get("name", "").lower():
                        continue
                        
                    restaurants.append({
                        "id": item["id"],
                        "name": item["name"],
                        "description": item.get("description", ""),
                        "short_description": item.get("short_description", ""),
                        "price": item.get("price", ""),
                        "regular_price": item.get("regular_price", ""),
                        "sale_price": item.get("sale_price", ""),
                        "images": [img["src"] for img in item.get("images", [])],
                        "categories": [cat["name"] for cat in item.get("categories", [])],
                        "tags": [tag["name"] for tag in item.get("tags", [])],
                        "location": location or "All locations"
                    })
                
                logger.info(f"Found {len(restaurants)} restaurants{' for ' + location if location else ''}")
                return {"status": "success", "restaurants": restaurants}
            else:
                error_msg = f"Failed to fetch restaurants: {response.status_code}"
                logger.error(error_msg)
                return {"status": "error", "message": error_msg}
                
        except Exception as e:
            error_msg = f"Error getting restaurants: {str(e)}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}
    
    def _is_kids_activity(self, product: Dict[str, Any]) -> bool:
        """Check if a product is a kids activity"""
        category_ids = [cat.get("id") for cat in product.get("categories", [])]
        category_slugs = [cat.get("slug") for cat in product.get("categories", [])]
        return CATEGORY_KIDS_ACTIVITIES in category_ids or CATEGORY_KIDS_ACTIVITIES_SLUG in category_slugs

    def _is_bio_food(self, product: Dict[str, Any]) -> bool:
        """Check if a product is a bio food item"""
        category_ids = [cat.get("id") for cat in product.get("categories", [])]
        category_slugs = [cat.get("slug") for cat in product.get("categories", [])]
        return CATEGORY_BIO_FOOD in category_ids or CATEGORY_BIO_FOOD_SLUG in category_slugs

    def _is_antipasti(self, product: Dict[str, Any]) -> bool:
        """Check if a product is an antipasti item"""
        category_ids = [cat.get("id") for cat in product.get("categories", [])]
        category_slugs = [cat.get("slug") for cat in product.get("categories", [])]
        return CATEGORY_ANTIPASTI in category_ids or CATEGORY_ANTIPASTI_SLUG in category_slugs

    def _is_pet_care(self, product: Dict[str, Any]) -> bool:
        """Check if a product is a pet care item"""
        category_ids = [cat.get("id") for cat in product.get("categories", [])]
        category_slugs = [cat.get("slug") for cat in product.get("categories", [])]
        return CATEGORY_PET_CARE in category_ids or CATEGORY_PET_CARE_SLUG in category_slugs

    def _is_allergy(self, product: Dict[str, Any]) -> bool:
        """Check if a product is an allergy-related item"""
        category_ids = [cat.get("id") for cat in product.get("categories", [])]
        category_slugs = [cat.get("slug") for cat in product.get("categories", [])]
        return CATEGORY_ALLERGIES in category_ids or CATEGORY_ALLERGIES_SLUG in category_slugs
    
    def get_mall_delivery_services(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get mall delivery services, optionally filtered by location"""
        params = {
            "category": CATEGORY_MALL_DELIVERY,
            "per_page": 100
        }
        
        if location:
            # Check in available cities metadata
            params["search"] = location
        
        success, products = self._make_request("products", params=params)
        if success and isinstance(products, list):
            services = [{
                "id": item["id"],
                "name": item["name"],
                "description": item.get("description", ""),
                "short_description": item.get("short_description", ""),
                "price": item.get("price", ""),
                "images": [img["src"] for img in item.get("images", [])],
                "categories": [cat["name"] for cat in item.get("categories", [])],
                "tags": [tag["name"] for tag in item.get("tags", [])]
            } for item in products if self._is_mall_service(item)]
            
            return {
                "status": "success",
                "services": services
            }
        return {"status": "error", "message": str(products)}
    
    def _is_mall_service(self, product: Dict[str, Any]) -> bool:
        """Check if a product is a mall delivery service"""
        category_ids = [cat.get("id") for cat in product.get("categories", [])]
        category_slugs = [cat.get("slug") for cat in product.get("categories", [])]
        return CATEGORY_MALL_DELIVERY in category_ids or CATEGORY_MALL_DELIVERY_SLUG in category_slugs
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID"""
        success, response = self._make_request(f"products/{product_id}")
        if success:
            return response
        return None
    
    def get_locations(self) -> List[str]:
        """Get all available locations"""
        return LOCATIONS
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        success, response = self._make_request("orders", method="POST", params=order_data)
        if success:
            return {"status": "success", "order": response}
        return {"status": "error", "message": str(response)}
    
    def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order details by ID"""
        success, response = self._make_request(f"orders/{order_id}")
        if success:
            return response
        return None

    
    def _is_cache_expired(self, cached_data: Dict[str, Any]) -> bool:
        """Check if the cache has expired"""
        if 'timestamp' not in cached_data:
            return True
        
        cache_time = cached_data['timestamp']
        current_time = time.time()
        
        return (current_time - cache_time) > self.cache_expiration
    
    def _cache_data(self, data: Dict[str, Any]) -> None:
        """Cache the data to disk"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
            
            # Add timestamp to the data
            data['timestamp'] = time.time()
            
            # Write to file
            with open(self.kb_path, 'w') as f:
                json.dump(data, f)
                
            logger.info(f"Cached WooCommerce data to {self.kb_path}")
        except Exception as e:
            logger.error(f"Error caching data: {str(e)}")
    
    def get_products(self, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products from WooCommerce API
        
        Args:
            category: Optional category filter
            limit: Maximum number of products to return
            
        Returns:
            List of product dictionaries
        """
        try:
            # Check if we have a valid cache that's not expired
            cached_data = self._get_cached_data()
            if cached_data and not self._is_cache_expired(cached_data) and 'products' in cached_data:
                products = cached_data['products']
                
                # Filter by category if specified
                if category and products:
                    # Check if category is a numeric ID or a slug
                    try:
                        category_id = int(category)
                        products = [p for p in products if any(cat.get('id') == category_id for cat in p.get('categories', []))]
                    except ValueError:
                        # If not a numeric ID, treat as a slug
                        products = [p for p in products if any(cat.get('slug') == category for cat in p.get('categories', []))]
                
                logger.info(f"Using cached products data ({len(products)} products)")
                return products[:limit]
            
            # Use the authenticated API
            params = {
                "per_page": limit,
                "status": "publish"
            }
            
            # Add category filter if specified
            if category:
                # Try to determine if it's a numeric ID or a slug
                try:
                    int(category)  # Will raise ValueError if not a number
                    params["category"] = category
                except ValueError:
                    # Find category ID by slug
                    success, categories = self._make_request("products/categories")
                    if success:
                        for cat in categories:
                            if cat.get("slug") == category:
                                params["category"] = cat.get("id")
                                break
                    else:
                        # If can't find category ID, use slug in search
                        params["search"] = category
                        
            success, data = self._make_request("products", params=params)
            if success and isinstance(data, list):
                # Cache the products for future use
                self._update_cache_with_products(data)
                return data[:limit]
            
            logger.warning(f"Failed to fetch products: {data}")
            return []

        except Exception as e:
            logger.error(f"Error in get_products: {str(e)}")
            return []

    def get_product_categories(self) -> List[Dict[str, Any]]:
        """
        Get product categories from WooCommerce API
        
        Returns:
            List of category dictionaries
        """
        try:
            # Check if we have cached data and it's not expired
            cached_data = self._get_cached_data()
            if cached_data and not self._is_cache_expired(cached_data):
                return cached_data.get("categories", [])
            
            # Cache is expired or doesn't exist, fetch from API
            response = self.wcapi.get("products/categories")
            
            if response.status_code != 200:
                logger.error(f"Failed to fetch product categories: {response.status_code} - {response.text}")
                return []
            
            categories = response.json()
            logger.info(f"Fetched {len(categories)} product categories from WooCommerce API")
            
            # Cache the data
            cached_data = self._get_cached_data() or {}
            cached_data["categories"] = categories
            self._cache_data(cached_data)
            
            return categories
        except Exception as e:
            logger.error(f"Error fetching product categories from WooCommerce API: {str(e)}")
            # Fall back to cache if available
            cached_data = self._get_cached_data()
            if cached_data and "categories" in cached_data:
                return cached_data["categories"]
            return []
            
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order in WooCommerce
        
        Args:
            order_data: Order data including line_items, shipping, billing info
            
        Returns:
            Created order data or error information
        """
        try:
            logger.info(f"Creating WooCommerce order with data: {json.dumps(order_data)}")
            
            # Make the API request to create the order
            response = self.wcapi.post("orders", order_data)
            
            if response.status_code in [200, 201]:
                order = response.json()
                logger.info(f"Successfully created order #{order.get('id')}")
                return {
                    "status": "success",
                    "order": order
                }
            else:
                logger.error(f"Failed to create order: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"Failed to create order: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"Error creating order in WooCommerce: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating order: {str(e)}"
            }
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID
        
        Args:
            product_id: The WooCommerce product ID
            
        Returns:
            Product data or None if not found
        """
        try:
            # Check if we have cached data
            cached_data = self._get_cached_data()
            if cached_data and "products" in cached_data:
                for product in cached_data["products"]:
                    if product.get("id") == product_id:
                        return product
            
            # Not found in cache, fetch from API
            response = self.wcapi.get(f"products/{product_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch product {product_id}: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            return None
    
    def get_order_status(self, order_id: int) -> Dict[str, Any]:
        """Get the status of an order
        
        Args:
            order_id: The WooCommerce order ID
            
        Returns:
            Order status information
        """
        try:
            response = self.wcapi.get(f"orders/{order_id}")
            
            if response.status_code == 200:
                order = response.json()
                return {
                    "status": "success",
                    "order_status": order.get("status"),
                    "order": order
                }
            else:
                logger.error(f"Failed to fetch order {order_id}: {response.status_code} - {response.text}")
                return {
                    "status": "error",
                    "message": f"Failed to fetch order: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error fetching order {order_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching order: {str(e)}"
            }

    def get_service_locations(self) -> List[Dict[str, Any]]:
        """
        Get service locations from product attributes in WooCommerce
        
        Returns:
            List of service location dictionaries
        """
        # Get products from API
        products = self.get_products()
        locations = []
        
        for product in products:
            # Check if this product has location attributes
            for attribute in product.get("attributes", []):
                if attribute["name"].lower() in ["location", "address", "service location"]:
                    locations.append({
                        "id": f"location_{product['id']}",
                        "name": product["name"],
                        "address": attribute["options"][0] if attribute["options"] else "",
                        "product_id": product["id"]
                    })
        
        return locations

    def sync_knowledge_base(self, force: bool = False) -> bool:
        """
        Sync the knowledge base with the latest data from WooCommerce
        
        Args:
            force: Force sync even if the cache hasn't expired
            
        Returns:
            True if sync was successful, False otherwise
        """
        # Check if we need to sync
        if not force and self.last_sync and (datetime.now() - self.last_sync).total_seconds() < self.cache_expiration:
            return True
        
        try:
            # Get food delivery products (assuming they're in the food-delivery category)
            food_products = self.get_products(category="food-delivery")
            
            # If no specific category exists, get all products
            if not food_products:
                food_products = self.get_products()
            
            # Transform products into the format expected by the RAG engine
            restaurants = []
            
            for product in food_products:
                # Extract specialties from tags or categories
                specialties = []
                for tag in product.get("tags", []):
                    specialties.append(tag["name"])
                
                # Extract location from attributes
                location = "Online"
                contact = ""
                hours = ""
                
                for attribute in product.get("attributes", []):
                    if attribute["name"].lower() == "location":
                        location = attribute["options"][0] if attribute["options"] else "Online"
                    elif attribute["name"].lower() == "contact":
                        contact = attribute["options"][0] if attribute["options"] else ""
                    elif attribute["name"].lower() == "hours":
                        hours = attribute["options"][0] if attribute["options"] else ""
                
                # Extract cuisine type from categories
                cuisine = "traditional"
                for category in product.get("categories", []):
                    category_name = category.get("name", "").lower()
                    if "italian" in category_name or "pizza" in category_name:
                        cuisine = "italian"
                    elif "grecesc" in category_name:
                        cuisine = "grecesc"
                    elif "spaniol" in category_name:
                        cuisine = "spaniol"
                    elif "vegan" in category_name:
                        cuisine = "vegan"
                    elif "arabesc" in category_name:
                        cuisine = "arabesc"
                    elif "asia" in category_name or "asian" in category_name or "chinese" in category_name:
                        cuisine = "asia"
                    elif "traditional" in category_name or "romanian" in category_name:
                        cuisine = "traditional"
                    elif "sport" in category_name:
                        cuisine = "sport"
                    elif "pizza" in category_name:
                        cuisine = "pizza"
                
                restaurant = {
                    "id": str(product['id']),
                    "name": product["name"],
                    "description": product["short_description"].strip() or product["description"].strip(),
                    "cuisine": cuisine,
                    "address": location,
                    "phone": contact,
                    "rating": float(product.get("average_rating", 4.5)),
                    "hours": hours,
                    "price": product["price"],
                    "image": product["images"][0]["src"] if product.get("images") else ""
                }
                
                restaurants.append(restaurant)
            
            # Get cuisine categories from products
            cuisine_categories = {}
            for restaurant in restaurants:
                cuisine = restaurant.get("cuisine")
                if cuisine and cuisine not in cuisine_categories:
                    cuisine_categories[cuisine] = {
                        "name": cuisine.capitalize(),
                        "description": f"{cuisine.capitalize()} cuisine from local restaurants",
                        "image": next((r["image"] for r in restaurants if r.get("cuisine") == cuisine and r.get("image")), "")
                    }
            
            # Get delivery information
            delivery_info = {
                "delivery_areas": [
                    "Alba Iulia", "Arad", "Miercurea Ciuc", "Vaslui", "Bucharest", "Bacău"
                ],
                "delivery_times": {
                    "standard": "30-60 minutes",
                    "express": "15-30 minutes"
                },
                "delivery_fees": {
                    "standard": "10 RON",
                    "express": "20 RON"
                }
            }

            kb_data = {
                "restaurants": restaurants,
                "cuisine_categories": cuisine_categories,
                "delivery_info": delivery_info
            }

            with open(self.kb_path, 'w') as f:
                json.dump(kb_data, f, indent=2)

            self.last_sync = datetime.now().timestamp()

            return True

        except Exception as e:
            logger.error(f"Error syncing knowledge base: {e}")
            return False

    def _should_use_cache(self) -> bool:
        """Check if we should use cached data based on last sync time"""
        try:
            # If the cache file doesn't exist, we can't use it
            if not os.path.exists(self.kb_path):
                return False
                
            # Check when the file was last modified
            file_mod_time = os.path.getmtime(self.kb_path)
            current_time = time.time()
            
            # If it's been less than cache_expiration seconds, use the cache
            return (current_time - file_mod_time) < self.cache_expiration
        except Exception as e:
            logger.error(f"Error checking cache: {str(e)}")
            return False
    
    def _load_from_cache(self) -> Dict[str, Any]:
        """Load data from cache file"""
        try:
            if os.path.exists(self.kb_path):
                with open(self.kb_path, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Error loading from cache: {str(e)}")
            return {}
    
    def _update_cache_with_products(self, products: List[Dict[str, Any]]) -> None:
        """Update cache with new products data"""
        try:
            # Load existing cache
            cached_data = self._load_from_cache()
            
            # Update products
            cached_data['products'] = products
            cached_data['last_updated'] = datetime.now().isoformat()
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
            
            # Write to file
            with open(self.kb_path, 'w') as f:
                json.dump(cached_data, f, indent=2)
                
            # Update last sync time
            self.last_sync = time.time()
        except Exception as e:
            logger.error(f"Error updating cache with products: {str(e)}")
    
    def _update_cache_with_categories(self, categories: List[Dict[str, Any]]) -> None:
        """Update cache with new categories data"""
        try:
            # Load existing cache
            cached_data = self._load_from_cache()
            
            # Update categories
            cached_data['categories'] = categories
            cached_data['last_updated'] = datetime.now().isoformat()
            
            # Ensure the directory exists
            os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
            
            # Write to file
            with open(self.kb_path, 'w') as f:
                json.dump(cached_data, f, indent=2)
                
            self.last_sync = time.time()
        except Exception as e:
            logger.error(f"Error updating cache with categories: {str(e)}")
    
    def sync_data(self, force: bool = False) -> bool:
        """
        Sync data from WooCommerce API to local cache
        
        Args:
            force: Force sync even if cache is still valid
            
        Returns:
            bool: True if sync was successful, False otherwise
        """
        try:
            # Check if we should use cached data
            if not force and self._should_use_cache():
                logger.info("Using cached data (still valid)")
                return True
            
            # Get products using _make_request
            logger.info("Fetching products...")
            success, products = self._make_request('products', params={"per_page": 100})
            if not success:
                logger.error(f"Failed to fetch products: {products}")
                return False
            self._update_cache_with_products(products)
            
            # Get categories using _make_request
            logger.info("Fetching categories...")
            success, categories = self._make_request('categories')
            if not success:
                logger.error(f"Failed to fetch categories: {categories}")
                return False
            self._update_cache_with_categories(categories)
            
            # Update last sync time
            self.last_sync = time.time()
            return True
        except Exception as e:
            logger.error(f"Error syncing data from WooCommerce API: {str(e)}")
            return False

    
    def get_service_by_id(self, service_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific mock service by ID
        
        Args:
            service_id: The service ID to look for
            
        Returns:
            Service dictionary or None if not found
        """
        # Check if the ID is a product ID
        if service_id.startswith("service_"):
            try:
                product_id = int(service_id.replace("service_", ""))
                # Find the product with this ID
                products = self.get_products()
                for product in products:
                    if product["id"] == product_id:
                        # Transform to service format
                        specialties = []
                        for tag in product.get("tags", []):
                            specialties.append(tag["name"])
                        
                        location = "Online"
                        contact = ""
                        hours = ""
                        
                        for attribute in product.get("attributes", []):
                            if attribute["name"].lower() == "location":
                                location = attribute["options"][0] if attribute["options"] else "Online"
                            elif attribute["name"].lower() == "contact":
                                contact = attribute["options"][0] if attribute["options"] else ""
                            elif attribute["name"].lower() == "hours":
                                hours = attribute["options"][0] if attribute["options"] else ""
                        
                        return {
                            "id": service_id,
                            "name": product["name"],
                            "description": product["short_description"].strip() or product["description"].strip(),
                            "location": location,
                            "contact": contact,
                            "website": "https://vogo.family",
                            "specialties": specialties,
                            "hours": hours,
                            "price": product["price"],
                            "image": product["images"][0]["src"] if product.get("images") else ""
                        }
            except (ValueError, KeyError):
                pass
        
        # If not found or not a WooCommerce ID, try the local knowledge base
        try:
            with open(self.kb_path, 'r') as f:
                kb_data = json.load(f)
                
            for service in kb_data.get("services", []):
                if service["id"] == service_id:
                    return service
                    
        except Exception as e:
            logger.error(f"Error getting service by ID: {e}")
            
        return None

    def get_mall_delivery_services(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get mall delivery services, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_MALL_DELIVERY,
                "per_page": 100,
                "status": "publish"
            }
            
            if location:
                # Check in available cities metadata
                params["search"] = location
            
            success, products = self._make_request("products", params=params)
            if not success:
                return {"status": "error", "message": products}
            
            services = []
            for product in products:
                # Extract location from product name or metadata
                product_location = self._extract_location_from_product(product)
                
                # If location is specified and doesn't match, skip this product
                if location and location.lower() not in product_location.lower():
                    continue
                
                # Extract available_cities from metadata if it exists
                available_cities = self._get_meta_value(product, "_available_cities")
                
                # Extract available_malls from metadata if it exists
                available_malls = self._get_meta_value(product, "_available_malls")
                
                services.append({
                    "id": product["id"],
                    "name": product["name"],
                    "slug": product.get("slug", ""),
                    "description": product.get("description", ""),
                    "short_description": product.get("short_description", ""),
                    "price": product.get("price", ""),
                    "regular_price": product.get("regular_price", ""),
                    "sale_price": product.get("sale_price", ""),
                    "images": [img["src"] for img in product.get("images", [])],
                    "categories": [cat["name"] for cat in product.get("categories", [])],
                    "tags": [tag["name"] for tag in product.get("tags", [])],
                    "location": product_location,
                    "available_cities": available_cities,
                    "available_malls": available_malls
                })
            
            return {
                "status": "success",
                "services": services
            }
        except Exception as e:
            logger.error(f"Error fetching mall delivery services: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _extract_location_from_product(self, product: Dict[str, Any]) -> str:
        """Extract location from product name or metadata"""
        # Try to extract from name (some products have format "Location - Store Name")
        name = product.get("name", "")
        if " - " in name:
            location = name.split(" - ")[0].strip()
            return location
        
        # Try to get from available_cities metadata
        available_cities = self._get_meta_value(product, "_available_cities")
        if available_cities and isinstance(available_cities, list) and len(available_cities) > 0:
            return available_cities[0]
        
        return "Unknown"
    
    def _get_meta_value(self, product: Dict[str, Any], meta_key: str) -> Any:
        """Get a value from product metadata by key"""
        if "meta_data" not in product:
            return None
            
        for meta in product["meta_data"]:
            if meta.get("key") == meta_key:
                return meta.get("value")
                
        return None
    
    def _is_mall_service(self, product: Dict[str, Any]) -> bool:
        """Check if a product is a mall delivery service"""
        if not product.get("categories"):
            return False
            
        category_ids = [cat.get("id") for cat in product.get("categories", [])]
        category_slugs = [cat.get("slug") for cat in product.get("categories", [])]
        
        return CATEGORY_MALL_DELIVERY in category_ids or CATEGORY_MALL_DELIVERY_SLUG in category_slugs

    def get_restaurant_services(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get restaurant services, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_RESTAURANT,
                "per_page": 100,
                "status": "publish"
            }
            
            if location:
                params["search"] = location
            
            success, products = self._make_request("products", params=params)
            if not success:
                return {"status": "error", "message": products}
            
            restaurants = []
            for product in products:
                # Extract location from product name or metadata
                product_location = self._extract_location_from_product(product)
                
                # If location is specified and doesn't match, skip this product
                if location and location.lower() not in product_location.lower():
                    continue
                
                # Extract available_cities from metadata if it exists
                available_cities = self._get_meta_value(product, "_available_cities")
                
                restaurants.append({
                    "id": product["id"],
                    "name": product["name"],
                    "slug": product.get("slug", ""),
                    "description": product.get("description", ""),
                    "short_description": product.get("short_description", ""),
                    "price": product.get("price", ""),
                    "regular_price": product.get("regular_price", ""),
                    "sale_price": product.get("sale_price", ""),
                    "images": [img["src"] for img in product.get("images", [])],
                    "categories": [cat["name"] for cat in product.get("categories", [])],
                    "tags": [tag["name"] for tag in product.get("tags", [])],
                    "location": product_location,
                    "available_cities": available_cities
                })
            
            return {
                "status": "success",
                "restaurants": restaurants
            }
        except Exception as e:
            logger.error(f"Error fetching restaurant services: {str(e)}")
            return {"status": "error", "message": str(e)}
            
    def get_pet_care_products(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get pet care products, optionally filtered by location"""
        try:
            params = {
                "category": CATEGORY_PET_CARE,
                "per_page": 100,
                "status": "publish"
            }
            
            if location:
                params["search"] = location
            
            success, products = self._make_request("products", params=params)
            if not success:
                return {"status": "error", "message": products}
            
            pet_products = []
            for product in products:
                # Extract location from product name or metadata
                product_location = self._extract_location_from_product(product)
                
                # If location is specified and doesn't match, skip this product
                if location and location.lower() not in product_location.lower():
                    continue
                
                # Extract available_cities from metadata if it exists
                available_cities = self._get_meta_value(product, "_available_cities")
                
                pet_products.append({
                    "id": product["id"],
                    "name": product["name"],
                    "slug": product.get("slug", ""),
                    "description": product.get("description", ""),
                    "short_description": product.get("short_description", ""),
                    "price": product.get("price", ""),
                    "regular_price": product.get("regular_price", ""),
                    "sale_price": product.get("sale_price", ""),
                    "images": [img["src"] for img in product.get("images", [])],
                    "categories": [cat["name"] for cat in product.get("categories", [])],
                    "tags": [tag["name"] for tag in product.get("tags", [])],
                    "location": product_location,
                    "available_cities": available_cities
                })
            
            return {
                "status": "success",
                "pet_products": pet_products
            }
        except Exception as e:
            logger.error(f"Error fetching pet care products: {str(e)}")
            return {"status": "error", "message": str(e)}
{{ ... }}

    def get_products(self, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get products from WooCommerce API
        
        Args:
            category: Optional category filter (can be ID or slug)
            limit: Maximum number of products to return
            
        Returns:
            List of product dictionaries
        """
        try:
            # Check if we have a valid cache that's not expired
            cached_data = self._get_cached_data()
            if cached_data and not self._is_cache_expired(cached_data) and 'products' in cached_data:
                products = cached_data['products']
                
                # Filter by category if specified
                if category and products:
                    # Check if category is a numeric ID or a slug
                    try:
                        category_id = int(category)
                        products = [p for p in products if any(cat.get('id') == category_id for cat in p.get('categories', []))]
                    except ValueError:
                        # If not a numeric ID, treat as a slug
                        products = [p for p in products if any(cat.get('slug') == category for cat in p.get('categories', []))]
                
                logger.info(f"Using cached products data ({len(products)} products)")
                return products[:limit]
            
            # Use the authenticated API
            params = {
                "per_page": limit,
                "status": "publish"
            }
            
            # Add category filter if specified
            if category:
                # Try to determine if it's a numeric ID or a slug
                try:
                    int(category)  # Will raise ValueError if not a number
                    params["category"] = category
                except ValueError:
                    # Find category ID by slug
                    success, categories = self._make_request("products/categories")
                    if success:
                        for cat in categories:
                            if cat.get("slug") == category:
                                params["category"] = cat.get("id")
                                break
                    else:
                        # If can't find category ID, use slug in search
                        params["search"] = category
                        
            success, data = self._make_request("products", params=params)
            if success and isinstance(data, list):
                # Cache the products for future use
                self._update_cache_with_products(data)
                return data[:limit]
            
            logger.warning(f"Failed to fetch products: {data}")
            return []

        except Exception as e:
            logger.error(f"Error in get_products: {str(e)}")
            return []
{{ ... }}

    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order in WooCommerce
        
        Args:
            order_data: Order data including line_items, shipping, billing info
            
        Returns:
            Created order data or error information
        """
        try:
            # Ensure the order_data has the required fields
            if 'line_items' not in order_data:
                return {
                    "status": "error", 
                    "message": "Order data must include line_items"
                }
            
            # Make the API request to create the order
            success, response = self._make_request("orders", method="POST", params=order_data)
            
            if success:
                logger.info(f"Order created successfully. Order ID: {response.get('id')}")
                return {
                    "status": "success",
                    "order": response
                }
            else:
                logger.error(f"Failed to create order: {response}")
                return {
                    "status": "error",
                    "message": response
                }
        except Exception as e:
            error_msg = f"Error creating order: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg
            }
{{ ... }}

    def get_service_locations(self) -> List[Dict[str, Any]]:
        """
        Get service locations from product attributes in WooCommerce
        
        Returns:
            List of service location dictionaries
        """
        try:
            # First, attempt to get locations from product metadata
            all_cities = set()
            
            # Get all products
            products = self.get_products(limit=200)
            
            # Extract cities from product metadata and names
            for product in products:
                # Check metadata for _available_cities
                available_cities = self._get_meta_value(product, "_available_cities")
                if available_cities and isinstance(available_cities, list):
                    all_cities.update(available_cities)
                
                # Check product name for location (e.g., "City - Location")
                name = product.get("name", "")
                if " - " in name:
                    city = name.split(" - ")[0].strip()
                    all_cities.add(city)
            
            # If we found cities, return them
            if all_cities:
                locations = sorted(list(all_cities))
                return [{"name": city, "id": city.lower().replace(" ", "-")} for city in locations]
            
            # Fallback to predefined locations
            return [{"name": location, "id": location.lower().replace(" ", "-")} for location in LOCATIONS]
            
        except Exception as e:
            logger.error(f"Error getting service locations: {str(e)}")
            return [{"name": location, "id": location.lower().replace(" ", "-")} for location in LOCATIONS]
{{ ... }}
