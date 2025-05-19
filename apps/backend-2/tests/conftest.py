import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

# Add the root directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import app and dependencies
from main import app
from src.services.woocommerce_service import WooCommerceService
from src.rag.engine import RAGEngine


@pytest.fixture
def client():
    """
    Create a test client for the FastAPI application
    """
    return TestClient(app)


@pytest.fixture
def mock_woocommerce_service():
    """
    Create a mock WooCommerceService for testing
    """
    mock_service = Mock(spec=WooCommerceService)
    
    # Mock common methods
    async def mock_get_products(*args, **kwargs):
        return [
            {
                "id": 1,
                "name": "Vaslui - Proxima Shopping Center",
                "price": "10.00",
                "regular_price": "10.00",
                "description": "Mall delivery service in Vaslui",
                "short_description": "Fast delivery",
                "categories": [{"id": 223, "name": "Mall Delivery", "slug": "mall-delivery"}],
                "images": [{"src": "https://example.com/image.jpg"}],
                "attributes": []
            }
        ]
    
    async def mock_get_categories(*args, **kwargs):
        return [
            {
                "id": 223,
                "name": "Mall Delivery",
                "slug": "mall-delivery"
            }
        ]
    
    async def mock_create_order(*args, **kwargs):
        return {
            "id": 100,
            "status": "processing",
            "total": "10.00"
        }
    
    mock_service.get_products.side_effect = mock_get_products
    mock_service.get_categories.side_effect = mock_get_categories
    mock_service.create_order.side_effect = mock_create_order
    
    return mock_service


@pytest.fixture
def mock_rag_engine():
    """
    Create a mock RAGEngine for testing
    """
    mock_engine = Mock(spec=RAGEngine)
    
    async def mock_generate_response(*args, **kwargs):
        return {
            "response": "I can help you with mall delivery services!",
            "products": [
                {
                    "id": 1,
                    "name": "Vaslui - Proxima Shopping Center",
                    "price": "10.00",
                    "description": "Mall delivery service in Vaslui"
                }
            ]
        }
    
    mock_engine.generate_response.side_effect = mock_generate_response
    
    return mock_engine
