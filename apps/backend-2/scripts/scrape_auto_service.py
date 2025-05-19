import requests
from bs4 import BeautifulSoup
import json
import os

def scrape_auto_service():
    url = "https://vogo.family/product/auto-service/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    try:
        # Get the product title
        title_elem = soup.find('h1', class_='product_title')
        title = title_elem.text.strip() if title_elem else "Auto Service"
        
        # Get the product description
        desc_elem = soup.find('div', class_='woocommerce-product-details__short-description')
        description = desc_elem.text.strip() if desc_elem else ""
        
        # Get the price if available
        price_elem = soup.find('p', class_='price')
        if price_elem:
            amount_elem = price_elem.find('span', class_='amount')
            price = amount_elem.text.strip() if amount_elem else "Contact for price"
        else:
            price = "Contact for price"
        
        # Create the service data structure
        service_data = {
            "title": title,
            "description": description,
            "price": price,
            "category": "Auto Service",
            "url": url
        }
        
        # Ensure the scraped_data directory exists
        os.makedirs("scraped_data", exist_ok=True)
        
        # Save to JSON file
        output_path = os.path.join("scraped_data", "auto_service.json")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(service_data, f, indent=2, ensure_ascii=False)
            
        print(f"Successfully scraped auto service data and saved to {output_path}")
        return service_data
        
    except Exception as e:
        print(f"Error scraping auto service data: {str(e)}")
        return None

if __name__ == "__main__":
    scrape_auto_service()
