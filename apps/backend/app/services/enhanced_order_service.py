import logging
from typing import Dict, List, Any, Optional
from .enhanced_woocommerce_service import EnhancedWooCommerceService

logger = logging.getLogger(__name__)

class EnhancedOrderService:
    """Service for handling orders with enhanced WooCommerce integration"""
    
    def __init__(self, woocommerce_service: EnhancedWooCommerceService):
        """
        Initialize the order service
        
        Args:
            woocommerce_service: Instance of EnhancedWooCommerceService
        """
        self.woocommerce_service = woocommerce_service
        logger.info("Enhanced Order Service initialized")
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new order
        
        Args:
            order_data: Order data including line_items, shipping, billing info
            
        Returns:
            Created order data or error information
        """
        try:
            # Format the order data for WooCommerce API
            formatted_order = self._format_order_data(order_data)
            
            # Create the order using WooCommerce service
            result = self.woocommerce_service.create_order(formatted_order)
            
            return result
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating order: {str(e)}"
            }
    
    def _format_order_data(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format order data for WooCommerce API
        
        Args:
            order_data: Raw order data from frontend
            
        Returns:
            Formatted order data for WooCommerce API
        """
        # Initialize formatted order with required fields
        formatted_order = {
            "payment_method": order_data.get("payment_method", "cod"),
            "payment_method_title": order_data.get("payment_method_title", "Cash on Delivery"),
            "set_paid": False,
            "status": "pending",
        }
        
        # Add customer information
        if "customer" in order_data:
            customer = order_data["customer"]
            
            # Add billing information
            formatted_order["billing"] = {
                "first_name": customer.get("first_name", ""),
                "last_name": customer.get("last_name", ""),
                "address_1": customer.get("address", ""),
                "city": customer.get("city", ""),
                "state": customer.get("state", ""),
                "postcode": customer.get("postcode", ""),
                "country": customer.get("country", "RO"),
                "email": customer.get("email", ""),
                "phone": customer.get("phone", "")
            }
            
            # Add shipping information (same as billing by default)
            formatted_order["shipping"] = formatted_order["billing"].copy()
            
            # Add customer note if provided
            if "note" in customer:
                formatted_order["customer_note"] = customer["note"]
        
        # Add line items (products)
        if "items" in order_data:
            formatted_order["line_items"] = []
            
            for item in order_data["items"]:
                line_item = {
                    "product_id": item.get("product_id"),
                    "quantity": item.get("quantity", 1)
                }
                
                # Add variation ID if provided
                if "variation_id" in item:
                    line_item["variation_id"] = item["variation_id"]
                
                formatted_order["line_items"].append(line_item)
        
        # Add coupon if provided
        if "coupon_code" in order_data:
            formatted_order["coupon_lines"] = [
                {
                    "code": order_data["coupon_code"]
                }
            ]
        
        # Add shipping line if provided
        if "shipping_method" in order_data:
            formatted_order["shipping_lines"] = [
                {
                    "method_id": order_data["shipping_method"],
                    "method_title": order_data.get("shipping_method_title", "Standard Shipping"),
                    "total": str(order_data.get("shipping_total", "0"))
                }
            ]
        
        return formatted_order
    
    def get_order(self, order_id: int) -> Dict[str, Any]:
        """
        Get order details by ID
        
        Args:
            order_id: WooCommerce order ID
            
        Returns:
            Order details or error information
        """
        return self.woocommerce_service.get_order(order_id)
    
    def get_customer_orders(self, customer_id: int) -> Dict[str, Any]:
        """
        Get orders for a specific customer
        
        Args:
            customer_id: WooCommerce customer ID
            
        Returns:
            List of customer orders or error information
        """
        return self.woocommerce_service.get_customer_orders(customer_id)
    
    def get_customer_orders_by_email(self, email: str) -> Dict[str, Any]:
        """
        Get orders for a customer by email
        
        Args:
            email: Customer email address
            
        Returns:
            List of customer orders or error information
        """
        try:
            # Find customer by email
            customer = self.woocommerce_service.get_customer_by_email(email)
            
            if customer:
                # Get orders for this customer
                return self.get_customer_orders(customer["id"])
            else:
                return {
                    "status": "error",
                    "message": f"Customer not found with email: {email}"
                }
        except Exception as e:
            logger.error(f"Error getting orders by email: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting orders by email: {str(e)}"
            }
    
    def update_order_status(self, order_id: int, status: str) -> Dict[str, Any]:
        """
        Update order status
        
        Args:
            order_id: WooCommerce order ID
            status: New order status (pending, processing, completed, etc.)
            
        Returns:
            Updated order data or error information
        """
        try:
            return self.woocommerce_service.update_order(order_id, {"status": status})
        except Exception as e:
            logger.error(f"Error updating order status: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating order status: {str(e)}"
            }
    
    def add_order_note(self, order_id: int, note: str, is_customer_note: bool = False) -> Dict[str, Any]:
        """
        Add a note to an order
        
        Args:
            order_id: WooCommerce order ID
            note: Note content
            is_customer_note: Whether the note is visible to the customer
            
        Returns:
            Result of the operation
        """
        try:
            # Get the current order
            order_result = self.woocommerce_service.get_order(order_id)
            
            if order_result["status"] == "error":
                return order_result
            
            # Add the note to the order
            order = order_result["order"]
            
            # Check if order has notes
            if "notes" not in order:
                order["notes"] = []
            
            # Add the new note
            order["notes"].append({
                "note": note,
                "customer_note": is_customer_note
            })
            
            # Update the order
            return self.woocommerce_service.update_order(order_id, order)
        except Exception as e:
            logger.error(f"Error adding order note: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding order note: {str(e)}"
            }
    
    def cancel_order(self, order_id: int, reason: Optional[str] = None) -> Dict[str, Any]:
        """
        Cancel an order
        
        Args:
            order_id: WooCommerce order ID
            reason: Optional reason for cancellation
            
        Returns:
            Result of the operation
        """
        try:
            # Update order status to cancelled
            result = self.update_order_status(order_id, "cancelled")
            
            # Add cancellation reason as a note if provided
            if result["status"] == "success" and reason:
                self.add_order_note(order_id, f"Cancellation reason: {reason}", True)
            
            return result
        except Exception as e:
            logger.error(f"Error cancelling order: {str(e)}")
            return {
                "status": "error",
                "message": f"Error cancelling order: {str(e)}"
            }
    
    def validate_coupon(self, code: str) -> Dict[str, Any]:
        """
        Validate a coupon code
        
        Args:
            code: Coupon code to validate
            
        Returns:
            Validation result
        """
        return self.woocommerce_service.validate_coupon(code)
