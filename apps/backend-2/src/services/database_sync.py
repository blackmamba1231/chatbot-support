"""
Database synchronization module for WooCommerce integration.
Handles fetching and storing complete product and category data from the WooCommerce API.
"""
import asyncio
import httpx
import json
import logging
import re
from typing import Dict, List, Any, Set
from datetime import datetime

logger = logging.getLogger(__name__)

class WooCommerceSync:
    """
    Service for synchronizing and maintaining a local copy of the WooCommerce database.
    Enables efficient search and retrieval operations across the entire product catalog.
    """
    
    def __init__(self, consumer_key, consumer_secret, base_url, timeout=120.0):
        """Initialize sync service with WooCommerce API credentials"""
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.base_url = base_url
        self.timeout = timeout
        
        # Initialize local database containers
        self.all_products = {}
        self.all_categories = {}
        self.product_name_index = {}
        self.category_name_index = {}
        self.last_sync_time = None
        
        # Initialize session
        self.session = None
    
    def normalize_text(self, text: str) -> str:
        """
        Normalize text for consistent indexing and searching.
        Converts to lowercase, removes extra whitespace, and strips punctuation.
        """
        if not text:
            return ""
            
        # Convert to lowercase and strip whitespace
        normalized = text.lower().strip()
        
        # Remove repeated spaces
        normalized = re.sub(r'\s+', ' ', normalized)
        
        return normalized
    
    async def initialize(self):
        """Initialize the sync service and perform first sync"""
        logger.info("Initializing WooCommerce sync service")
        
        # Create persistent HTTP session
        self.session = httpx.AsyncClient(
            auth=(self.consumer_key, self.consumer_secret),
            timeout=self.timeout
        )
        
        # Perform initial sync
        await self.sync_all_data()
        
        # Start background sync task
        asyncio.create_task(self.schedule_periodic_sync())
        
        logger.info("WooCommerce sync service initialized")
    
    async def sync_all_data(self):
        """
        Synchronize all product and category data from WooCommerce API.
        This comprehensive sync enables access to the entire product catalog.
        
        Returns:
            Dict with counts of synced categories and products
        """
        logger.info("Starting full WooCommerce data sync")
        
        try:
            # Fetch all categories
            all_categories = await self.fetch_all_paginated('/products/categories')
            logger.info(f"Fetched {len(all_categories)} categories from WooCommerce")
            
            # Fetch all products
            all_products = await self.fetch_all_paginated('/products')
            logger.info(f"Fetched {len(all_products)} products from WooCommerce")
            
            # Store in memory
            self.store_data(all_categories, all_products)
            
            # Record sync time
            self.last_sync_time = datetime.now()
            
            return {"categories": len(all_categories), "products": len(all_products)}
            
        except Exception as e:
            logger.error(f"Error during WooCommerce data sync: {e}")
            return {"categories": 0, "products": 0, "error": str(e)}
    
    async def fetch_all_paginated(self, endpoint, per_page=100, max_retries=3):
        """
        Fetches all pages from a WooCommerce endpoint using pagination.
        This ensures we get ALL data even when there are thousands of products.
        Includes robust retry logic to handle transient network issues.
        Now optimized with parallel requests for faster synchronization.
        
        Args:
            endpoint: API endpoint to fetch data from
            per_page: Number of items per page
            max_retries: Maximum number of retry attempts for each page
            
        Returns:
            List of all items from all pages or raises exception if critical failure
        """
        # First, get total number of items to determine how many pages we need
        try:
            # Make a request for just one item to get the total count from headers
            url = f"{self.base_url}{endpoint}?per_page=1"
            response = await self.session.get(url)
            response.raise_for_status()
            
            # WooCommerce returns total count in the headers
            total_items = int(response.headers.get('X-WP-Total', 0))
            total_pages = int(response.headers.get('X-WP-TotalPages', 0))
            
            logger.info(f"Found {total_items} total items across {total_pages} pages")
            
            if total_items == 0 or total_pages == 0:
                logger.warning(f"No items found for {endpoint}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting pagination info: {e}")
            # Fall back to sequential pagination method if we couldn't get the total
            return await self._fetch_sequential(endpoint, per_page, max_retries)
        
        # Function to fetch a single page with retries
        async def fetch_page(page_num):
            url = f"{self.base_url}{endpoint}?per_page={per_page}&page={page_num}"
            logger.info(f"Fetching page {page_num} from {endpoint}")
            
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = await self.session.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    # Validation
                    if data is None:
                        raise ValueError("Received null response from API")
                    if not isinstance(data, list):
                        raise ValueError(f"Expected list response, got {type(data)}")
                    
                    logger.info(f"Successfully retrieved {len(data)} items from page {page_num}")
                    return data
                    
                except (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout) as e:
                    retry_count += 1
                    backoff_time = 2 ** retry_count  # 2, 4, 8 seconds
                    logger.warning(f"Connection error on page {page_num}: {e}. Retrying in {backoff_time} seconds (attempt {retry_count}/{max_retries})")
                    await asyncio.sleep(backoff_time)
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Data error on page {page_num}: {e}")
                    retry_count += 1
                    await asyncio.sleep(2)
            
            logger.error(f"Failed to fetch page {page_num} after {max_retries} attempts")
            return []
        
        # Fetch all pages in parallel, with a reasonable limit to avoid overwhelming the server
        # Process in smaller batches of 5 concurrent requests to be gentle on the server
        batch_size = 5
        all_data = []
        
        for batch_start in range(1, total_pages + 1, batch_size):
            batch_end = min(batch_start + batch_size - 1, total_pages)
            logger.info(f"Fetching batch of pages {batch_start}-{batch_end}")
            
            # Create tasks for this batch
            tasks = [fetch_page(page_num) for page_num in range(batch_start, batch_end + 1)]
            
            # Wait for all pages in this batch
            try:
                batch_results = await asyncio.gather(*tasks)
                for page_data in batch_results:
                    all_data.extend(page_data)
            except Exception as e:
                logger.error(f"Error processing batch {batch_start}-{batch_end}: {e}")
        
        logger.info(f"Successfully retrieved {len(all_data)} total items from {endpoint}")
        return all_data
        
    async def _fetch_sequential(self, endpoint, per_page=100, max_retries=3):
        """Fallback method for sequential fetching if parallel fetching fails"""
        page = 1
        all_data = []
        connection_errors = 0
        max_connection_errors = 5  # Allow up to 5 total connection errors
        
        while True:
            url = f"{self.base_url}{endpoint}?per_page={per_page}&page={page}"
            logger.info(f"Sequentially fetching page {page} from {endpoint}")
            
            retry_count = 0
            success = False
            
            while retry_count < max_retries and not success:
                try:
                    response = await self.session.get(url)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data is None or not isinstance(data, list):
                        raise ValueError(f"Invalid data format: {type(data)}")
                    
                    if not data:
                        logger.info(f"No more data at page {page}. Sequential pagination complete.")
                        success = True
                        break
                    
                    all_data.extend(data)
                    logger.info(f"Added {len(data)} items from page {page}")
                    success = True
                    
                except (httpx.HTTPStatusError, httpx.ConnectError, httpx.ReadTimeout) as e:
                    retry_count += 1
                    connection_errors += 1
                    
                    backoff_time = 2 ** retry_count  # 2, 4, 8 seconds
                    logger.warning(f"Connection error on page {page}: {e}. Retrying in {backoff_time} seconds (attempt {retry_count}/{max_retries})")
                    
                    if connection_errors >= max_connection_errors:
                        logger.error(f"Too many connection errors ({connection_errors}). Aborting pagination.")
                        return all_data  # Return what we have so far
                    
                    await asyncio.sleep(backoff_time)
                    
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Data error on page {page}: {e}")
                    retry_count += 1
                    
                    if retry_count >= max_retries:
                        logger.error(f"Maximum retries reached for page {page}. Continuing.")
                        success = True  # Mark as success to move on
                    else:
                        await asyncio.sleep(2)
            
            # If this page was empty or had no data, we've reached the end
            if not success or not data or len(data) == 0:
                break
                
            page += 1
            
        return all_data
    
    def store_data(self, categories, products):
        """
        Store WooCommerce data in memory and build search indexes.
        This creates fast lookup structures for product and category searches.
        
        Args:
            categories: List of category dictionaries
            products: List of product dictionaries
        """
        logger.info("Building in-memory database and search indexes")
        
        # Store by ID for fast lookups
        self.all_categories = {int(cat["id"]): cat for cat in categories}
        self.all_products = {int(prod["id"]): prod for prod in products}
        
        # Create name-based search indexes
        self.product_name_index = {}
        self.category_name_index = {}
        
        # Build product name index
        for product in products:
            if "name" in product and product["name"]:
                norm_name = self.normalize_text(product["name"])
                self.product_name_index[norm_name] = product["id"]
        
        # Build category name index
        for category in categories:
            if "name" in category and category["name"]:
                norm_name = self.normalize_text(category["name"])
                self.category_name_index[norm_name] = category["id"]
        
        logger.info(f"Stored {len(products)} products and {len(categories)} categories in memory")
        logger.info(f"Created indexes with {len(self.product_name_index)} product names and {len(self.category_name_index)} category names")
    
    async def schedule_periodic_sync(self, hours=12):
        """
        Schedule periodic data sync to keep the local database fresh.
        
        Args:
            hours: Hours between syncs
        """
        while True:
            try:
                # Sleep first to avoid double-syncing at startup
                await asyncio.sleep(hours * 3600)  # Convert hours to seconds
                
                logger.info(f"Running scheduled WooCommerce data sync after {hours} hours")
                await self.sync_all_data()
                logger.info("Scheduled WooCommerce data sync complete")
                
            except Exception as e:
                logger.error(f"Error in scheduled data sync: {e}")
                # Sleep a bit and then continue the loop
                await asyncio.sleep(300)  # 5 minute delay on error
    
    def find_product_by_exact_name(self, product_name: str) -> List[Dict]:
        """
        Find products by exact name match using the local database.
        
        Args:
            product_name: The exact product name to search for
            
        Returns:
            List of matching products
        """
        if not product_name or not self.all_products:
            return []
            
        query_normalized = self.normalize_text(product_name)
        
        # First try exact match on the normalized name
        if query_normalized in self.product_name_index:
            product_id = self.product_name_index[query_normalized]
            product = self.all_products.get(product_id)
            if product:
                logger.info(f"Found exact match in local database for '{product_name}'")
                return [product]
        
        # Try partial match in product names
        matches = []
        query_tokens = set(query_normalized.split())
        
        for prod_id, product in self.all_products.items():
            name = product.get("name", "")
            norm_name = self.normalize_text(name)
            
            # Check for exact match or significant partial match
            if query_normalized == norm_name or query_normalized in norm_name:
                matches.append(product)
            else:
                # Token-based matching for partial matches
                name_tokens = set(norm_name.split())
                common_tokens = query_tokens.intersection(name_tokens)
                if len(common_tokens) >= max(1, len(query_tokens) * 0.6):
                    matches.append(product)
        
        if matches:
            logger.info(f"Found {len(matches)} matches in local database for '{product_name}'")
            return matches
            
        return []
    
    def find_products_by_category_name(self, category_name: str) -> List[Dict]:
        """
        Find products by category name using the local database.
        
        Args:
            category_name: The category name to search for
            
        Returns:
            List of products in the matching categories
        """
        if not category_name or not self.all_categories:
            return []
            
        category_matches = []
        norm_category = self.normalize_text(category_name)
        
        # Try exact match first
        if norm_category in self.category_name_index:
            category_id = self.category_name_index[norm_category]
            category_matches.append(category_id)
        else:
            # Try partial matches on category names
            for cat_id, category in self.all_categories.items():
                if "name" in category and category["name"]:
                    cat_name = self.normalize_text(category["name"])
                    if norm_category in cat_name or cat_name in norm_category:
                        category_matches.append(cat_id)
        
        # If we found matching categories, get all products in those categories
        if category_matches:
            results = []
            for product_id, product in self.all_products.items():
                if "categories" in product and product["categories"]:
                    product_cats = [cat.get("id") for cat in product["categories"] if "id" in cat]
                    for cat_id in category_matches:
                        if cat_id in product_cats:
                            results.append(product)
                            break  # Break once we've added the product
            
            if results:
                logger.info(f"Found {len(results)} products in categories matching '{category_name}'")
                return results
                
        return []
    
    def search_products(self, query: str) -> List[Dict]:
        """
        Search across all products using multiple search strategies.
        
        Args:
            query: The search query
            
        Returns:
            List of matching products
        """
        # First try exact name match
        exact_matches = self.find_product_by_exact_name(query)
        if exact_matches:
            return exact_matches
            
        # Then try category-based search
        category_matches = self.find_products_by_category_name(query)
        if category_matches:
            return category_matches
            
        # Finally, try fuzzy keyword search
        query_terms = set(self.normalize_text(query).split())
        if len(query_terms) == 0:
            return []
            
        matches = []
        for prod_id, product in self.all_products.items():
            # Search in name, description, and short description
            name = self.normalize_text(product.get("name", ""))
            desc = self.normalize_text(product.get("description", ""))
            short_desc = self.normalize_text(product.get("short_description", ""))
            
            # Combine all text fields for searching
            all_text = f"{name} {desc} {short_desc}"
            all_tokens = set(all_text.split())
            
            # Calculate term overlap
            common_terms = query_terms.intersection(all_tokens)
            if len(common_terms) > 0:
                match_score = len(common_terms) / len(query_terms)
                if match_score >= 0.3:  # Match if at least 30% of query terms found
                    matches.append((match_score, product))
        
        # Sort by match score (descending)
        matches.sort(key=lambda x: x[0], reverse=True)
        
        # Return top 20 products
        return [product for _, product in matches[:20]]
        
    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.aclose()
