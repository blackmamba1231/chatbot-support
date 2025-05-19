import logging
from typing import Dict, List, Any, Optional
from .enhanced_woocommerce_service import EnhancedWooCommerceService

logger = logging.getLogger(__name__)

class CustomerService:
    """Service for handling customer management with WooCommerce integration"""
    
    def __init__(self, woocommerce_service: EnhancedWooCommerceService):
        """
        Initialize the customer service
        
        Args:
            woocommerce_service: Instance of EnhancedWooCommerceService
        """
        self.woocommerce_service = woocommerce_service
        logger.info("Customer Service initialized")
    
    def create_customer(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new customer
        
        Args:
            customer_data: Customer data including email, name, etc.
            
        Returns:
            Created customer data or error information
        """
        try:
            # Format the customer data for WooCommerce API
            formatted_customer = self._format_customer_data(customer_data)
            
            # Check if customer already exists
            existing_customer = self.woocommerce_service.get_customer_by_email(formatted_customer.get("email", ""))
            
            if existing_customer:
                return {
                    "status": "error",
                    "message": "Customer with this email already exists",
                    "customer": existing_customer
                }
            
            # Create the customer using WooCommerce service
            return self.woocommerce_service.create_customer(formatted_customer)
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating customer: {str(e)}"
            }
    
    def _format_customer_data(self, customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format customer data for WooCommerce API
        
        Args:
            customer_data: Raw customer data from frontend
            
        Returns:
            Formatted customer data for WooCommerce API
        """
        # Initialize formatted customer with required fields
        formatted_customer = {
            "email": customer_data.get("email", ""),
            "first_name": customer_data.get("first_name", ""),
            "last_name": customer_data.get("last_name", ""),
            "username": customer_data.get("username", customer_data.get("email", "")),
            "password": customer_data.get("password", ""),
        }
        
        # Add billing information if provided
        if "billing" in customer_data:
            billing = customer_data["billing"]
            formatted_customer["billing"] = {
                "first_name": billing.get("first_name", formatted_customer["first_name"]),
                "last_name": billing.get("last_name", formatted_customer["last_name"]),
                "company": billing.get("company", ""),
                "address_1": billing.get("address_1", ""),
                "address_2": billing.get("address_2", ""),
                "city": billing.get("city", ""),
                "state": billing.get("state", ""),
                "postcode": billing.get("postcode", ""),
                "country": billing.get("country", "RO"),
                "email": billing.get("email", formatted_customer["email"]),
                "phone": billing.get("phone", "")
            }
        
        # Add shipping information if provided
        if "shipping" in customer_data:
            shipping = customer_data["shipping"]
            formatted_customer["shipping"] = {
                "first_name": shipping.get("first_name", formatted_customer["first_name"]),
                "last_name": shipping.get("last_name", formatted_customer["last_name"]),
                "company": shipping.get("company", ""),
                "address_1": shipping.get("address_1", ""),
                "address_2": shipping.get("address_2", ""),
                "city": shipping.get("city", ""),
                "state": shipping.get("state", ""),
                "postcode": shipping.get("postcode", ""),
                "country": shipping.get("country", "RO")
            }
        
        return formatted_customer
    
    def get_customer(self, customer_id: int) -> Dict[str, Any]:
        """
        Get customer details by ID
        
        Args:
            customer_id: WooCommerce customer ID
            
        Returns:
            Customer data or error information
        """
        try:
            customer = self.woocommerce_service.get_customer(customer_id)
            
            if customer:
                return {
                    "status": "success",
                    "customer": customer
                }
            else:
                return {
                    "status": "error",
                    "message": f"Customer not found with ID: {customer_id}"
                }
        except Exception as e:
            logger.error(f"Error fetching customer: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching customer: {str(e)}"
            }
    
    def get_customer_by_email(self, email: str) -> Dict[str, Any]:
        """
        Get customer details by email
        
        Args:
            email: Customer email address
            
        Returns:
            Customer data or error information
        """
        try:
            customer = self.woocommerce_service.get_customer_by_email(email)
            
            if customer:
                return {
                    "status": "success",
                    "customer": customer
                }
            else:
                return {
                    "status": "error",
                    "message": f"Customer not found with email: {email}"
                }
        except Exception as e:
            logger.error(f"Error fetching customer by email: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching customer by email: {str(e)}"
            }
    
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
            # Format the customer data for WooCommerce API
            formatted_customer = self._format_customer_data(customer_data)
            
            # Update the customer using WooCommerce service
            return self.woocommerce_service.update_customer(customer_id, formatted_customer)
        except Exception as e:
            logger.error(f"Error updating customer: {str(e)}")
            return {
                "status": "error",
                "message": f"Error updating customer: {str(e)}"
            }
    
    def add_customer_address(self, customer_id: int, address_data: Dict[str, Any], address_type: str = "billing") -> Dict[str, Any]:
        """
        Add a new address to a customer
        
        Args:
            customer_id: WooCommerce customer ID
            address_data: Address data
            address_type: Type of address (billing or shipping)
            
        Returns:
            Updated customer data or error information
        """
        try:
            # Get current customer data
            customer_result = self.get_customer(customer_id)
            
            if customer_result["status"] == "error":
                return customer_result
            
            customer = customer_result["customer"]
            
            # Update the address
            if address_type == "billing":
                customer["billing"] = address_data
            elif address_type == "shipping":
                customer["shipping"] = address_data
            else:
                return {
                    "status": "error",
                    "message": f"Invalid address type: {address_type}"
                }
            
            # Update the customer
            return self.woocommerce_service.update_customer(customer_id, customer)
        except Exception as e:
            logger.error(f"Error adding customer address: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding customer address: {str(e)}"
            }
