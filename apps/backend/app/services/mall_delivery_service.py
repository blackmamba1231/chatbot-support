from typing import Dict, List, Any, Optional
import os
import json
import logging
from datetime import datetime, timedelta

from app.services.woocommerce_service import WooCommerceService

class MallDeliveryService:
    def __init__(self, woocommerce_service: WooCommerceService):
        self.woocommerce_service = woocommerce_service
        self.logger = logging.getLogger(__name__)
        
        # Location data for mall delivery services
        self.locations = [
            {
                "city": "Alba Iulia",
                "state": "Alba",
                "is_active": True,
                "services": ["mall_delivery", "restaurant_delivery"],
                "description": "Mall services and restaurant delivery available"
            },
            {
                "city": "Arad",
                "state": "Arad",
                "is_active": True,
                "services": ["mall_delivery", "restaurant_delivery"],
                "description": "Full mall delivery and restaurant services"
            },
            {
                "city": "Miercurea Ciuc",
                "state": "Harghita",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Shopping mall delivery available"
            },
            {
                "city": "Vaslui",
                "state": "Vaslui",
                "is_active": True,
                "services": ["mall_delivery", "restaurant_delivery"],
                "description": "Mall and restaurant delivery services"
            }
        ]
        
        # Mock pizza products for demonstration
        self.mock_pizza_products = [
            {
                "id": "1",
                "name": "Margherita Pizza",
                "price": "45.00",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
                "description": "Classic pizza with tomato sauce, mozzarella, and basil",
                "location": "Alba Iulia",
                "restaurant": "Pizza Roma"
            },
            {
                "id": "2",
                "name": "Pepperoni Pizza",
                "price": "55.00",
                "image": "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee",
                "description": "Pizza with tomato sauce, mozzarella, and pepperoni",
                "location": "Alba Iulia",
                "restaurant": "Pizza Roma"
            },
            {
                "id": "3",
                "name": "Vegetarian Pizza",
                "price": "50.00",
                "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38",
                "description": "Pizza with tomato sauce, mozzarella, and various vegetables",
                "location": "Alba Iulia",
                "restaurant": "Pizza Roma"
            },
            {
                "id": "4",
                "name": "Traditional Romanian Platter",
                "price": "75.00",
                "image": "https://images.unsplash.com/photo-1544025162-d76694265947",
                "description": "Selection of traditional Romanian dishes",
                "location": "Alba Iulia",
                "restaurant": "La Conac"
            },
            {
                "id": "5",
                "name": "Kung Pao Chicken",
                "price": "65.00",
                "image": "https://images.unsplash.com/photo-1525755662778-989d0524087e",
                "description": "Spicy stir-fried chicken with peanuts and vegetables",
                "location": "Alba Iulia",
                "restaurant": "Beijing Garden"
            },
            {
                "id": "6",
                "name": "Butter Chicken",
                "price": "70.00",
                "image": "https://images.unsplash.com/photo-1565557623262-b51c2513a641",
                "description": "Creamy tomato curry with tender chicken pieces",
                "location": "Alba Iulia",
                "restaurant": "Taj Mahal"
            },
            {
                "id": "7",
                "name": "Quattro Formaggi",
                "price": "60.00",
                "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
                "description": "Pizza with four different types of cheese",
                "location": "Arad",
                "restaurant": "Pizza Place"
            },
            {
                "id": "8",
                "name": "Hawaiian Pizza",
                "price": "55.00",
                "image": "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee",
                "description": "Pizza with tomato sauce, mozzarella, ham, and pineapple",
                "location": "Arad",
                "restaurant": "Pizza Place"
            },
            {
                "id": "9",
                "name": "Diavola Pizza",
                "price": "58.00",
                "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38",
                "description": "Spicy pizza with tomato sauce, mozzarella, and spicy salami",
                "location": "Vaslui",
                "restaurant": "Pizza House"
            },
        ]
    
    def get_locations(self) -> Dict[str, Any]:
        """Get all available mall delivery locations"""
        return {"locations": self.locations}
    
    def get_products(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get mall delivery products, optionally filtered by location"""
        try:
            # First try to get real products from WooCommerce
            products = self._get_products_from_woocommerce(location)
            if products:
                # If we got products from WooCommerce, still add our mock pizza products
                # for Alba Iulia to ensure pizza options are available
                if location and location.lower() == "alba iulia":
                    alba_iulia_products = [p for p in self.mock_pizza_products if p["location"].lower() == "alba iulia"]
                    products.extend(alba_iulia_products)
                return {"products": products}
        except Exception as e:
            self.logger.error(f"Error fetching products from WooCommerce: {str(e)}")
        
        # Fall back to mock data if WooCommerce fails
        filtered_products = self.mock_pizza_products
        if location:
            filtered_products = [p for p in self.mock_pizza_products if p["location"].lower() == location.lower()]
            
            # If no products found for this location, add some generic ones
            if not filtered_products and location.lower() == "alba iulia":
                filtered_products = [
                    {
                        "id": "alba-1",
                        "name": "Margherita Pizza - Pizza Roma",
                        "price": "45.00",
                        "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591",
                        "description": "Classic pizza with tomato sauce, mozzarella, and basil from Pizza Roma in Alba Iulia",
                        "location": "Alba Iulia",
                        "restaurant": "Pizza Roma"
                    },
                    {
                        "id": "alba-2",
                        "name": "Pepperoni Pizza - Pizza Roma",
                        "price": "55.00",
                        "image": "https://images.unsplash.com/photo-1534308983496-4fabb1a015ee",
                        "description": "Pizza with tomato sauce, mozzarella, and pepperoni from Pizza Roma in Alba Iulia",
                        "location": "Alba Iulia",
                        "restaurant": "Pizza Roma"
                    },
                    {
                        "id": "alba-3",
                        "name": "Traditional Platter - La Conac",
                        "price": "75.00",
                        "image": "https://images.unsplash.com/photo-1544025162-d76694265947",
                        "description": "Selection of traditional Romanian dishes from La Conac in Alba Iulia",
                        "location": "Alba Iulia",
                        "restaurant": "La Conac"
                    },
                ]
        
        return {"products": filtered_products}
    
    def _get_products_from_woocommerce(self, location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch products from WooCommerce API"""
        try:
            # Get products from WooCommerce, specifically from Mall Delivery category
            params = {
                "category": "223",  # Mall Delivery category ID
                "per_page": 100
            }
            woo_products = self.woocommerce_service.get_products(**params)
            
            self.logger.info(f"Fetched {len(woo_products)} products from WooCommerce Mall Delivery category")
            
            if not woo_products:
                self.logger.warning("No products found in WooCommerce Mall Delivery category")
                return []
            
            # Transform WooCommerce products to our format
            products = []
            for product in woo_products:
                # Extract location from product name (e.g., "Vaslui - Proxima Shopping Center")
                product_name = product.get("name", "")
                product_location = self._extract_location_from_name(product_name)
                
                # If location filter is provided, skip products that don't match
                if location and product_location and product_location.lower() != location.lower():
                    continue
                
                # Skip products without a valid price
                price = product.get("price", "")
                if not price:
                    continue
                
                products.append({
                    "id": str(product.get("id", "")),
                    "name": product.get("name", ""),
                    "price": str(price),
                    "image": self._get_product_image(product),
                    "description": product.get("short_description", "") or product.get("description", ""),
                    "location": product_location,
                    "restaurant": self._get_product_restaurant(product)
                })
            
            self.logger.info(f"Processed {len(products)} mall delivery products from WooCommerce")
            return products
        except Exception as e:
            self.logger.error(f"Error in _get_products_from_woocommerce: {str(e)}")
            return []
    
    def _get_product_image(self, product: Dict[str, Any]) -> str:
        """Extract product image URL from WooCommerce product data"""
        if "images" in product and product["images"] and len(product["images"]) > 0:
            return product["images"][0].get("src", "")
        return ""
    
    def _extract_location_from_name(self, product_name: str) -> str:
        """Extract location from product name (e.g., 'Vaslui - Proxima Shopping Center')"""
        # Common locations from the API documentation
        known_locations = [
            "Alba Iulia", "Arad", "Miercurea Ciuc", "Vaslui", "Târgu Mureș", "Pitești",
            "Târgu Mureş", "Piteşti", "Pitesti", "Targu Mures", "Miercurea-Ciuc"
        ]
        
        # Check if product name starts with a known location
        for location in known_locations:
            if product_name.startswith(location) or product_name.lower().startswith(location.lower()):
                return location
        
        # Try to extract location from the beginning of the name (assuming format: "Location - Mall Name")
        if " - " in product_name:
            potential_location = product_name.split(" - ")[0].strip()
            return potential_location
        
        # Default to first location if not found
        return "Alba Iulia"
        
    def _get_product_location(self, product: Dict[str, Any]) -> str:
        """Extract location from WooCommerce product data"""
        # First try to extract from product name
        product_name = product.get("name", "")
        if product_name:
            location = self._extract_location_from_name(product_name)
            if location:
                return location
                
        # Check meta data for location information
        if "meta_data" in product:
            for meta in product["meta_data"]:
                if meta.get("key") == "location":
                    return meta.get("value", "")
        
        # Default to first location if not found
        return "Alba Iulia"
    
    def _get_product_restaurant(self, product: Dict[str, Any]) -> str:
        """Extract restaurant name from WooCommerce product data"""
        # Check meta data for restaurant information
        if "meta_data" in product:
            for meta in product["meta_data"]:
                if meta.get("key") == "restaurant":
                    return meta.get("value", "")
        
        # Default to category name if available
        if "categories" in product and product["categories"] and len(product["categories"]) > 0:
            return product["categories"][0].get("name", "")
        
        return "Restaurant"
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order for mall delivery products"""
        try:
            # Try to create order in WooCommerce
            customer_info = order_data.get("customer", {})
            items = order_data.get("items", [])
            
            # Format items for WooCommerce
            line_items = []
            for item in items:
                line_items.append({
                    "product_id": int(item["id"]),
                    "quantity": item["quantity"]
                })
            
            # Create order data for WooCommerce
            woo_order_data = {
                "payment_method": "cod",
                "payment_method_title": "Cash on Delivery",
                "set_paid": False,
                "billing": {
                    "first_name": customer_info.get("name", "").split(" ")[0],
                    "last_name": " ".join(customer_info.get("name", "").split(" ")[1:]) if len(customer_info.get("name", "").split(" ")) > 1 else "",
                    "address_1": customer_info.get("address", ""),
                    "city": order_data.get("location", ""),
                    "email": customer_info.get("email", ""),
                    "phone": customer_info.get("phone", "")
                },
                "shipping": {
                    "first_name": customer_info.get("name", "").split(" ")[0],
                    "last_name": " ".join(customer_info.get("name", "").split(" ")[1:]) if len(customer_info.get("name", "").split(" ")) > 1 else "",
                    "address_1": customer_info.get("address", ""),
                    "city": order_data.get("location", "")
                },
                "line_items": line_items,
                "shipping_lines": [
                    {
                        "method_id": "flat_rate",
                        "method_title": "Delivery",
                        "total": "10.00"
                    }
                ]
            }
            
            # Create order in WooCommerce
            try:
                order_response = self.woocommerce_service.create_order(woo_order_data)
                if order_response and "id" in order_response:
                    return {
                        "success": True,
                        "order_id": str(order_response["id"]),
                        "message": "Order created successfully"
                    }
            except Exception as e:
                self.logger.error(f"Error creating order in WooCommerce: {str(e)}")
            
            # Fall back to mock order creation
            return {
                "success": True,
                "order_id": f"ORDER-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "message": "Order created successfully (mock)"
            }
        except Exception as e:
            self.logger.error(f"Error in create_order: {str(e)}")
            return {
                "success": False,
                "message": f"Error creating order: {str(e)}"
            }
