#!/usr/bin/env python3
import os
import json
import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from pprint import pprint
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VogoWebScraper:
    """Scraper for extracting product data from vogo.family website"""
    
    def __init__(self, base_url="https://vogo.family"):
        """Initialize the scraper"""
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5'
        })
        
        # Create output directory
        self.output_dir = "scraped_data"
        os.makedirs(self.output_dir, exist_ok=True)
        
        logger.info(f"Initialized scraper for {self.base_url}")
    
    def save_json(self, data, filename):
        """Save data to a JSON file"""
        filepath = os.path.join(self.output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved data to {filepath}")
        return filepath
    
    def get_url(self, url_path):
        """Get full URL from path"""
        return urljoin(self.base_url, url_path)
    
    def fetch_page(self, url_path):
        """Fetch a page and return the BeautifulSoup object"""
        url = self.get_url(url_path)
        try:
            logger.info(f"Fetching {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_product_links(self, soup):
        """Extract product links from a page"""
        product_links = []
        
        # Try to find product links - look for common WooCommerce patterns
        # Method 1: Look for product links in WooCommerce product grids
        products = soup.select('.product a.woocommerce-loop-product__link')
        if not products:
            products = soup.select('.product a.woocommerce-LoopProduct-link')
        if not products:
            products = soup.select('.products .product a')
        if not products:
            products = soup.select('li.product a')
        if not products:
            products = soup.select('a.product_type_simple')
        
        for product in products:
            href = product.get('href')
            if href and '/product/' in href:
                product_links.append(href)
        
        # Remove duplicates
        product_links = list(set(product_links))
        
        logger.info(f"Found {len(product_links)} product links")
        return product_links
    
    def extract_category_links(self, soup):
        """Extract category links from a page"""
        category_links = []
        
        # Method 1: Look for category links in WooCommerce category lists
        categories = soup.select('.product-category a')
        if not categories:
            categories = soup.select('.product-categories a')
        if not categories:
            categories = soup.select('li.cat-item a')
        if not categories:
            categories = soup.select('.wc-block-product-categories-list a')
            
        for category in categories:
            href = category.get('href')
            if href and '/product-category/' in href:
                category_links.append(href)
        
        # Remove duplicates
        category_links = list(set(category_links))
        
        logger.info(f"Found {len(category_links)} category links")
        return category_links
    
    def extract_product_details(self, soup, url):
        """Extract product details from a product page"""
        product = {
            'url': url,
            'slug': urlparse(url).path.split('/')[-2] if urlparse(url).path.endswith('/') else urlparse(url).path.split('/')[-1]
        }
        
        # Extract product name
        product_name = soup.select_one('.product_title')
        if product_name:
            product['name'] = product_name.text.strip()
        
        # Extract product price
        product_price = soup.select_one('.price')
        if product_price:
            product['price'] = product_price.text.strip()
        
        # Extract product description
        product_short_desc = soup.select_one('.woocommerce-product-details__short-description')
        if product_short_desc:
            product['short_description'] = product_short_desc.text.strip()
        
        product_desc = soup.select_one('#tab-description')
        if product_desc:
            product['description'] = product_desc.text.strip()
        elif soup.select_one('.woocommerce-Tabs-panel--description'):
            product['description'] = soup.select_one('.woocommerce-Tabs-panel--description').text.strip()
        
        # Extract product categories
        product_cats = []
        cat_links = soup.select('.posted_in a')
        for cat_link in cat_links:
            cat_url = cat_link.get('href')
            cat_name = cat_link.text.strip()
            cat_slug = urlparse(cat_url).path.split('/')[-2] if urlparse(cat_url).path.endswith('/') else urlparse(cat_url).path.split('/')[-1]
            product_cats.append({
                'name': cat_name,
                'slug': cat_slug,
                'url': cat_url
            })
        
        product['categories'] = product_cats
        
        # Extract product images
        product_images = []
        img_elements = soup.select('.woocommerce-product-gallery__image img')
        for img in img_elements:
            img_url = img.get('src') or img.get('data-src') or img.get('data-large_image')
            if img_url:
                product_images.append(img_url)
        
        product['images'] = product_images
        
        # Extract product attributes
        attributes = {}
        attr_rows = soup.select('.woocommerce-product-attributes-item')
        for row in attr_rows:
            label = row.select_one('.woocommerce-product-attributes-item__label')
            value = row.select_one('.woocommerce-product-attributes-item__value')
            if label and value:
                key = label.text.strip().rstrip(':')
                attributes[key] = value.text.strip()
        
        product['attributes'] = attributes
        
        logger.info(f"Extracted details for product: {product.get('name', product['slug'])}")
        return product
    
    def extract_category_details(self, soup, url):
        """Extract category details from a category page"""
        category = {
            'url': url,
            'slug': urlparse(url).path.split('/')[-2] if urlparse(url).path.endswith('/') else urlparse(url).path.split('/')[-1]
        }
        
        # Extract category name
        category_name = soup.select_one('.woocommerce-products-header__title')
        if category_name:
            category['name'] = category_name.text.strip()
        else:
            # Try alternative selectors
            category_name = soup.select_one('h1.page-title')
            if category_name:
                category['name'] = category_name.text.strip()
        
        # Extract category description
        category_desc = soup.select_one('.term-description')
        if category_desc:
            category['description'] = category_desc.text.strip()
            
        logger.info(f"Extracted details for category: {category.get('name', category['slug'])}")
        return category
    
    def scrape_shop_page(self):
        """Scrape the main shop page to discover products and categories"""
        logger.info("Scraping main shop page")
        
        # First try the /shop/ URL
        soup = self.fetch_page('/shop/')
        if not soup:
            # If that fails, try the root URL
            soup = self.fetch_page('/')
        
        if not soup:
            logger.error("Failed to fetch the shop page")
            return [], []
        
        # Extract product and category links
        product_links = self.extract_product_links(soup)
        category_links = self.extract_category_links(soup)
        
        return product_links, category_links
    
    def scrape_products(self, product_links, max_products=100):
        """Scrape details for a list of products"""
        products = []
        
        for i, url in enumerate(product_links[:max_products], 1):
            logger.info(f"Scraping product {i}/{min(len(product_links), max_products)}: {url}")
            soup = self.fetch_page(url)
            if soup:
                product = self.extract_product_details(soup, url)
                products.append(product)
        
        # Save the scraped products
        if products:
            self.save_json(products, "scraped_products.json")
        
        return products
    
    def scrape_categories(self, category_links):
        """Scrape details for a list of categories"""
        categories = []
        
        for i, url in enumerate(category_links, 1):
            logger.info(f"Scraping category {i}/{len(category_links)}: {url}")
            soup = self.fetch_page(url)
            if soup:
                category = self.extract_category_details(soup, url)
                categories.append(category)
                
                # Also look for product links on the category page
                product_links = self.extract_product_links(soup)
                category['product_links'] = product_links
        
        # Save the scraped categories
        if categories:
            self.save_json(categories, "scraped_categories.json")
        
        return categories
    
    def discover_menu_items(self, soup):
        """Extract menu items from the main navigation"""
        menu_items = []
        
        # Find all navigation menu items
        nav_items = soup.select('.menu-item a') or soup.select('nav a') or soup.select('#menu-main-menu a')
        
        for item in nav_items:
            href = item.get('href')
            if href and self.base_url in href:
                menu_items.append({
                    'text': item.text.strip(),
                    'url': href,
                    'slug': urlparse(href).path.strip('/')
                })
        
        logger.info(f"Found {len(menu_items)} menu items")
        
        if menu_items:
            self.save_json(menu_items, "menu_items.json")
            
        return menu_items
    
    def run_full_scrape(self):
        """Run a full scrape of the website"""
        logger.info("Starting full website scrape")
        
        # Scrape the homepage to get menu items
        home_soup = self.fetch_page('/')
        if home_soup:
            menu_items = self.discover_menu_items(home_soup)
        
        # Scrape the shop page to get products and categories
        product_links, category_links = self.scrape_shop_page()
        
        # Scrape individual categories
        categories = self.scrape_categories(category_links)
        
        # Gather more product links from categories
        all_product_links = set(product_links)
        for category in categories:
            all_product_links.update(category.get('product_links', []))
        
        logger.info(f"Found a total of {len(all_product_links)} unique product links")
        
        # Scrape individual products
        products = self.scrape_products(list(all_product_links))
        
        # Generate a summary of everything found
        summary = {
            'product_count': len(products),
            'category_count': len(categories),
            'all_product_slugs': [p.get('slug') for p in products],
            'all_category_slugs': [c.get('slug') for c in categories],
            'product_by_category': {}
        }
        
        # Organize products by category
        for product in products:
            for category in product.get('categories', []):
                cat_slug = category.get('slug')
                if cat_slug:
                    if cat_slug not in summary['product_by_category']:
                        summary['product_by_category'][cat_slug] = []
                    summary['product_by_category'][cat_slug].append(product.get('slug'))
        
        # Save the summary
        self.save_json(summary, "scrape_summary.json")
        
        logger.info(f"Scraping complete! Found {len(products)} products and {len(categories)} categories")
        return summary

if __name__ == "__main__":
    scraper = VogoWebScraper()
    summary = scraper.run_full_scrape()
    
    # Print a brief summary of what was found
    print("\n=== SCRAPING RESULTS ===")
    print(f"Found {summary['product_count']} products across {summary['category_count']} categories")
    
    print("\nCategories and product counts:")
    for cat_slug, products in summary['product_by_category'].items():
        print(f"  - {cat_slug}: {len(products)} products")
