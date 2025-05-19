#!/usr/bin/env python3
import os
import json
import requests
from dotenv import load_dotenv
from woocommerce import API
from pprint import pprint

# Load environment variables
load_dotenv()

class WooCommerceExplorer:
    def __init__(self):
        """Initialize WooCommerce API explorer"""
        # Get credentials from environment variables
        self.api_url = os.environ.get("WP_API_URL", "https://vogo.family")
        self.consumer_key = os.environ.get("WP_CONSUMER_KEY", "ck_47075e7afebb1ad956d0350ee9ada1c93f3dbbaa")
        self.consumer_secret = os.environ.get("WP_CONSUMER_SECRET", "cs_c264cd481899b999ce5cd3cc3b97ff7cb32aab07")
        
        print(f"Initializing WooCommerce Explorer for {self.api_url}")
        print(f"Consumer key: {self.consumer_key[:5]}...{self.consumer_key[-5:]}")
        
        # Initialize WooCommerce API client
        self.wcapi = API(
            url=self.api_url,
            consumer_key=self.consumer_key,
            consumer_secret=self.consumer_secret,
            version="wc/v3",
            timeout=60
        )
        
        # Initialize Store API URL
        self.store_api_url = f"{self.api_url}/wp-json/wc/store/v1"
        
        # Output directory
        self.output_dir = "woocommerce_data"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def save_json(self, data, filename):
        """Save data to a JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Saved data to {filepath}")
        return filepath
    
    def discover_endpoints(self):
        """Discover available WooCommerce API endpoints"""
        print("\n=== DISCOVERING API ENDPOINTS ===")
        
        # Try to get the API index
        try:
            response = requests.get(f"{self.api_url}/wp-json/")
            if response.status_code == 200:
                routes = response.json().get("routes", {})
                
                # Extract WooCommerce related endpoints
                wc_routes = {k: v for k, v in routes.items() if "/wc/" in k}
                
                # Save all discovered routes
                self.save_json(routes, "all_wp_routes.json")
                self.save_json(wc_routes, "woocommerce_routes.json")
                
                print(f"Discovered {len(wc_routes)} WooCommerce related endpoints")
                return wc_routes
            else:
                print(f"Failed to get API index: {response.status_code}")
                
        except Exception as e:
            print(f"Error discovering endpoints: {str(e)}")
        
        return {}
    
    def get_products(self, per_page=100, max_pages=10):
        """Get all products using pagination"""
        print("\n=== FETCHING ALL PRODUCTS ===")
        all_products = []
        
        # Try using the authenticated API
        try:
            for page in range(1, max_pages + 1):
                print(f"Fetching products page {page}...")
                
                response = self.wcapi.get("products", params={
                    "per_page": per_page,
                    "page": page
                })
                
                if response.status_code != 200:
                    print(f"Error fetching products: {response.status_code}")
                    break
                
                products = response.json()
                
                if not products:
                    print("No more products found.")
                    break
                
                print(f"Found {len(products)} products on page {page}")
                all_products.extend(products)
                
                # Check if we've reached the last page
                total_pages = int(response.headers.get('X-WP-TotalPages', '1'))
                if page >= total_pages:
                    print(f"Reached last page of products ({total_pages})")
                    break
        
        except Exception as auth_error:
            print(f"Error using authenticated API: {str(auth_error)}")
            
            # Fall back to Store API
            try:
                print("Falling back to Store API...")
                
                for page in range(1, max_pages + 1):
                    url = f"{self.store_api_url}/products"
                    response = requests.get(url, params={
                        "per_page": per_page,
                        "page": page
                    })
                    
                    if response.status_code != 200:
                        print(f"Error fetching products from Store API: {response.status_code}")
                        break
                    
                    products = response.json()
                    
                    if not products:
                        print("No more products found.")
                        break
                    
                    print(f"Found {len(products)} products on page {page}")
                    all_products.extend(products)
                    
                    # Check if we've reached the last page
                    if len(products) < per_page:
                        print("Reached last page of products")
                        break
            
            except Exception as store_error:
                print(f"Error fetching from Store API: {str(store_error)}")
        
        # Save all products to file
        if all_products:
            filepath = self.save_json(all_products, "all_products.json")
            print(f"Saved {len(all_products)} products to {filepath}")
        else:
            print("No products found")
        
        return all_products
    
    def get_categories(self):
        """Get all product categories"""
        print("\n=== FETCHING ALL CATEGORIES ===")
        all_categories = []
        
        # Try the authenticated API
        try:
            response = self.wcapi.get("products/categories", params={"per_page": 100})
            
            if response.status_code == 200:
                categories = response.json()
                all_categories.extend(categories)
                print(f"Found {len(categories)} categories using authenticated API")
            else:
                print(f"Error fetching categories: {response.status_code}")
        
        except Exception as auth_error:
            print(f"Error using authenticated API for categories: {str(auth_error)}")
            
            # Fall back to Store API
            try:
                print("Falling back to Store API for categories...")
                url = f"{self.store_api_url}/products/categories"
                response = requests.get(url, params={"per_page": 100})
                
                if response.status_code == 200:
                    categories = response.json()
                    all_categories.extend(categories)
                    print(f"Found {len(categories)} categories using Store API")
                else:
                    print(f"Error fetching categories from Store API: {response.status_code}")
            
            except Exception as store_error:
                print(f"Error fetching categories from Store API: {str(store_error)}")
        
        # Save all categories to file
        if all_categories:
            filepath = self.save_json(all_categories, "all_categories.json")
            print(f"Saved {len(all_categories)} categories to {filepath}")
        else:
            print("No categories found")
        
        return all_categories
    
    def get_orders(self, max_count=20):
        """Get recent orders (limited sample)"""
        print("\n=== FETCHING SAMPLE ORDERS ===")
        try:
            response = self.wcapi.get("orders", params={"per_page": max_count})
            
            if response.status_code == 200:
                orders = response.json()
                print(f"Found {len(orders)} recent orders")
                
                # Save orders to file
                self.save_json(orders, "sample_orders.json")
                return orders
            else:
                print(f"Error fetching orders: {response.status_code}")
        
        except Exception as e:
            print(f"Error fetching orders: {str(e)}")
        
        return []
    
    def get_shipping_methods(self):
        """Get available shipping methods"""
        print("\n=== FETCHING SHIPPING METHODS ===")
        try:
            response = self.wcapi.get("shipping_methods")
            
            if response.status_code == 200:
                methods = response.json()
                print(f"Found {len(methods)} shipping methods")
                
                # Save shipping methods to file
                self.save_json(methods, "shipping_methods.json")
                return methods
            else:
                print(f"Error fetching shipping methods: {response.status_code}")
        
        except Exception as e:
            print(f"Error fetching shipping methods: {str(e)}")
        
        return []
    
    def get_payment_gateways(self):
        """Get available payment gateways"""
        print("\n=== FETCHING PAYMENT GATEWAYS ===")
        try:
            response = self.wcapi.get("payment_gateways")
            
            if response.status_code == 200:
                gateways = response.json()
                print(f"Found {len(gateways)} payment gateways")
                
                # Save payment gateways to file
                self.save_json(gateways, "payment_gateways.json")
                return gateways
            else:
                print(f"Error fetching payment gateways: {response.status_code}")
        
        except Exception as e:
            print(f"Error fetching payment gateways: {str(e)}")
        
        return []
    
    def explore_custom_endpoints(self):
        """Try exploring potential custom endpoints"""
        print("\n=== EXPLORING CUSTOM ENDPOINTS ===")
        custom_endpoints = [
            "products/attributes",
            "products/tags",
            "coupons",
            "customers",
            "reports/sales",
            "settings",
            "system_status",
            "shipping/zones",
            "taxes",
            "webhooks"
        ]
        
        results = {}
        
        for endpoint in custom_endpoints:
            print(f"Trying endpoint: {endpoint}")
            try:
                response = self.wcapi.get(endpoint)
                
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        print(f"✓ Success: Found {len(data)} items")
                    else:
                        print(f"✓ Success: Found data")
                    
                    # Save to results
                    results[endpoint] = data
                    
                    # Save individual endpoint data
                    filename = f"endpoint_{endpoint.replace('/', '_')}.json"
                    self.save_json(data, filename)
                else:
                    print(f"✗ Failed: {response.status_code}")
            
            except Exception as e:
                print(f"✗ Error: {str(e)}")
        
        # Save all discovered endpoint results
        if results:
            self.save_json(results, "custom_endpoints_data.json")
        
        return results

    def run_full_exploration(self):
        """Run a full exploration of the WooCommerce site"""
        print("\n====================================")
        print("STARTING FULL WOOCOMMERCE EXPLORATION")
        print("====================================")
        
        # Step 1: Discover API endpoints
        self.discover_endpoints()
        
        # Step 2: Get all products
        products = self.get_products()
        
        # Step 3: Get all categories
        categories = self.get_categories()
        
        # Step 4: Get sample orders
        self.get_orders()
        
        # Step 5: Get shipping methods
        self.get_shipping_methods()
        
        # Step 6: Get payment gateways
        self.get_payment_gateways()
        
        # Step 7: Explore custom endpoints
        self.explore_custom_endpoints()
        
        # Step 8: Generate summary report
        self.generate_summary(products, categories)
        
        print("\n====================================")
        print("EXPLORATION COMPLETE!")
        print(f"All data saved to {os.path.abspath(self.output_dir)}")
        print("====================================")
    
    def generate_summary(self, products, categories):
        """Generate a summary of the exploration results"""
        print("\n=== GENERATING SUMMARY REPORT ===")
        
        summary = {
            "site_url": self.api_url,
            "products_count": len(products),
            "categories_count": len(categories),
            "product_categories": {},
            "product_slugs": [],
            "category_slugs": []
        }
        
        # Collect category information
        for category in categories:
            cat_name = category.get("name", "Unknown")
            cat_slug = category.get("slug", "unknown")
            summary["category_slugs"].append(cat_slug)
            summary["product_categories"][cat_slug] = {
                "name": cat_name,
                "id": category.get("id"),
                "count": category.get("count", 0)
            }
        
        # Collect product slugs
        for product in products:
            summary["product_slugs"].append(product.get("slug", "unknown"))
        
        # Save summary to file
        self.save_json(summary, "exploration_summary.json")
        
        # Print basic summary
        print(f"Found {summary['products_count']} products across {summary['categories_count']} categories")
        
        # List categories with product counts
        print("\nProduct Categories:")
        for slug, cat in summary["product_categories"].items():
            print(f"  - {cat['name']} ({slug}): {cat['count']} products")
        
        return summary


if __name__ == "__main__":
    explorer = WooCommerceExplorer()
    explorer.run_full_exploration()
