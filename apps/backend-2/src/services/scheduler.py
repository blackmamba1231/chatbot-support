import asyncio
import logging
import time
from datetime import datetime
import os
import json
from .scraper import run_scheduled_scraper

logger = logging.getLogger(__name__)

class ScraperScheduler:
    """
    Scheduler for running the web scraper at regular intervals.
    Designed to run once daily to update the local knowledge base.
    """
    def __init__(self, hour=3, minute=0, data_dir=None):
        """
        Initialize the scheduler
        
        Args:
            hour: Hour of the day to run (0-23)
            minute: Minute of the hour to run (0-59)
            data_dir: Directory to store scraped data
        """
        self.hour = hour
        self.minute = minute
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "scraped_data")
        else:
            self.data_dir = data_dir
            
        # Create data directory if it doesn't exist
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            logger.info(f"Created data directory at {self.data_dir}")
            
        # Initialize last run time
        self.last_run_time = self._get_last_run_time()
        
    def _get_last_run_time(self):
        """Get the last time the scraper was run from metadata"""
        metadata_file = os.path.join(self.data_dir, "metadata.json")
        if os.path.exists(metadata_file):
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                if 'end_time' in metadata:
                    return datetime.fromisoformat(metadata['end_time'])
            except Exception as e:
                logger.error(f"Error reading metadata: {e}")
        return None
        
    def _should_run_now(self):
        """Check if the scraper should be run now"""
        now = datetime.now()
        
        # If it's the first run or it hasn't run today and it's after the scheduled time
        if (self.last_run_time is None or 
            self.last_run_time.date() < now.date() and 
            now.hour >= self.hour and now.minute >= self.minute):
            return True
        return False
    
    async def run_once(self):
        """Run the scraper once"""
        try:
            logger.info("Running scheduled scraping task")
            
            # Verify site accessibility before running the full scrape
            import requests
            try:
                response = requests.get("https://vogo.family", timeout=10)
                if response.status_code != 200:
                    logger.warning(f"Website returned status code {response.status_code}, scraping may fail")
            except Exception as e:
                logger.warning(f"Could not access website: {e}. Will still attempt to scrape but may fail.")
            
            result = await run_scheduled_scraper()
            
            # If we successfully scraped anything, update the last run time
            if result.get('products_count', 0) > 0 or result.get('categories_count', 0) > 0:
                self.last_run_time = datetime.now()
                logger.info(f"Scheduled scraping completed with {result.get('products_count', 0)} products from {result.get('categories_count', 0)} categories")
            else:
                logger.warning("Scraping completed but no products or categories were found")
                
            return result
        except Exception as e:
            logger.error(f"Error in scheduled scraping: {e}")
            return {"error": str(e)}
    
    async def start(self):
        """Start the scheduler loop"""
        logger.info(f"Scheduler started. Will run scraper job daily at {self.hour:02d}:{self.minute:02d}")
        
        # Run immediately on startup if never run before
        if self.last_run_time is None:
            await self.run_once()
        
        while True:
            try:
                if self._should_run_now():
                    await self.run_once()
                
                # Sleep for 5 minutes before checking again
                await asyncio.sleep(300)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Sleep a bit on error

# For command-line execution
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the scheduler
    scheduler = ScraperScheduler()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(scheduler.start())
