from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
from src.services.woocommerce_service import WooCommerceService

# Define router
order_router = APIRouter()

# Models for order creation
class OrderLineItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=1)
    
class CustomerInfo(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    address_1: Optional[str] = None
    address_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None
    country: Optional[str] = "RO"  # Default to Romania
    
class CreateOrderRequest(BaseModel):
    line_items: List[OrderLineItem]
    customer: CustomerInfo
    payment_method: str = "cod"  # Default to cash on delivery
    payment_method_title: str = "Cash on Delivery"
    set_paid: bool = False
    customer_note: Optional[str] = None

@order_router.post("/")
async def create_order(
    order_request: CreateOrderRequest,
    woocommerce: WooCommerceService = Depends()
):
    """
    Create a new order in WooCommerce.
    
    Args:
        order_request: Order data including line items and customer info
        
    Returns:
        Created order details
    """

@order_router.get("/customer/{customer_id}")
async def get_customer_orders(
    customer_id: int,
    woocommerce: WooCommerceService = Depends()
):
    """
    Get all orders for a specific customer.
    
    Args:
        customer_id: WooCommerce customer ID
        
    Returns:
        List of orders for the customer
    """
    try:
        return await woocommerce.get_orders(customer=customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer orders: {str(e)}")

@order_router.post("/")
async def create_order(
    order_request: CreateOrderRequest,
    woocommerce: WooCommerceService = Depends()
):
    """
    Create a new order in WooCommerce.
    
    Args:
        order_request: Order data including line items and customer info
        
    Returns:
        Created order details
    """
    try:
        # Format the order data for WooCommerce API
        order_data = {
            "payment_method": order_request.payment_method,
            "payment_method_title": order_request.payment_method_title,
            "set_paid": order_request.set_paid,
            "customer_note": order_request.customer_note,
            "billing": {
                "first_name": order_request.customer.first_name,
                "last_name": order_request.customer.last_name,
                "email": order_request.customer.email,
                "phone": order_request.customer.phone,
                "address_1": order_request.customer.address_1,
                "address_2": order_request.customer.address_2,
                "city": order_request.customer.city,
                "state": order_request.customer.state,
                "postcode": order_request.customer.postcode,
                "country": order_request.customer.country
            },
            "shipping": {
                "first_name": order_request.customer.first_name,
                "last_name": order_request.customer.last_name,
                "address_1": order_request.customer.address_1,
                "address_2": order_request.customer.address_2,
                "city": order_request.customer.city,
                "state": order_request.customer.state,
                "postcode": order_request.customer.postcode,
                "country": order_request.customer.country
            },
            "line_items": [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity
                }
                for item in order_request.line_items
            ],
            "shipping_lines": [
                {
                    "method_id": "flat_rate",
                    "method_title": "Flat Rate",
                    "total": "10.00"
                }
            ]
        }
        
        # Create the order
        order = await woocommerce.create_order(order_data)
        return order
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create order: {str(e)}")

@order_router.get("/")
async def get_orders(
    customer_id: Optional[int] = None,
    woocommerce: WooCommerceService = Depends()
):
    """
    Get orders, optionally filtered by customer ID.
    
    Args:
        customer_id: Filter orders by customer ID
        
    Returns:
        List of orders
    """
    try:
        return await woocommerce.get_orders(customer_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch orders: {str(e)}")

@order_router.get("/{order_id}")
async def get_order(
    order_id: int,
    woocommerce: WooCommerceService = Depends()
):
    """
    Get a specific order by ID.
    
    Args:
        order_id: WooCommerce order ID
        
    Returns:
        Order details
    """
    try:
        return await woocommerce._make_request(f"orders/{order_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch order: {str(e)}")
