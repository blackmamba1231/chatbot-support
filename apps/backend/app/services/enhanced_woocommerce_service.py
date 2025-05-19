import os
import json
import logging
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from woocommerce import API

logger = logging.getLogger(__name__)

class EnhancedWooCommerceService:
    """Enhanced service for interacting with WooCommerce API"""
    
    def __init__(self):
        """Initialize the WooCommerce API service"""
        # Get credentials from environment variables
        self.api_url = os.environ.get("WP_API_URL", "https://vogo.family/wp-json/wc/v3/")
        self.consumer_key = os.environ.get("WP_CONSUMER_KEY", "ck_47075e7afebb1ad956d0350ee9ada1c93f3dbbaa")
        self.consumer_secret = os.environ.get("WP_CONSUMER_SECRET", "cs_c264cd481899b999ce5cd3cc3b97ff7cb32aab07")
        
        # Log the API configuration (without secrets)
        logger.info(f"Initializing Enhanced WooCommerce API with URL: {self.api_url}")
        logger.info(f"Consumer key is {'provided' if self.consumer_key else 'missing'}")
        logger.info(f"Consumer secret is {'provided' if self.consumer_secret else 'missing'}")
        
        # Initialize WooCommerce API client for authenticated requests
        self.wcapi = API(
            url=self.api_url.rstrip('/'),
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version="wc/v3",
            timeout=30,
            query_string_auth=True  # Use query string authentication instead of Basic Auth
        )
        
        # Store API endpoint for public access
        self.store_api_url = "https://vogo.family/wp-json/wc/store/v1"
        self.store_api_products_url = f"{self.store_api_url}/products"
        self.store_api_categories_url = f"{self.store_api_url}/products/categories"
        
        # Path to store the cached data
        self.kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "knowledge_base", "woocommerce_data.json")
        
        # Cache expiration in seconds (default: 1 hour)
        self.cache_expiration = 3600
    
    #
    # Cache Management Methods
    #
    
    def _get_cached_data(self) -> Optional[Dict[str, Any]]:
        """Get cached data if available"""
        try:
            if os.path.exists(self.kb_path):
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading cached data: {str(e)}")
            return None
    
    def _is_cache_expired(self, cached_data: Dict[str, Any]) -> bool:
        """Check if the cached data is expired"""
        if not cached_data or 'timestamp' not in cached_data:
            return True
        
        timestamp = cached_data['timestamp']
        expiration_time = datetime.fromisoformat(timestamp) + timedelta(seconds=self.cache_expiration)
        
        return datetime.now() > expiration_time
    
    def _cache_data(self, data: Dict[str, Any]) -> None:
        """Cache data for future use"""
        try:
            # Add timestamp for cache expiration
            data['timestamp'] = datetime.now().isoformat()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.kb_path), exist_ok=True)
            
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Cached WooCommerce data to {self.kb_path}")
        except Exception as e:
            logger.error(f"Error caching data: {str(e)}")
    
    #
    # Product Methods
    #
    
    def get_products(self, category: Optional[str] = None, limit: int = 100, per_page: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get products from WooCommerce API
        
        Args:
            category: Optional category filter
            limit: Maximum number of products to return
            per_page: Number of products per page (defaults to limit if not specified)
            
        Returns:
            List of product dictionaries
        """
        try:
            # If per_page is not specified, use limit
            if per_page is None:
                per_page = limit
                
            # Check if we have a valid cache that's not expired
            cached_data = self._get_cached_data()
            if cached_data and not self._is_cache_expired(cached_data) and 'products' in cached_data:
                products = cached_data['products']
                
                # Filter by category if specified
                if category and products:
                    products = [p for p in products if any(cat.get('slug') == category for cat in p.get('categories', []))]
                
                logger.info(f"Using cached products data ({len(products)} products)")
                return products[:limit]
            
            # Try both API methods - first the authenticated API, then fall back to Store API if needed
            products = []
            
            # Method 1: Try using the authenticated WooCommerce API
            try:
                logger.info(f"Attempting to fetch products using authenticated WooCommerce API")
                params = {"per_page": per_page}
                if category:
                    params["category"] = category
                
                response = self.wcapi.get("products", params=params)
                
                if response.status_code == 200:
                    products = response.json()
                    logger.info(f"Successfully fetched {len(products)} products using authenticated API")
                else:
                    logger.warning(f"Authenticated API request failed: {response.status_code}")
            except Exception as auth_error:
                logger.warning(f"Error using authenticated API: {str(auth_error)}")
            
            # Method 2: If authenticated API didn't work, try the public Store API
            if not products:
                logger.info(f"Falling back to public Store API")
                store_api_url = f"{self.store_api_url}/products"
                
                params = {"per_page": per_page}
                if category:
                    params['category'] = category
                
                try:
                    logger.info(f"Making WooCommerce Store API request to: {store_api_url}")
                    response = requests.get(store_api_url, params=params)
                    
                    if response.status_code == 200:
                        products = response.json()
                        logger.info(f"Fetched {len(products)} products from WooCommerce Store API")
                    else:
                        logger.error(f"Store API request failed: {response.status_code} - {response.text[:200]}")
                except Exception as store_error:
                    logger.error(f"Error fetching from Store API: {str(store_error)}")
            
            # If we got products, fetch categories and cache the data
            if products:
                # Get categories
                categories = self.get_product_categories()
                
                # Cache the data
                self._cache_data({"products": products, "categories": categories})
                
                return products
            
            # If we still don't have products, check if we have any cached data to fall back to
            if not products:
                cached_data = self._get_cached_data()
                if cached_data and 'products' in cached_data:
                    products = cached_data['products']
                    logger.info(f"Using fallback cached data ({len(products)} products)")
                    return products[:limit]
            
            return products
        except Exception as e:
            logger.error(f"Error in get_products: {str(e)}")
            # Fall back to cache if available
            cached_data = self._get_cached_data()
            if cached_data and 'products' in cached_data:
                products = cached_data['products']
                logger.info(f"Using emergency cached data ({len(products)} products)")
                return products[:limit]
            return []
            
            # If we still don't have products, check if we have any cached data to fall back to
            if not products:
                cached_data = self._get_cached_data()
                if cached_data and 'products' in cached_data:
                    products = cached_data['products']
                    logger.info(f"Using fallback cached data ({len(products)} products)")
                    return products[:limit]
            
            return products
            
        except Exception as e:
            logger.error(f"Error in get_products: {str(e)}")
            # Fall back to cache if available
            cached_data = self._get_cached_data()
            if cached_data and 'products' in cached_data:
                products = cached_data['products']
                logger.info(f"Using emergency cached data ({len(products)} products)")
                return products[:limit]
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific product by ID
        
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
            # Try authenticated API first
            try:
                response = self.wcapi.get(f"products/{product_id}")
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Authenticated API request failed: {response.status_code}")
            except Exception as auth_error:
                logger.warning(f"Error using authenticated API: {str(auth_error)}")
            
            # Fall back to Store API
            try:
                store_api_url = f"{self.store_api_url}/products/{product_id}"
                response = requests.get(store_api_url)
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.error(f"Failed to fetch product {product_id}: {response.status_code} - {response.text[:200]}")
            except Exception as store_error:
                logger.error(f"Error fetching from Store API: {str(store_error)}")
            
            return None
        except Exception as e:
            logger.error(f"Error fetching product {product_id}: {str(e)}")
            return None
    
    def search_products(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Enhanced search for products across all fields: name, description, slug, and category slugs
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of products to return
            
        Returns:
            List of matching products with added match information
        """
        try:
            # Try authenticated API first
            try:
                params = {
                    "search": query,
                    "per_page": limit
                }
                
                if category:
                    params["category"] = category
                
                response = self.wcapi.get("products", params=params)
                
                if response.status_code == 200:
                    try:
                        products = response.json()
                        # Enhance results with match information
                        return self._enhance_search_results(products, query)
                    except json.JSONDecodeError as json_err:
                        logger.error(f"JSON decode error in authenticated API: {str(json_err)}")
                        # Try to sanitize the response
                        try:
                            text = response.text
                            # Find the valid JSON part - often the problem is extra data after valid JSON
                            if text.strip().startswith('[') or text.strip().startswith('{'):
                                # Try to parse manually by finding the closing bracket
                                valid_json = self._extract_valid_json(text)
                                if valid_json:
                                    products = json.loads(valid_json)
                                    return self._enhance_search_results(products, query)
                        except Exception as e:
                            logger.error(f"Failed to sanitize JSON response: {str(e)}")
                else:
                    logger.warning(f"Authenticated API search failed: {response.status_code}")
                    if response.status_code == 401:
                        logger.warning("Authentication failed, check your API credentials")
            except Exception as auth_error:
                logger.warning(f"Error using authenticated API for search: {str(auth_error)}")
            
            # Fall back to Store API
            try:
                store_api_url = f"{self.store_api_url}/products"
                params = {
                    "search": query,
                    "per_page": limit
                }
                
                if category:
                    params["category"] = category
                
                response = requests.get(store_api_url, params=params)
                
                if response.status_code == 200:
                    try:
                        products = response.json()
                        # Enhance results with match information
                        return self._enhance_search_results(products, query)
                    except json.JSONDecodeError as json_err:
                        logger.error(f"JSON decode error in Store API: {str(json_err)}")
                        # Try to sanitize the response
                        try:
                            text = response.text
                            # Find the valid JSON part
                            if text.strip().startswith('[') or text.strip().startswith('{'):
                                # Try to parse manually
                                valid_json = self._extract_valid_json(text)
                                if valid_json:
                                    products = json.loads(valid_json)
                                    return self._enhance_search_results(products, query)
                        except Exception as e:
                            logger.error(f"Failed to sanitize JSON response from Store API: {str(e)}")
                else:
                    logger.error(f"Store API search failed: {response.status_code} - {response.text[:200]}")
            except Exception as store_error:
                logger.error(f"Error searching with Store API: {str(store_error)}")
            
            # If API search fails, do comprehensive search in cached data
            return self._search_cached_products(query, category, limit)
                
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return []
            
    def _search_cached_products(self, query: str, category: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Comprehensive search through cached products looking in all relevant fields
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of products to return
            
        Returns:
            List of products with match information
        """
        cached_data = self._get_cached_data()
        if not cached_data or "products" not in cached_data:
            return []
            
        products = cached_data["products"]
        query_lower = query.lower()
        
        # Search results with information about match locations
        results = []
        
        for product in products:
            # Initialize match information
            match_info = {
                "name_match": False,
                "slug_match": False,
                "description_match": False,
                "short_description_match": False,
                "category_match": False,
                "category_slug_match": False
            }
            
            # Check product name
            name = product.get("name", "").lower()
            if query_lower in name:
                match_info["name_match"] = True
            
            # Check product slug
            slug = product.get("slug", "").lower()
            if query_lower in slug:
                match_info["slug_match"] = True
            
            # Check product descriptions
            description = product.get("description", "").lower()
            if query_lower in description:
                match_info["description_match"] = True
                
            short_description = product.get("short_description", "").lower()
            if query_lower in short_description:
                match_info["short_description_match"] = True
            
            # Check category name and slug matches
            categories = product.get("categories", [])
            for cat in categories:
                cat_name = cat.get("name", "").lower()
                cat_slug = cat.get("slug", "").lower()
                
                if query_lower in cat_name:
                    match_info["category_match"] = True
                    
                if query_lower in cat_slug:
                    match_info["category_slug_match"] = True
            
            # If any match or category filter passes, add to results
            is_match = any(match_info.values())
            passes_category_filter = True
            
            if category and categories:
                passes_category_filter = any(cat.get("slug") == category for cat in categories)
            
            if is_match and passes_category_filter:
                # Add match info to product
                product_copy = product.copy()
                product_copy["match_info"] = match_info
                results.append(product_copy)
        
        # Sort results - prioritize name/slug matches first
        results.sort(key=lambda p: (
            not (p["match_info"]["name_match"] or p["match_info"]["slug_match"]),
            not p["match_info"]["category_slug_match"],
            not p["match_info"]["category_match"],
            not p["match_info"]["description_match"]
        ))
        
        return results[:limit]
        
    def _enhance_search_results(self, products: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """
        Enhances search results by adding match information
        
        Args:
            products: List of products from API
            query: Original search query
            
        Returns:
            Enhanced products with match information
        """
        query_lower = query.lower()
        enhanced_products = []
        
        for product in products:
            # Initialize match information
            match_info = {
                "name_match": False,
                "slug_match": False,
                "description_match": False,
                "short_description_match": False,
                "category_match": False,
                "category_slug_match": False
            }
            
            # Check product name
            name = product.get("name", "").lower()
            if query_lower in name:
                match_info["name_match"] = True
            
            # Check product slug
            slug = product.get("slug", "").lower()
            if query_lower in slug:
                match_info["slug_match"] = True
            
            # Check product descriptions
            description = product.get("description", "").lower()
            if query_lower in description:
                match_info["description_match"] = True
                
            short_description = product.get("short_description", "").lower()
            if query_lower in short_description:
                match_info["short_description_match"] = True
            
            # Check category name and slug matches
            categories = product.get("categories", [])
            for cat in categories:
                cat_name = cat.get("name", "").lower()
                cat_slug = cat.get("slug", "").lower()
                
                if query_lower in cat_name:
                    match_info["category_match"] = True
                    
                if query_lower in cat_slug:
                    match_info["category_slug_match"] = True
            
            # Add match info to product
            product_copy = product.copy()
            product_copy["match_info"] = match_info
            enhanced_products.append(product_copy)
        
        # Sort results - prioritize name/slug matches first
        enhanced_products.sort(key=lambda p: (
            not (p["match_info"]["name_match"] or p["match_info"]["slug_match"]),
            not p["match_info"]["category_slug_match"],
            not p["match_info"]["category_match"],
            not p["match_info"]["description_match"]
        ))
        
        return enhanced_products
    
    def get_product_categories(self) -> List[Dict[str, Any]]:
        """
        Get product categories from WooCommerce API
        
        Returns:
            List of category dictionaries
        """
        try:
            # Check if we have cached data and it's not expired
            cached_data = self._get_cached_data()
            if cached_data and not self._is_cache_expired(cached_data) and "categories" in cached_data:
                return cached_data["categories"]
            
            # Try authenticated API first
            try:
                response = self.wcapi.get("products/categories", params={"per_page": 100})
                
                if response.status_code == 200:
                    categories = response.json()
                    logger.info(f"Fetched {len(categories)} categories using authenticated API")
                    
                    # Cache the data
                    if cached_data:
                        cached_data["categories"] = categories
                        self._cache_data(cached_data)
                    else:
                        self._cache_data({"categories": categories})
                    
                    return categories
                else:
                    logger.warning(f"Authenticated API request failed: {response.status_code}")
            except Exception as auth_error:
                logger.warning(f"Error using authenticated API: {str(auth_error)}")
            
            # Fall back to Store API
            try:
                store_api_url = f"{self.store_api_url}/products/categories"
                response = requests.get(store_api_url, params={"per_page": 100})
                
                if response.status_code == 200:
                    categories = response.json()
                    logger.info(f"Fetched {len(categories)} categories from Store API")
                    
                    # Cache the data
                    if cached_data:
                        cached_data["categories"] = categories
                        self._cache_data(cached_data)
                    else:
                        self._cache_data({"categories": categories})
                    
                    return categories
                else:
                    logger.error(f"Store API request failed: {response.status_code} - {response.text[:200]}")
            except Exception as store_error:
                logger.error(f"Error fetching from Store API: {str(store_error)}")
            
            # Fall back to cache if available
            if cached_data and "categories" in cached_data:
                return cached_data["categories"]
            
            return []
        except Exception as e:
            logger.error(f"Error fetching product categories: {str(e)}")
            return []
    
        try:
            response = self.wcapi.get("products/categories", params={"per_page": 100})

            if response.status_code == 200:
                categories = response.json()
                logger.info(f"Fetched {len(categories)} categories using authenticated API")

                # Cache the data
                if cached_data:
                    cached_data["categories"] = categories
                    self._cache_data(cached_data)
                else:
                    self._cache_data({"categories": categories})

                return categories
            else:
                logger.warning(f"Authenticated API request failed: {response.status_code}")
        except Exception as auth_error:
            logger.warning(f"Error using authenticated API: {str(auth_error)}")

        # Fall back to Store API
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer in WooCommerce
        
        Args:
            customer_data: Customer data including email, name, etc.
            
        Returns:
            Created customer data or error information
        """
        try:
            response = self.wcapi.post("customers", customer_data)
            
            if response.status_code in [200, 201]:
                customer = response.json()
                logger.info(f"Successfully created customer #{customer.get('id')}")
                return {
                    "status": "success",
                    "customer": customer
                }
            else:
                logger.error(f"Failed to create customer: {response.status_code} - {response.text[:200]}")
                return {
                    "status": "error",
                    "message": f"Failed to create customer: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating customer: {str(e)}"
            }
    
    def get_restaurants(self, location: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """
        Get restaurants, optionally filtered by location
        
        Args:
            location: Optional location filter
            limit: Maximum number of restaurants to return
            
        Returns:
            Dictionary with status and list of restaurants
        """
        try:
            # Get products from the Mall Delivery category (ID 223)
            params = {
                "category": "223",  # Mall Delivery category ID
                "per_page": limit
            }
            
            products = self.get_products(**params)
            
            # Filter and format restaurant products
            restaurants = []
            for product in products:
                # Skip products that don't match location filter
                product_name = product.get("name", "")
                if location and location.lower() not in product_name.lower():
                    continue
                    
                restaurants.append({
                    "id": str(product.get("id", "")),
                    "name": product.get("name", ""),
                    "price": str(product.get("price", "0.00")),
                    "image": product.get("images", [{}])[0].get("src", "") if product.get("images") else "",
                    "description": product.get("short_description", "") or product.get("description", ""),
                    "location": location or "All locations"
                })
            
            logger.info(f"Found {len(restaurants)} restaurant products for location: {location or 'all'}")
            
            return {
                "status": "success",
                "restaurants": restaurants
            }
        except Exception as e:
            logger.error(f"Error getting restaurants: {str(e)}")
            return {
                "status": "error",
                "message": str(e),
                "restaurants": []
            }
    
    def get_customer(self, customer_id: int) -> Optional[Dict[str, Any]]:
        """
        Get customer details by ID
        
        Args:
            customer_id: WooCommerce customer ID
            
        Returns:
            Customer data or None if not found
        """
        try:
            response = self.wcapi.get(f"customers/{customer_id}")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch customer {customer_id}: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"Error fetching customer {customer_id}: {str(e)}")
            return None
    
    def get_customer_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Get customer details by email
        
        Args:
            email: Customer email address
            
        Returns:
            Customer data or None if not found
        """
        try:
            response = self.wcapi.get("customers", params={"email": email})
            
            if response.status_code == 200:
                customers = response.json()
                if customers:
                    return customers[0]  # Return the first matching customer
                return None
            else:
                logger.error(f"Failed to fetch customer by email {email}: {response.status_code} - {response.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"Error fetching customer by email {email}: {str(e)}")
            return None
    
    def update_customer(self, customer_id: int, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update customer details
        
        Args:
            customer_id: WooCommerce customer ID
            customer_data: Updated customer data
            
        Returns:
            Updated customer data or error information
        """
        try:
            response = self.wcapi.put(f"customers/{customer_id}", customer_data)
            
            if response.status_code == 200:
                customer = response.json()
                logger.info(f"Successfully updated customer #{customer.get('id')}")
                return {
                    "status": "success",
                    "customer": customer
                }
            else:
                logger.error(f"Failed to update customer: {response.status_code} - {response.text[:200]}")
                return {
                    "status": "error",
                    "message": f"Failed to update customer: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating customer: {str(e)}"
            }
    
    #
    # Order Methods
    #
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order in WooCommerce
        
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
                logger.error(f"Failed to create order: {response.status_code} - {response.text[:200]}")
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
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """
        Get order details by ID
        
        Args:
            order_id: WooCommerce order ID
            
        Returns:
            Order details or error information
        """
        try:
            response = self.wcapi.get(f"orders/{order_id}")
            
            if response.status_code == 200:
                order = response.json()
                return {
                    "status": "success",
                    "order": order
                }
            else:
                logger.error(f"Failed to fetch order {order_id}: {response.status_code} - {response.text[:200]}")
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
    
    def get_customer_orders(self, customer_id: int) -> Dict[str, Any]:
        """
        Get orders for a specific customer
        
        Args:
            customer_id: WooCommerce customer ID
            
        Returns:
            List of customer orders or error information
        """
        try:
            response = self.wcapi.get("orders", params={"customer": customer_id})
            
            if response.status_code == 200:
                orders = response.json()
                return {
                    "status": "success",
                    "orders": orders
                }
            else:
                logger.error(f"Failed to fetch orders for customer {customer_id}: {response.status_code} - {response.text[:200]}")
                return {
                    "status": "error",
                    "message": f"Failed to fetch orders: {response.status_code}"
                }
        except Exception as e:
            logger.error(f"Error fetching orders for customer {customer_id}: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching orders: {str(e)}"
            }
    
    def update_order(self, order_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing order
        
        Args:
            order_id: WooCommerce order ID
            order_data: Updated order data
            
        Returns:
            Updated order data or error information
        """
        try:
            response = self.wcapi.put(f"orders/{order_id}", order_data)
            
            if response.status_code == 200:
                order = response.json()
                logger.info(f"Successfully updated order #{order.get('id')}")
                return {
                    "status": "success",
                    "order": order
                }
            else:
                logger.error(f"Failed to update order: {response.status_code} - {response.text[:200]}")
                return {
                    "status": "error",
                    "message": f"Failed to update order: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            logger.error(f"Error updating order: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating order: {str(e)}"
            }
    
    #
    # Coupon Methods
    #
    
    def get_coupons(self) -> List[Dict[str, Any]]:
        """
        Get available coupons
        
        Returns:
            List of coupon dictionaries
        """
        try:
            response = self.wcapi.get("coupons", params={"per_page": 50})
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch coupons: {response.status_code} - {response.text[:200]}")
                return []
        except Exception as e:
            logger.error(f"Error fetching coupons: {str(e)}")
            return []
    
    def validate_coupon(self, code: str) -> Dict[str, Any]:
        """
        Validate a coupon code
        
        Args:
            code: Coupon code to validate
            
        Returns:
            Validation result
        """
        try:
            response = self.wcapi.get("coupons", params={"code": code})
            
            if response.status_code == 200:
                coupons = response.json()
                if coupons:
                    coupon = coupons[0]
                    # Check if coupon is valid (not expired, etc.)
                    if coupon.get("date_expires") and datetime.now() > datetime.fromisoformat(coupon["date_expires"]):
                        return {
                            "status": "error",
                            "message": "Coupon has expired"
                        }
                    
                    return {
                        "status": "success",
                        "coupon": coupon
                    }
                else:
                    return {
                        "status": "error",
                        "message": "Invalid coupon code"
                    }
            else:
                logger.error(f"Failed to validate coupon: {response.status_code} - {response.text[:200]}")
                return {
                    "status": "error",
                    "message": "Error validating coupon"
                }
        except Exception as e:
            logger.error(f"Error validating coupon: {str(e)}")
            return {
                "status": "error",
                "message": f"Error validating coupon: {str(e)}"
            }
    
    #
    # Shipping Methods
    #
    
    def get_shipping_methods(self) -> List[Dict[str, Any]]:
        """
        Get available shipping methods
        
        Returns:
            List of shipping method dictionaries
        """
        try:
            response = self.wcapi.get("shipping_methods")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch shipping methods: {response.status_code} - {response.text[:200]}")
                return []
        except Exception as e:
            logger.error(f"Error fetching shipping methods: {str(e)}")
            return []
    
    def get_shipping_zones(self) -> List[Dict[str, Any]]:
        """
        Get shipping zones
        
        Returns:
            List of shipping zone dictionaries
        """
        try:
            response = self.wcapi.get("shipping/zones")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch shipping zones: {response.status_code} - {response.text[:200]}")
                return []
        except Exception as e:
            logger.error(f"Error fetching shipping zones: {str(e)}")
            return []
    
    #
    # Payment Methods
    #
    
    def get_payment_gateways(self) -> List[Dict[str, Any]]:
        """
        Get available payment gateways
        
        Returns:
            List of payment gateway dictionaries
        """
        try:
            response = self.wcapi.get("payment_gateways")
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch payment gateways: {response.status_code} - {response.text[:200]}")
                return []
        except Exception as e:
            logger.error(f"Error fetching payment gateways: {str(e)}")
            return []
