import requests
from bs4 import BeautifulSoup
import json
import os
import time
import logging
import re
import shutil
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
import asyncio

logger = logging.getLogger(__name__)

class VogoScraper:
    """
    A controlled web scraper for vogo.family to supplement API data.
    This scraper is designed to run once daily to update the local knowledge base
    with product and service information from the website.
    """
    def __init__(self):
        self.base_url = "https://vogo.family"
        # Based on the 404 error, the site may not use /product-category/ directly
        # Let's use the shop URL which typically lists all products on WooCommerce sites
        self.categories_url = f"{self.base_url}/shop/"
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scraped_data")
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory at {self.data_dir}")
    
    def get_page(self, url: str, retries: int = 3, timeout: int = 15) -> str:
        """
        Get HTML content with proper headers and delay, with retry logic
        
        Args:
            url: The URL to fetch
            retries: Number of retry attempts (default: 3)
            timeout: Timeout in seconds (default: 15)
            
        Returns:
            The HTML content as a string
        """
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml",
            "Accept-Language": "en-US,en;q=0.9,ro;q=0.8,fr;q=0.7"  # Support multiple languages
        }
        
        for attempt in range(retries):
            try:
                logger.info(f"Fetching page: {url} (Attempt {attempt+1}/{retries})")
                response = requests.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                time.sleep(2)  # Be respectful with rate limiting
                return response.text
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout fetching {url} (Attempt {attempt+1}/{retries})")
                # Wait longer between retries
                time.sleep(3 * (attempt + 1))
            except requests.exceptions.ConnectionError:
                logger.warning(f"Connection error fetching {url} (Attempt {attempt+1}/{retries})")
                time.sleep(3 * (attempt + 1))
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                time.sleep(2)
        
        # All retries failed
        logger.error(f"Failed to fetch {url} after {retries} attempts")
        return ""
    
    def scrape_categories(self) -> List[Dict[str, str]]:
        """
        Scrape main product categories
        
        Returns:
            List of category dictionaries with name and URL
        """
        html = self.get_page(self.categories_url)
        if not html:
            logger.error("Failed to get categories page")
            # Let's use main navigation links as a fallback approach
            return self._get_categories_from_nav()
            
        soup = BeautifulSoup(html, 'html.parser')
        categories = []
        
        # Extract categories (adapt selectors to match the website structure)
        # This is based on typical WooCommerce structure but may need adjustment
        category_elements = soup.select('.product-category')
        
        if not category_elements:
            # Try alternative selectors commonly used in WooCommerce themes
            category_elements = soup.select('.woocommerce-loop-category__title, .wc-block-product-category, .product-categories li')
            
        if not category_elements:
            logger.warning("Could not find product categories with standard selectors, trying alternative approach")
            return self._get_categories_from_nav()
            
        for element in category_elements:
            link = element.find('a')
            if link:
                category_name = link.get_text().strip()
                # Remove any "(" count suffix that WooCommerce adds
                category_name = category_name.split('(')[0].strip()
                categories.append({
                    'name': category_name,
                    'url': link['href']
                })
                
        # Save categories
        with open(os.path.join(self.data_dir, "categories.json"), 'w', encoding='utf-8') as f:
            json.dump(categories, f, ensure_ascii=False, indent=2)
            
        logger.info(f"Scraped {len(categories)} categories")
        return categories
    
    def _get_categories_from_nav(self) -> List[Dict[str, str]]:
        """
        Alternative method to extract categories from the main navigation menu
        Used as a fallback when product category pages can't be accessed
        
        Returns:
            List of category dictionaries with name and URL
        """
        html = self.get_page(self.base_url)
        if not html:
            logger.error("Failed to get main page")
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        categories = []
        
        # Try to find main navigation menu items that might be categories
        # Common patterns in WordPress/WooCommerce sites
        nav_items = soup.select('nav li a, .menu-item a, .main-menu a, .main-navigation a, #menu-main-menu a, .header-menu a')
        
        # Also look for links in the header and footer that might point to category pages
        header_footer_links = soup.select('header a, footer a, .header a, .footer a')
        nav_items.extend(header_footer_links)
        
        # Track what we've processed to avoid duplicates
        processed_urls = set()
        
        for item in nav_items:
            href = item.get('href')
            text = item.get_text().strip()
            
            # Skip items that are likely not product categories or duplicates
            if not href or not text or href in processed_urls:
                continue
                
            processed_urls.add(href)
                
            # Skip very short items or likely header/footer links
            if len(text) < 3 or any(skip in text.lower() for skip in ['home', 'contact', 'about', 'login', 'register']):
                continue
                
            # If the URL points to the shop or a product category, it's likely a category
            if 'shop' in href or 'product-category' in href or 'product' in href:
                categories.append({
                    'name': text,
                    'url': href
                })
            
            # Look specifically for pet-related categories
            pet_keywords = ['pet', 'dog', 'cat', 'animal', 'veterinary', 'clinic', 'vet']
            if any(keyword in text.lower() for keyword in pet_keywords):
                logger.info(f"Found pet-related category: {text}")
                categories.append({
                    'name': text,
                    'url': href
                })
                
        # If we still don't have categories, add some default ones
        if not categories:
            logger.warning("Could not extract categories from navigation, adding default categories")
            categories = [
                {'name': 'Restaurant Delivery', 'url': f"{self.base_url}/shop/"},
                {'name': 'Pet Services', 'url': f"{self.base_url}/shop/"},
                {'name': 'Mall Delivery', 'url': f"{self.base_url}/shop/"}
            ]
        
        # Also add mall delivery and restaurant categories that we know exist
        known_categories = [
            {'name': 'Mall Delivery', 'url': f"{self.base_url}/product-category/mall-delivery/"},
            {'name': 'Restaurant', 'url': f"{self.base_url}/product-category/restaurant/"}
        ]
        
        # Add known categories that aren't already in our list
        for known_cat in known_categories:
            if not any(cat['name'].lower() == known_cat['name'].lower() for cat in categories):
                categories.append(known_cat)
                
        return categories
    
    def scrape_products(self, category_url: str, category_name: str) -> List[Dict[str, str]]:
        """
        Scrape products from a category page
        
        Args:
            category_url: URL of the category page
            category_name: Name of the category
            
        Returns:
            List of product dictionaries
        """
        html = self.get_page(category_url)
        if not html:
            logger.error(f"Failed to get product page for {category_name}")
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        
        # Extract products (typical WooCommerce structure)
        product_elements = soup.select('li.product, ul.products li, .product')
        if not product_elements:
            # Try alternative selectors for different WooCommerce themes
            product_elements = soup.select('.wc-block-grid__product, .woocommerce-loop-product, div[data-product-id]')
            
        for element in product_elements:
            try:
                # IMPROVED TITLE EXTRACTION
                # Extract from URL path as a fallback (often more reliable in custom themes)
                url_path = ""
                link = element.find('a', href=True)
                if link:
                    url = link['href']
                    url_path = url.rstrip('/').split('/')[-1].replace('-', ' ').replace('_', ' ').title()
                    
                # Direct HTML approaches
                # 1. Try standard WooCommerce title tags with any class
                title_tag = element.find(['h2', 'h3', 'h4', 'h5'])
                
                # 2. Also check for links within the product, which often contain the title
                if not title_tag:
                    link_tag = element.find('a')
                    if link_tag and link_tag.get_text().strip() and not link_tag.find('img'):
                        title_tag = link_tag
                        
                # 3. Look for any element with a title attribute
                if not title_tag:
                    element_with_title = element.find(title=True)
                    if element_with_title:
                        title_from_attr = element_with_title.get('title')
                        if title_from_attr and len(title_from_attr) > 3:
                            title = title_from_attr
            
                # 4. Check for data attributes that might contain title (common in some themes)
                if not title_tag:
                    for el in element.find_all(attrs={"data-title": True}):
                        title_tag = el
                        break
            
                # Get title text or use the URL path as fallback, or finally "Unknown Product"
                title = title_tag.get_text().strip() if title_tag else (url_path if url_path else "Unknown Product")
                
                # Clean up the title text (remove extra spaces, line breaks)
                title = re.sub(r'\s+', ' ', title).strip()
                
                # Log the title extraction for debugging
                if title == "Unknown Product":
                    logger.warning(f"Could not extract product title from element. URL: {url if 'url' in locals() else 'No URL found'}")
                else:
                    logger.info(f"Successfully extracted product title: {title}")
                    
                # Link is usually on the title or image
                link = element.find('a', href=True)
                url = link['href'] if link else "#"
                
                # EXACT MATCH FOR VOGO.FAMILY PRICE STRUCTURE
                # 1. Try the exact class structure from the site
                price_tag = element.find('span', class_='woocommerce-Price-amount amount')
                if not price_tag:
                    # Try with space-separated classes
                    price_tag = element.select_one('span.woocommerce-Price-amount.amount')
                
                # 2. If found, extract the text carefully
                if price_tag:
                    # The price might be inside nested font tags or bdi
                    bdi_tag = price_tag.find('bdi')
                    if bdi_tag:
                        price_tag = bdi_tag
                    
                    # Sometimes the price is in a nested font tag
                    font_tags = price_tag.find_all('font')
                    if font_tags and len(font_tags) > 0:
                        # Take the innermost font tag
                        inner_font = font_tags[-1]
                        price = inner_font.get_text().strip()
                    else:
                        # Just get the text from whatever element we found
                        price = price_tag.get_text().strip()
                else:
                    # Fallback to other common price selectors
                    price_tag = element.select_one('.price, .amount, .price-container, .product-price')
                    if price_tag:
                        price = price_tag.get_text().strip()
                    else:
                        # Last resort - look for text containing currency symbols or 'lei'
                        for potential_tag in element.find_all(['span', 'div', 'p', 'bdi', 'font']):
                            text = potential_tag.get_text().strip()
                            if 'lei' in text.lower() or '₽' in text or '€' in text or '$' in text or '£' in text:
                                price = text
                                break
                        else:
                            price = "N/A"
                
                # Clean up price (remove currency symbols, etc.)
                if price != "N/A":
                    # Remove all non-numeric characters except for decimal points
                    price = re.sub(r'[^\d.,]', '', price).strip()
                    # Make sure we don't have empty price after cleanup
                    if not price:
                        price = "N/A"
                
                # Log the price extraction without flooding logs
                # Skip warnings for menu items that don't typically have prices
                if price == "N/A":
                    # Only log warnings for non-menu items to avoid console spam
                    menu_items = ["pizza", "pasta", "bors", "ciorba", "mici", "sarmale", "italian", "carbonara"]
                    if not any(item in title.lower() for item in menu_items):
                        logger.warning(f"Could not extract price for product: {title}")
                else:
                    logger.info(f"Extracted price: {price} for product: {title}")
                
                # Get image if available
                img = element.find('img')
                img_url = img['src'] if img and 'src' in img.attrs else ""
                
                # Extract short description if available
                desc_element = element.select_one('.product-short-description')
                description = desc_element.get_text().strip() if desc_element else ""
                
                products.append({
                    'name': title,
                    'url': url,
                    'price': price,
                    'category': category_name,
                    'image_url': img_url,
                    'description': description
                })
            except Exception as e:
                logger.error(f"Error processing product in {category_name}: {e}")
                continue
        
        # Check if there are pagination links
        pagination = soup.select('.page-numbers')
        next_page = None
        for page in pagination:
            if page.get_text().strip() == '→' or page.get_text().strip() == 'Next':
                next_page = page['href']
                break
                
        # If there's a next page, recursively scrape it and extend products
        if next_page:
            logger.info(f"Scraping next page for {category_name}: {next_page}")
            # Avoid too deep recursion
            time.sleep(2)  # Be extra respectful with pagination
            next_page_products = self.scrape_products(next_page, category_name)
            products.extend(next_page_products)
        
        return products
    
    def scrape_product_details(self, product_url: str) -> Dict[str, Any]:
        """
        Scrape detailed information from a product page
        
        Args:
            product_url: URL of the product detail page
            
        Returns:
            Dictionary with detailed product information
        """
        html = self.get_page(product_url)
        if not html:
            logger.error(f"Failed to get product detail page: {product_url}")
            return {}
            
        soup = BeautifulSoup(html, 'html.parser')
        details = {}
        
        try:
            # Product title
            title_element = soup.select_one('.product_title')
            details['title'] = title_element.get_text().strip() if title_element else "Unknown Product"
            
            # Price
            price_element = soup.select_one('.price')
            details['price'] = price_element.get_text().strip() if price_element else "Price not available"
            
            # Description
            short_desc = soup.select_one('.woocommerce-product-details__short-description')
            details['short_description'] = short_desc.get_text().strip() if short_desc else ""
            
            long_desc = soup.select_one('#tab-description')
            details['description'] = long_desc.get_text().strip() if long_desc else ""
            
            # Main image
            img = soup.select_one('.woocommerce-product-gallery__image img')
            details['image_url'] = img['src'] if img and 'src' in img.attrs else ""
            
            # Additional images
            gallery_images = soup.select('.woocommerce-product-gallery__image img')
            details['gallery_images'] = [img['src'] for img in gallery_images if 'src' in img.attrs][1:]  # Skip first (main) image
            
            # Extract attributes/specifications
            attributes = {}
            attr_rows = soup.select('.woocommerce-product-attributes-item')
            for row in attr_rows:
                label = row.select_one('.woocommerce-product-attributes-item__label')
                value = row.select_one('.woocommerce-product-attributes-item__value')
                if label and value:
                    attr_name = label.get_text().strip().rstrip(':')
                    attr_value = value.get_text().strip()
                    attributes[attr_name] = attr_value
            
            details['attributes'] = attributes
            
            # Extract categories
            categories = []
            cat_links = soup.select('.posted_in a')
            for cat in cat_links:
                categories.append(cat.get_text().strip())
            
            details['categories'] = categories
            
            # Reviews if available
            reviews = []
            review_elements = soup.select('.comment_container')
            for rev in review_elements:
                author = rev.select_one('.woocommerce-review__author')
                date = rev.select_one('.woocommerce-review__published-date')
                text = rev.select_one('.description p')
                rating = rev.select_one('.star-rating')
                
                if author and text:
                    reviews.append({
                        'author': author.get_text().strip(),
                        'date': date.get_text().strip() if date else "",
                        'text': text.get_text().strip(),
                        'rating': rating['aria-label'] if rating and 'aria-label' in rating.attrs else ""
                    })
            
            details['reviews'] = reviews
            
        except Exception as e:
            logger.error(f"Error processing product detail page {product_url}: {e}")
        
        return details
    
    def _load_existing_data(self, filename: str) -> List[Dict]:
        """
        Load existing scraped data from a file if it exists
        
        Args:
            filename: Name of the file to load
            
        Returns:
            List of product dictionaries or empty list if file doesn't exist
        """
        file_path = os.path.join(self.data_dir, filename)
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading existing data from {filename}: {e}")
        return []
    
    def _merge_product_data(self, existing_data: List[Dict], new_data: List[Dict]) -> List[Dict]:
        """
        Merge existing product data with new scraped data
        
        Args:
            existing_data: Previously scraped products
            new_data: Newly scraped products
            
        Returns:
            Merged product list with new data taking precedence
        """
        # Create a lookup dictionary of existing products by URL
        existing_by_url = {product.get('url', ''): product for product in existing_data if 'url' in product}
        
        # Start with a copy of the new data
        merged_data = list(new_data)
        
        # Track URLs we've already processed
        processed_urls = set(product.get('url', '') for product in new_data if 'url' in product)
        
        # Add back any products that weren't in the new scrape
        for url, product in existing_by_url.items():
            if url and url not in processed_urls:
                merged_data.append(product)
        
        # Log the merge statistics
        logger.info(f"Merged {len(existing_data)} existing products with {len(new_data)} new products resulting in {len(merged_data)} total products")
        
        return merged_data
        
    async def run_scraper(self) -> Dict[str, Any]:
        """
        Main method to run the scraping process
        
        Returns:
            Dictionary with statistics about the scraping process
        """
        start_time = datetime.now()
        logger.info(f"Starting scrape at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        stats = {
            'start_time': start_time.isoformat(),
            'categories_count': 0,
            'products_count': 0,
            'errors': 0
        }
        
        try:
            # First check if the website is accessible
            test_html = self.get_page(self.base_url)
            if not test_html:
                logger.warning("Cannot access the website. Will use existing data if available.")
                stats['error_message'] = "Website not accessible - using cached data"
                
                # Check if we have existing data
                all_products_path = os.path.join(self.data_dir, "all_products.json")
                if os.path.exists(all_products_path):
                    try:
                        with open(all_products_path, 'r', encoding='utf-8') as f:
                            existing_data = json.load(f)
                            
                        logger.info(f"Using existing data with {len(existing_data)} products")
                        
                        # Update stats and return existing data
                        stats['products_count'] = len(existing_data)
                        stats['categories_count'] = len(self._load_existing_data("categories.json"))
                        stats['using_cached_data'] = True
                        stats['end_time'] = datetime.now().isoformat()
                        
                        # Save metadata
                        with open(os.path.join(self.data_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                            json.dump(stats, f, ensure_ascii=False, indent=2)
                            
                        return stats
                    except Exception as e:
                        logger.error(f"Error loading existing data: {e}")
                        
                logger.error("No existing data available. Cannot proceed with scraping.")
                return stats
                
            # Get categories
            categories = self.scrape_categories()
            stats['categories_count'] = len(categories)
            
            all_products = []
            
            # Get products for each category
            for category in categories:
                try:
                    logger.info(f"Scraping category: {category['name']}")
                    products = self.scrape_products(category['url'], category['name'])
                    
                    # Load existing data for this category (if any)
                    category_filename = category['name'].lower().replace(' ', '_').replace('-', '_')
                    category_file_path = os.path.join(self.data_dir, f"{category_filename}.json")
                    existing_cat_products = self._load_existing_data(f"{category_filename}.json")
                    
                    # Merge with new data
                    merged_products = self._merge_product_data(existing_cat_products, products)
                    
                    # Create a backup of the existing file if it exists
                    if os.path.exists(category_file_path):
                        backup_dir = os.path.join(self.data_dir, "backups")
                        os.makedirs(backup_dir, exist_ok=True)
                        backup_file = os.path.join(backup_dir, f"{category_filename}_{start_time.strftime('%Y%m%d_%H%M%S')}.json")
                        try:
                            shutil.copy2(category_file_path, backup_file)
                            logger.info(f"Created backup of {category_filename}.json")
                        except Exception as e:
                            logger.warning(f"Failed to create backup of {category_filename}.json: {e}")
                    
                    # Save updated category products
                    with open(category_file_path, 'w', encoding='utf-8') as f:
                        json.dump(merged_products, f, ensure_ascii=False, indent=2)
                    
                    # Add to the all_products collection
                    all_products.extend(merged_products)
                    
                    # For a limited set of products, get detailed information
                    # Only get details for the first 5 products per category to be respectful
                    detailed_products = []
                    for idx, product in enumerate(products[:5]):
                        try:
                            if idx >= 5:
                                break
                            logger.info(f"Scraping details for product: {product['name']}")
                            details = self.scrape_product_details(product['url'])
                            # Merge the basic product info with details
                            detailed_product = {**product, **details}
                            detailed_products.append(detailed_product)
                            # Be extra careful with detailed pages
                            time.sleep(3)
                        except Exception as e:
                            logger.error(f"Error scraping product details: {e}")
                            stats['errors'] += 1
                    
                    # Save detailed products for this category
                    if detailed_products:
                        with open(os.path.join(self.data_dir, f"{category_filename}_detailed.json"), 'w', encoding='utf-8') as f:
                            json.dump(detailed_products, f, ensure_ascii=False, indent=2)
                    
                except Exception as e:
                    logger.error(f"Error processing category {category['name']}: {e}")
                    stats['errors'] += 1
                
            # Load existing all_products data (if any)
            all_products_path = os.path.join(self.data_dir, "all_products.json")
            existing_all_products = self._load_existing_data("all_products.json")
            
            # Merge with new data
            merged_all_products = self._merge_product_data(existing_all_products, all_products)
            
            # Create a backup of the existing all_products file if it exists
            if os.path.exists(all_products_path):
                backup_dir = os.path.join(self.data_dir, "backups")
                os.makedirs(backup_dir, exist_ok=True)
                backup_file = os.path.join(backup_dir, f"all_products_{start_time.strftime('%Y%m%d_%H%M%S')}.json")
                try:
                    shutil.copy2(all_products_path, backup_file)
                    logger.info(f"Created backup of all_products.json")
                except Exception as e:
                    logger.warning(f"Failed to create backup of all_products.json: {e}")
            
            # Save updated all_products
            with open(all_products_path, 'w', encoding='utf-8') as f:
                json.dump(merged_all_products, f, ensure_ascii=False, indent=2)
                
            stats['products_count'] = len(merged_all_products)
            
            # Save metadata including timestamps and counts
            end_time = datetime.now()
            stats['end_time'] = end_time.isoformat()
            stats['duration_seconds'] = (end_time - start_time).total_seconds()
            
            with open(os.path.join(self.data_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)
                
            logger.info(f"Scraping completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"Total products scraped: {len(all_products)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"Error in scraper main process: {e}")
            stats['errors'] += 1
            stats['error_message'] = str(e)
            return stats

# Helper function to run the scraper as a scheduled task
async def run_scheduled_scraper():
    """Run the scraper and return its results"""
    scraper = VogoScraper()
    result = await scraper.run_scraper()
    return result

# For command-line execution
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the scraper
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_scheduled_scraper())
    print(f"Scraping completed with {result['products_count']} products from {result['categories_count']} categories.")
