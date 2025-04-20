import os
import json
import logging
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
from app.services.woocommerce_service import WooCommerceService

logger = logging.getLogger(__name__)

class OrderService:
    """Service for handling food and mall delivery orders"""
    
    def __init__(self, woocommerce_service: Optional[WooCommerceService] = None):
        """Initialize the order service"""
        self.woocommerce_service = woocommerce_service or WooCommerceService()
        
        # Path to store the cached orders
        self.kb_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   "knowledge_base", "orders.json")
        
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order in WooCommerce
        
        Args:
            order_data: Order data including products, customer info, etc.
            
        Returns:
            Order creation result
        """
        try:
            # Validate required fields
            required_fields = ["products", "customer"]
            for field in required_fields:
                if field not in order_data:
                    return {
                        "status": "error",
                        "message": f"Missing required field: {field}"
                    }
            
            # Format the order data for WooCommerce API
            wc_order_data = self._format_order_for_woocommerce(order_data)
            
            # Create the order in WooCommerce
            result = self.woocommerce_service.create_order(wc_order_data)
            
            # If successful, cache the order
            if result.get("status") == "success":
                self._cache_order(result.get("order"))
            
            return result
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
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
            Order details
        """
        return self.woocommerce_service.get_order_status(order_id)
    
    def get_customer_orders(self, customer_email: str) -> List[Dict[str, Any]]:
        """
        Get orders for a specific customer
        
        Args:
            customer_email: Customer email address
            
        Returns:
            List of customer orders
        """
        try:
            # Try to load cached orders
            cached_orders = self._get_cached_orders()
            
            # Filter orders by customer email
            customer_orders = []
            for order in cached_orders:
                billing = order.get("billing", {})
                if billing.get("email") == customer_email:
                    customer_orders.append(order)
            
            return {
                "status": "success",
                "orders": customer_orders
            }
        except Exception as e:
            logger.error(f"Error getting customer orders: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting customer orders: {str(e)}"
            }
    
    def _format_order_for_woocommerce(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format order data for WooCommerce API
        
        Args:
            order_data: Order data from the frontend
            
        Returns:
            WooCommerce-formatted order data
        """
        # Extract customer info
        customer = order_data.get("customer", {})
        
        # Format line items (products)
        line_items = []
        for product in order_data.get("products", []):
            product_id = product.get("id")
            quantity = product.get("quantity", 1)
            
            line_item = {
                "product_id": product_id,
                "quantity": quantity
            }
            
            # Add variation ID if provided
            if "variation_id" in product:
                line_item["variation_id"] = product["variation_id"]
            
            line_items.append(line_item)
        
        # Create the WooCommerce order data
        wc_order = {
            "payment_method": order_data.get("payment_method", "cod"),
            "payment_method_title": order_data.get("payment_method_title", "Cash on Delivery"),
            "set_paid": False,
            "billing": {
                "first_name": customer.get("first_name", ""),
                "last_name": customer.get("last_name", ""),
                "address_1": customer.get("address", ""),
                "address_2": customer.get("address_2", ""),
                "city": customer.get("city", ""),
                "state": customer.get("state", ""),
                "postcode": customer.get("postcode", ""),
                "country": customer.get("country", "RO"),
                "email": customer.get("email", ""),
                "phone": customer.get("phone", "")
            },
            "shipping": {
                "first_name": customer.get("first_name", ""),
                "last_name": customer.get("last_name", ""),
                "address_1": customer.get("address", ""),
                "address_2": customer.get("address_2", ""),
                "city": customer.get("city", ""),
                "state": customer.get("state", ""),
                "postcode": customer.get("postcode", ""),
                "country": customer.get("country", "RO")
            },
            "line_items": line_items,
            "shipping_lines": [
                {
                    "method_id": "flat_rate",
                    "method_title": "Delivery",
                    "total": str(order_data.get("shipping_cost", "0.00"))
                }
            ],
            "customer_note": order_data.get("notes", "")
        }
        
        return wc_order
    
    def _cache_order(self, order: Dict[str, Any]) -> None:
        """
        Cache an order for future reference
        
        Args:
            order: Order data to cache
        """
        try:
            # Load existing cached orders
            cached_orders = self._get_cached_orders()
            
            # Add the new order
            cached_orders.append(order)
            
            # Save back to the cache file
            with open(self.kb_path, 'w', encoding='utf-8') as f:
                json.dump({"orders": cached_orders}, f, indent=2)
                
            logger.info(f"Cached order #{order.get('id')}")
        except Exception as e:
            logger.error(f"Error caching order: {str(e)}")
    
    def _get_cached_orders(self) -> List[Dict[str, Any]]:
        """
        Get cached orders
        
        Returns:
            List of cached orders
        """
        try:
            if os.path.exists(self.kb_path):
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("orders", [])
            return []
        except Exception as e:
            logger.error(f"Error loading cached orders: {str(e)}")
            return []
