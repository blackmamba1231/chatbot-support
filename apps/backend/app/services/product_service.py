import logging
from typing import Dict, List, Any, Optional
from .enhanced_woocommerce_service import EnhancedWooCommerceService

logger = logging.getLogger(__name__)

class ProductService:
    """Service for handling product management with WooCommerce integration"""
    
    def __init__(self, woocommerce_service=None):
        """Initialize ProductService with WooCommerceService"""
        self.woocommerce_service = woocommerce_service or EnhancedWooCommerceService()
        logger.info("Product Service initialized")
    
    def get_products(self, category: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Get products, optionally filtered by category
        
        Args:
            category: Optional category slug to filter by
            limit: Maximum number of products to return
            
        Returns:
            List of products
        """
        try:
            products = self.woocommerce_service.get_products(category, limit)
            
            return {
                "status": "success",
                "products": products
            }
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching products: {str(e)}"
            }
    
    def get_product_by_id(self, product_id: int) -> Dict[str, Any]:
        """
        Get a specific product by ID
        
        Args:
            product_id: The WooCommerce product ID
            
        Returns:
            Product data or error information
        """
        try:
            product = self.woocommerce_service.get_product(product_id)
            
            if product:
                return {
                    "status": "success",
                    "product": product
                }
            else:
                return {
                    "status": "error",
                    "message": f"Product not found with ID: {product_id}"
                }
        except Exception as e:
            logger.error(f"Error fetching product: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching product: {str(e)}"
            }
    
    def search_products(self, query: str, category: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Enhanced search for products by name, description, slug, and category.
        Returns detailed match information with each product.
        
        Args:
            query: Search query
            category: Optional category filter
            limit: Maximum number of products to return
            
        Returns:
            Dict with status, products, match summary, and search insights
        """
        try:
            # Get enhanced search results with match info
            products = self.woocommerce_service.search_products(query, category, limit)
            
            # Generate search insights summary
            match_summary = self._generate_search_summary(products, query)
            
            return {
                "status": "success",
                "products": products,
                "match_summary": match_summary,
                "search_term": query,
                "count": len(products)
            }
        except Exception as e:
            logger.error(f"Error searching products: {str(e)}")
            return {
                "status": "error",
                "message": f"Error searching products: {str(e)}"
            }
            
    def _generate_search_summary(self, products: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """
        Generate a summary of search result matches for natural language responses
        
        Args:
            products: List of products with match_info
            query: Original search query
            
        Returns:
            Dict with match statistics and insights
        """
        # Initialize counters
        total = len(products)
        name_matches = 0
        slug_matches = 0
        description_matches = 0
        category_matches = 0
        category_slug_matches = 0
        
        # Category grouping
        categories = {}
        locations = {}
        
        # Track matching fields for each product
        for product in products:
            # Skip products without match info
            if "match_info" not in product:
                continue
                
            match_info = product.get("match_info", {})
            
            # Count match types
            if match_info.get("name_match"):
                name_matches += 1
                
            if match_info.get("slug_match"):
                slug_matches += 1
                
            if match_info.get("description_match") or match_info.get("short_description_match"):
                description_matches += 1
                
            if match_info.get("category_match"):
                category_matches += 1
                
            if match_info.get("category_slug_match"):
                category_slug_matches += 1
            
            # Group by category
            for category in product.get("categories", []):
                cat_name = category.get("name")
                if cat_name:
                    categories[cat_name] = categories.get(cat_name, 0) + 1
            
            # Extract location from product name if it's a mall delivery product
            name = product.get("name", "")
            if " - " in name:
                location = name.split(" - ")[0].strip()
                locations[location] = locations.get(location, 0) + 1
        
        # Determine primary match reason (for human-like responses)
        primary_match_reason = "products"
        if name_matches > 0:
            primary_match_reason = "product names"
        elif slug_matches > 0:
            primary_match_reason = "product identifiers"
        elif category_matches > 0 or category_slug_matches > 0:
            primary_match_reason = "product categories"
        elif description_matches > 0:
            primary_match_reason = "product descriptions"
            
        # Build summary
        return {
            "total": total,
            "name_matches": name_matches,
            "slug_matches": slug_matches,
            "description_matches": description_matches,
            "category_matches": category_matches,
            "category_slug_matches": category_slug_matches,
            "categories": categories,
            "locations": locations,
            "primary_match_reason": primary_match_reason,
            "query": query
        }
    
    def get_product_categories(self) -> List[Dict[str, Any]]:
        """Get all product categories"""
        try:
            categories = self.woocommerce_service.get_categories()
            
            return categories
        except Exception as e:
            logger.error(f"Error fetching product categories: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching product categories: {str(e)}"
            }
    
    def get_product_reviews(self, product_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get product reviews
        
        Args:
            product_id: Optional product ID to filter reviews
            
        Returns:
            List of review dictionaries
        """
        try:
            reviews = self.woocommerce_service.get_product_reviews(product_id)
            
            return {
                "status": "success",
                "reviews": reviews
            }
        except Exception as e:
            logger.error(f"Error fetching product reviews: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching product reviews: {str(e)}"
            }
    
    def get_products_by_category_tree(self) -> Dict[str, Any]:
        """
        Get products organized by category tree
        
        Returns:
            Dictionary with categories as keys and lists of products as values
        """
        try:
            # Get all categories
            categories_result = self.get_product_categories()
            
            if isinstance(categories_result, dict) and categories_result.get("status") == "error":
                return categories_result
            
            categories = categories_result
            
            # Create a dictionary to store products by category
            products_by_category = {}
            
            # Process each category
            for category in categories:
                # Skip categories with no products
                if category.get("count", 0) == 0:
                    continue
                
                # Get products for this category
                category_products = self.woocommerce_service.get_products(category["slug"], 20)
                
                # Add to dictionary
                products_by_category[category["slug"]] = {
                    "category": category,
                    "products": category_products
                }
            
            return {
                "status": "success",
                "products_by_category": products_by_category
            }
        except Exception as e:
            logger.error(f"Error fetching products by category tree: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching products by category tree: {str(e)}"
            }
    
    def get_restaurants(self, location: Optional[str] = None, limit: int = 50) -> Dict[str, Any]:
        """Get restaurants for a specific location"""
        try:
            result = self.woocommerce_service.get_restaurants(location)
            if result.get("status") == "success":
                # limit the number of restaurants returned
                restaurants = result["restaurants"][:limit]
                return {"status": "success", "restaurants": restaurants}
            else:
                return result
        except Exception as e:
            logger.error(f"Error fetching restaurants: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching restaurants: {str(e)}"
            }
    
    def get_mall_services(self, location: Optional[str] = None) -> Dict[str, Any]:
        """Get mall delivery services for a specific location"""
        try:
            mall_services = self.woocommerce_service.get_mall_delivery_services(location)
            
            return {
                "status": "success",
                "mall_services": mall_services
            }
        except Exception as e:
            logger.error(f"Error fetching mall services: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching mall services: {str(e)}"
            }
    
    def get_locations(self) -> List[str]:
        """Get all available delivery locations"""
        try:
            locations = self.woocommerce_service.get_locations()
            
            return locations
        except Exception as e:
            logger.error(f"Error fetching locations: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching locations: {str(e)}"
            }
    
    def get_product(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific product by ID"""
        try:
            product = self.woocommerce_service.get_product(product_id)
            
            return product
        except Exception as e:
            logger.error(f"Error fetching product: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching product: {str(e)}"
            }
    
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new order"""
        try:
            order = self.woocommerce_service.create_order(order_data)
            
            return order
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return {
                "status": "error",
                "message": f"Error creating order: {str(e)}"
            }
    
    def get_order(self, order_id: int) -> Optional[Dict[str, Any]]:
        """Get order details by ID"""
        try:
            order = self.woocommerce_service.get_order(order_id)
            
            return order
        except Exception as e:
            logger.error(f"Error fetching order: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching order: {str(e)}"
            }
    
    def get_featured_products(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get featured products
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of featured products
        """
        try:
            # Get featured products using Store API
            products = self.woocommerce_service.get_products(limit=100)
            
            # Filter for featured products
            featured_products = [p for p in products if p.get("featured", False)]
            
            return {
                "status": "success",
                "products": featured_products[:limit]
            }
        except Exception as e:
            logger.error(f"Error fetching featured products: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching featured products: {str(e)}"
            }
    
    def get_on_sale_products(self, limit: int = 10) -> Dict[str, Any]:
        """
        Get products that are on sale
        
        Args:
            limit: Maximum number of products to return
            
        Returns:
            List of on-sale products
        """
        try:
            # Get on-sale products using Store API
            products = self.woocommerce_service.get_products(limit=100)
            
            # Filter for on-sale products
            on_sale_products = [p for p in products if p.get("on_sale", False)]
            
            return {
                "status": "success",
                "products": on_sale_products[:limit]
            }
        except Exception as e:
            logger.error(f"Error fetching on-sale products: {str(e)}")
            return {
                "status": "error",
                "message": f"Error fetching on-sale products: {str(e)}"
            }
