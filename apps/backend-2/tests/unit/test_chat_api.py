import pytest
from fastapi.testclient import TestClient
import json
from unittest.mock import patch
from main import app

# Use the test client fixture
client = TestClient(app)

def test_process_message(monkeypatch):
    """Test the chat message processing endpoint"""
    # Mock RAG engine's generate_response method
    async def mock_generate_response(*args, **kwargs):
        return {
            "response": "I can help you with mall delivery in Vaslui!",
            "products": [
                {
                    "id": 1,
                    "name": "Vaslui - Proxima Shopping Center", 
                    "price": "10.00"
                }
            ]
        }
    
    # Apply the monkeypatch
    with patch('src.rag.engine.RAGEngine.generate_response', side_effect=mock_generate_response):
        # Make the request to the endpoint
        response = client.post(
            "/chat/message",
            json={"message": "I need mall delivery in Vaslui"}
        )
        
        # Assert the response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "products" in data
        assert data["response"] == "I can help you with mall delivery in Vaslui!"
        assert len(data["products"]) == 1
        assert data["products"][0]["name"] == "Vaslui - Proxima Shopping Center"



def test_quick_response():
    """Test the quick response endpoint"""
    response = client.get("/chat/quick-responses")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for item in data:
        assert "text" in item
        assert "id" in item