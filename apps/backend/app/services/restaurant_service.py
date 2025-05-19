import os
import json
import logging
import random
import requests
from typing import Dict, Any, List, Optional
from app.services.woocommerce_service import WooCommerceService

logger = logging.getLogger(__name__)

class RestaurantService:
    """Service for restaurant search and food ordering"""
    
    def __init__(self):
        """Initialize the restaurant service"""
        # Initialize WooCommerce service for fetching restaurant data
        self.woocommerce_service = WooCommerceService()
        
        # For caching and fallback, we'll use a local file
        self.data_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "knowledge_base"
        )
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.restaurants_file = os.path.join(self.data_dir, "restaurants.json")
        
        # Create restaurants file with sample data if it doesn't exist (for fallback)
        if not os.path.exists(self.restaurants_file):
            self._create_fallback_restaurants()
    
    def _create_fallback_restaurants(self):
        """Create fallback restaurant data in case WooCommerce API is unavailable"""
        mock_restaurants = {
            "restaurants": [
                {
                    "id": "1",
                    "name": "La Mama",
                    "cuisine": "traditional",
                    "rating": 4.7,
                    "address": "Strada Episcopiei 9, București",
                    "phone": "+40 21 314 1234",
                    "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "2",
                    "name": "Trattoria Buongiorno",
                    "cuisine": "italian",
                    "rating": 4.5,
                    "address": "Bulevardul Lascăr Catargiu 56, București",
                    "phone": "+40 21 317 4567",
                    "image": "https://images.unsplash.com/photo-1498579150354-977475b7ea0b?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "3",
                    "name": "Beijing Garden",
                    "cuisine": "chinese",
                    "rating": 4.3,
                    "address": "Strada Academiei 4, București",
                    "phone": "+40 21 315 7890",
                    "image": "https://images.unsplash.com/photo-1525755662778-989d0524087e?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "4",
                    "name": "Taj Mahal",
                    "cuisine": "indian",
                    "rating": 4.6,
                    "address": "Calea Victoriei 100, București",
                    "phone": "+40 21 312 3456",
                    "image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "5",
                    "name": "McDonald's",
                    "cuisine": "fastfood",
                    "rating": 4.0,
                    "address": "Piața Universității, București",
                    "phone": "+40 21 310 2345",
                    "image": "https://images.unsplash.com/photo-1561758033-7e924f619b47?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "6",
                    "name": "Caru' cu Bere",
                    "cuisine": "traditional",
                    "rating": 4.8,
                    "address": "Strada Stavropoleos 5, București",
                    "phone": "+40 21 313 7560",
                    "image": "https://images.unsplash.com/photo-1544148103-0773bf10d330?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "7",
                    "name": "Pizza Hut",
                    "cuisine": "italian",
                    "rating": 4.2,
                    "address": "Bulevardul Nicolae Bălcescu 2, București",
                    "phone": "+40 21 315 2468",
                    "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "9",
                    "name": "Domino's Pizza",
                    "cuisine": "italian",
                    "rating": 4.1,
                    "address": "Strada Academiei 28-30, București",
                    "phone": "+40 21 314 9876",
                    "image": "https://images.unsplash.com/photo-1594007654729-407eedc4be65?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "10",
                    "name": "Pizza Roma",
                    "cuisine": "italian",
                    "rating": 4.6,
                    "address": "Strada Lipscani 43, București",
                    "phone": "+40 21 313 5791",
                    "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                },
                {
                    "id": "8",
                    "name": "Chopstix",
                    "cuisine": "chinese",
                    "rating": 4.4,
                    "address": "Strada Lipscani 10, București",
                    "phone": "+40 21 314 1357",
                    "image": "https://images.unsplash.com/photo-1526318896980-cf78c088247c?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60"
                }
            ]
        }
        
        with open(self.restaurants_file, 'w') as f:
            json.dump(mock_restaurants, f, indent=2)
    
    def get_restaurants(self, cuisine: Optional[str] = None, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
        """
        Get restaurants, optionally filtered by cuisine and sorted by distance
        
        Args:
            cuisine: Optional cuisine type filter
            latitude: Optional user latitude for distance calculation
            longitude: Optional user longitude for distance calculation
            
        Returns:
            Dictionary with restaurants list
        """
        try:
            # First try to get real data from WooCommerce API
            logger.info("Attempting to fetch restaurant data from WooCommerce API")
            woo_restaurants = self._get_restaurants_from_woocommerce(cuisine, latitude, longitude)
            
            if woo_restaurants and len(woo_restaurants) > 0:
                logger.info(f"Successfully fetched {len(woo_restaurants)} restaurants from WooCommerce API")
                return {"restaurants": woo_restaurants}
            
            # If WooCommerce API fails or returns no data, fall back to mock data
            logger.warning("Falling back to mock restaurant data")
            with open(self.restaurants_file, 'r') as f:
                data = json.load(f)
                restaurants = data["restaurants"]
                
            # Filter by cuisine if specified
            if cuisine:
                restaurants = [r for r in restaurants if r["cuisine"].lower() == cuisine.lower()]
                
            # Calculate distances if location provided
            if latitude is not None and longitude is not None:
                for restaurant in restaurants:
                    # Mock distance calculation for now
                    restaurant["distance"] = f"{random.uniform(0.5, 5.0):.1f} km"
                    
            return {"restaurants": restaurants}
            
            # Add category filter if specified
            if cuisine:
                # Get the category ID from the cuisine name
                cat_response = requests.get("https://vogo.family/wp-json/wc/store/v1/products/categories")
                if cat_response.status_code == 200:
                    categories = cat_response.json()
                    for category in categories:
                        if cuisine.lower() in category.get('name', '').lower():
                            params['category'] = category.get('id')
                            break
            
            # Make the API request
            try:
                logger.info(f"Making direct Store API request to: {store_api_url}")
                response = requests.get(store_api_url, params=params)
                
                if response.status_code == 200:
                    products = response.json()
                    logger.info(f"Fetched {len(products)} products directly from Store API")
                    
                    # Transform products into restaurant format
                    restaurants = []
                    for product in products:
                        # Check if this is a food/restaurant product
                        restaurant = {
                            'id': str(product.get('id')),
                            'name': product.get('name', ''),
                            'cuisine': self._extract_cuisine_from_store_api(product),
                            'rating': float(product.get('average_rating', 4.5)),
                            'address': self._extract_address_from_store_api(product),
                            'phone': '+40 21 123 4567',  # Default phone number
                            'image': product.get('images', [{}])[0].get('src', '') if product.get('images') else ''
                        }
                        restaurants.append(restaurant)
                else:
                    logger.error(f"Direct Store API request failed: {response.status_code}")
                    # Fall back to WooCommerce service
                    return self._get_restaurants_from_woocommerce(cuisine, latitude, longitude)
            except Exception as api_error:
                logger.error(f"Error fetching from direct Store API: {str(api_error)}")
                # Fall back to WooCommerce service
                return self._get_restaurants_from_woocommerce(cuisine, latitude, longitude)
        except Exception as e:
            logger.error(f"Error in direct API approach: {str(e)}")
            # Fall back to WooCommerce service
            return self._get_restaurants_from_woocommerce(cuisine, latitude, longitude)
        
        # If we got here, we have restaurants from the direct API call
        # Add distance if location is provided
        if latitude is not None and longitude is not None:
            for restaurant in restaurants:
                # In a real app, we would calculate actual distance based on coordinates
                # For now, we'll just add a random distance
                distance_km = round(random.uniform(0.5, 10.0), 1)
                restaurant["distance"] = f"{distance_km} km"
            
            # Sort by distance
            restaurants.sort(key=lambda r: float(r.get("distance", "0").split()[0]))
        
        # Cache the results for fallback
        self._cache_restaurants(restaurants)
        
        return {"restaurants": restaurants}
    
    def _extract_cuisine_from_store_api(self, product: Dict[str, Any]) -> str:
        """Extract cuisine from Store API product data"""
        # For mall delivery products, we'll categorize them by location
        # Extract location from the product name
        name = product.get('name', '').lower()
        
        # Map of Romanian cities to cuisine types
        city_cuisine_map = {
            'alba iulia': 'traditional',
            'arad': 'traditional',
            'miercurea ciuc': 'traditional',
            'vaslui': 'traditional',
            'târgu mureș': 'traditional',
            'targu mures': 'traditional',
            'suceava': 'traditional',
            'satu mare': 'traditional',
            'oradea': 'traditional',
            'cluj': 'traditional',
            'bucharest': 'international',
            'bucuresti': 'international',
            'bucurești': 'international'
        }
        
        # Check if any city name is in the product name
        for city, cuisine in city_cuisine_map.items():
            if city in name:
                return cuisine
        
        # Also check categories
        categories = product.get('categories', [])
        for category in categories:
            category_name = category.get('name', '').lower()
            if 'mall delivery' in category_name:
                return 'mall delivery'
            elif 'food' in category_name:
                return 'food delivery'
        
        # Default to mall delivery if no match found
        return 'mall delivery'
    
    def _extract_address_from_store_api(self, product: Dict[str, Any]) -> str:
        """Extract address from Store API product data"""
        # Extract location from the product name
        name = product.get('name', '')
        
        # Map of common mall names to addresses
        mall_address_map = {
            'Carolina Mall': 'Strada Ștefan cel Mare 22, Alba Iulia, Romania',
            'Atrium Mall': 'Calea Aurel Vlaicu 10-12, Arad, Romania',
            'Nest Park Retail': 'Strada Lunca Mare 5, Miercurea Ciuc, Romania',
            'Proxima Shopping Center': 'Strada Ștefan cel Mare 79, Vaslui, Romania',
            'PlazaM': 'Strada Gheorghe Doja 243, Târgu Mureș, Romania',
            'Mureș Mall': 'Bulevardul 1 Decembrie 1918 291, Târgu Mureș, Romania',
            'Shopping City': 'Calea Unirii 22, Suceava, Romania'
        }
        
        # Check if any mall name is in the product name
        for mall, address in mall_address_map.items():
            if mall in name:
                return address
        
        # Try to extract city from the name
        city_list = ['Alba Iulia', 'Arad', 'Miercurea Ciuc', 'Vaslui', 'Târgu Mureș', 'Suceava', 'Satu Mare', 'Oradea', 'Cluj-Napoca', 'București']
        
        for city in city_list:
            if city in name or city.lower() in name.lower():
                return f'{city}, Romania'
        
        # Try to get from description
        description = product.get('description', '')
        for city in city_list:
            if city in description or city.lower() in description.lower():
                return f'{city}, Romania'
        
        # Default address
        return 'Romania'
    
    def _get_restaurants_from_woocommerce(self, cuisine: Optional[str] = None, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Dict[str, Any]:
        """Get restaurants using the WooCommerce service as fallback"""
        try:
            # Get restaurant category ID for filtering
            category_id = None
            if cuisine:
                categories = self.woocommerce_service.get_product_categories()
                for category in categories:
                    if cuisine.lower() in category.get('name', '').lower():
                        category_id = category.get('id')
                        break
            
            # Fetch products from WooCommerce
            products = self.woocommerce_service.get_products(category=category_id)
            
            # Transform products into restaurant format
            restaurants = []
            for product in products:
                # Check if this is a restaurant/food product
                restaurant = {
                    'id': str(product.get('id')),
                    'name': product.get('name', ''),
                    'cuisine': self._extract_cuisine(product),
                    'rating': self._extract_rating(product),
                    'address': self._extract_address(product),
                    'phone': self._extract_phone(product),
                    'image': self._extract_image(product)
                }
                restaurants.append(restaurant)
            
            # Add distance if location is provided
            if latitude is not None and longitude is not None:
                for restaurant in restaurants:
                    # In a real app, we would calculate actual distance based on coordinates
                    # For now, we'll just add a random distance
                    distance_km = round(random.uniform(0.5, 10.0), 1)
                    restaurant["distance"] = f"{distance_km} km"
                
                # Sort by distance
                restaurants.sort(key=lambda r: float(r.get("distance", "0").split()[0]))
            
            # Cache the results for fallback
            self._cache_restaurants(restaurants)
            
            return {"restaurants": restaurants}
        
        except Exception as e:
            logger.error(f"Error getting restaurants from WooCommerce: {str(e)}")
            # Fall back to cached data
            try:
                with open(self.restaurants_file, 'r') as f:
                    data = json.load(f)
                
                restaurants = data.get("restaurants", [])
                
                # Filter by cuisine if specified
                if cuisine:
                    restaurants = [r for r in restaurants if r.get("cuisine") == cuisine]
                
                # Add distance if location is provided
                if latitude is not None and longitude is not None:
                    for restaurant in restaurants:
                        distance_km = round(random.uniform(0.5, 10.0), 1)
                        restaurant["distance"] = f"{distance_km} km"
                    
                    # Sort by distance
                    restaurants.sort(key=lambda r: float(r.get("distance", "0").split()[0]))
                
                return {"restaurants": restaurants}
            except Exception as fallback_error:
                logger.error(f"Error getting fallback restaurants: {str(fallback_error)}")
                return {"restaurants": [], "error": str(e)}
    
    def _extract_cuisine(self, product: Dict[str, Any]) -> str:
        """
        Extract cuisine type from product data
        
        Args:
            product: WooCommerce product data
            
        Returns:
            Cuisine type as string
        """
        # Try to get cuisine from categories
        categories = product.get('categories', [])
        cuisine_map = {
            'italian': ['italian', 'pizza', 'pasta', 'meniu italian'],
            'grecesc': ['grecesc', 'greek', 'meniu grecesc'],
            'spaniol': ['spaniol', 'spanish', 'meniu spaniol'],
            'vegan': ['vegan', 'vegetarian', 'meniu vegan'],
            'arabesc': ['arabesc', 'arabic', 'meniu arabesc'],
            'asia': ['asia', 'asian', 'chinese', 'meniu asia'],
            'traditional': ['traditional', 'romanian', 'meniu traditional'],
            'sport': ['sport', 'meniu sport'],
            'pizza': ['pizza']
        }
        
        for category in categories:
            category_name = category.get('name', '').lower()
            for cuisine, keywords in cuisine_map.items():
                if any(keyword in category_name for keyword in keywords):
                    return cuisine
        
        # Try to get cuisine from attributes
        attributes = product.get('attributes', [])
        for attribute in attributes:
            if attribute.get('name', '').lower() in ['cuisine', 'type']:
                return attribute.get('options', ['traditional'])[0].lower()
        
        # Default to traditional if no cuisine found
        return 'traditional'
    
    def _extract_rating(self, product: Dict[str, Any]) -> float:
        """
        Extract rating from product data
        
        Args:
            product: WooCommerce product data
            
        Returns:
            Rating as float
        """
        # Try to get rating from product
        rating = product.get('average_rating', None)
        if rating is not None:
            try:
                return float(rating)
            except (ValueError, TypeError):
                pass
        
        # Generate a random rating between 3.5 and 5.0 if not available
        return round(random.uniform(3.5, 5.0), 1)
    
    def _extract_address(self, product: Dict[str, Any]) -> str:
        """
        Extract address from product data
        
        Args:
            product: WooCommerce product data
            
        Returns:
            Address as string
        """
        # Try to get address from attributes
        attributes = product.get('attributes', [])
        for attribute in attributes:
            if attribute.get('name', '').lower() in ['address', 'location']:
                return attribute.get('options', [''])[0]
        
        # Try to get from meta data
        meta_data = product.get('meta_data', [])
        for meta in meta_data:
            if meta.get('key', '').lower() in ['address', 'location']:
                return meta.get('value', '')
        
        # Default to empty string if no address found
        return 'Bucharest, Romania'
    
    def _extract_phone(self, product: Dict[str, Any]) -> str:
        """
        Extract phone from product data
        
        Args:
            product: WooCommerce product data
            
        Returns:
            Phone as string
        """
        # Try to get phone from attributes
        attributes = product.get('attributes', [])
        for attribute in attributes:
            if attribute.get('name', '').lower() in ['phone', 'contact']:
                return attribute.get('options', [''])[0]
        
        # Try to get from meta data
        meta_data = product.get('meta_data', [])
        for meta in meta_data:
            if meta.get('key', '').lower() in ['phone', 'contact']:
                return meta.get('value', '')
        
        # Default to empty string if no phone found
        return '+40 21 123 4567'
    
    def _extract_image(self, product: Dict[str, Any]) -> str:
        """
        Extract image URL from product data
        
        Args:
            product: WooCommerce product data
            
        Returns:
            Image URL as string
        """
        # Try to get image from product
        images = product.get('images', [])
        if images and len(images) > 0:
            return images[0].get('src', '')
        
        # Default to empty string if no image found
        return ''
    
    def _cache_restaurants(self, restaurants: List[Dict[str, Any]]) -> None:
        """
        Cache restaurants data to file
        
        Args:
            restaurants: List of restaurant dictionaries
        """
        try:
            with open(self.restaurants_file, 'w') as f:
                json.dump({"restaurants": restaurants}, f, indent=2)
        except Exception as e:
            logger.error(f"Error caching restaurants: {str(e)}")
    
    def get_restaurant(self, restaurant_id: str) -> Dict[str, Any]:
        """
        Get a specific restaurant by ID
        
        Args:
            restaurant_id: Restaurant ID
            
        Returns:
            Dictionary with restaurant details
        """
        try:
            # Try to get from WooCommerce API
            product = self.woocommerce_service.get_product(restaurant_id)
            
            if product:
                restaurant = {
                    'id': str(product.get('id')),
                    'name': product.get('name', ''),
                    'cuisine': self._extract_cuisine(product),
                    'rating': self._extract_rating(product),
                    'address': self._extract_address(product),
                    'phone': self._extract_phone(product),
                    'image': self._extract_image(product)
                }
                return {"restaurant": restaurant}
            
            # If not found in WooCommerce, try fallback data
            with open(self.restaurants_file, 'r') as f:
                data = json.load(f)
            
            restaurants = data.get("restaurants", [])
            restaurant = next((r for r in restaurants if r.get("id") == restaurant_id), None)
            
            if not restaurant:
                return {"error": "Restaurant not found"}
            
            return {"restaurant": restaurant}
        
        except Exception as e:
            logger.error(f"Error getting restaurant: {str(e)}")
            # Try fallback data
            try:
                with open(self.restaurants_file, 'r') as f:
                    data = json.load(f)
                
                restaurants = data.get("restaurants", [])
                restaurant = next((r for r in restaurants if r.get("id") == restaurant_id), None)
                
                if not restaurant:
                    return {"error": "Restaurant not found"}
                
                return {"restaurant": restaurant}
            except Exception as fallback_error:
                logger.error(f"Error getting fallback restaurant: {str(fallback_error)}")
                return {"error": str(e)}
    
    def search_restaurants(self, query: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Search for restaurants by name, cuisine, or location
        
        Args:
            query: Search query
            location: Optional location filter
            
        Returns:
            Dictionary with search results
        """
        try:
            # Search products in WooCommerce
            # WooCommerce API doesn't support full text search well, so we'll fetch all products
            # and filter them on our side
            products = self.woocommerce_service.get_products(limit=100)
            
            # Transform and filter products
            query = query.lower()
            results = []
            
            for product in products:
                # Check if product matches search query
                name = product.get('name', '').lower()
                description = product.get('description', '').lower()
                short_description = product.get('short_description', '').lower()
                categories = [cat.get('name', '').lower() for cat in product.get('categories', [])]
                
                # Extract cuisine for matching
                cuisine = self._extract_cuisine(product).lower()
                
                # Extract address for location matching
                address = self._extract_address(product).lower()
                
                # Check if product matches query
                if (query in name or 
                    query in description or 
                    query in short_description or 
                    any(query in cat for cat in categories) or
                    query in cuisine):
                    
                    # Check location filter if specified
                    if location and location.lower() not in address:
                        continue
                    
                    # Convert to restaurant format
                    restaurant = {
                        'id': str(product.get('id')),
                        'name': product.get('name', ''),
                        'cuisine': cuisine,
                        'rating': self._extract_rating(product),
                        'address': address,
                        'phone': self._extract_phone(product),
                        'image': self._extract_image(product)
                    }
                    
                    # Add distance
                    distance_km = round(random.uniform(0.5, 10.0), 1)
                    restaurant["distance"] = f"{distance_km} km"
                    
                    results.append(restaurant)
            
            # Sort by distance
            results.sort(key=lambda r: float(r.get("distance", "0").split()[0]))
            
            # Cache results for fallback
            if results:
                self._cache_restaurants(results)
            
            return {"restaurants": results}
        
        except Exception as e:
            logger.error(f"Error searching restaurants from WooCommerce: {str(e)}")
            # Fall back to cached data
            try:
                with open(self.restaurants_file, 'r') as f:
                    data = json.load(f)
                
                restaurants = data.get("restaurants", [])
                
                # Filter by query
                query = query.lower()
                results = []
                
                for restaurant in restaurants:
                    name = restaurant.get("name", "").lower()
                    cuisine = restaurant.get("cuisine", "").lower()
                    address = restaurant.get("address", "").lower()
                    
                    if query in name or query in cuisine or query in address:
                        # Add a copy of the restaurant to results
                        results.append(restaurant.copy())
                
                # Filter by location if specified
                if location:
                    location = location.lower()
                    results = [r for r in results if location in r.get("address", "").lower()]
                
                # Add distance for demo purposes
                for restaurant in results:
                    distance_km = round(random.uniform(0.5, 10.0), 1)
                    restaurant["distance"] = f"{distance_km} km"
                
                # Sort by distance
                results.sort(key=lambda r: float(r.get("distance", "0").split()[0]))
                
                return {"restaurants": results}
            except Exception as fallback_error:
                logger.error(f"Error searching fallback restaurants: {str(fallback_error)}")
                return {"restaurants": [], "error": str(e)}
