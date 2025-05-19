# Vogo.Family AI-Powered Chatbot Backend

This backend service provides API endpoints for the Vogo.Family AI-powered chatbot, which integrates with WooCommerce to fetch product data from various categories including mall delivery services, pet supplies, and restaurant services.

## Features

- AI-powered chat responses using RAG (Retrieval-Augmented Generation)
- WooCommerce API integration for product data
- Product search and filtering by category
- Order creation and management
- Location-based service recommendations
- In-memory caching for improved performance

## Setup and Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `sample.env`:
   ```
   cp sample.env .env
   ```

5. Add your OpenAI API key to the `.env` file:
   ```
   OPENAI_API_KEY=your_key_here
   ```

## Running the Server

Start the server using Uvicorn:

```
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access the interactive API documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Available Endpoints

### Chat

- `POST /chat/message` - Send a chat message and get AI response with product recommendations

### Products

- `GET /products` - Get all products with optional filtering
- `GET /products/{product_id}` - Get a specific product by ID
- `GET /products/categories` - Get all product categories
- `GET /products/mall-delivery` - Get mall delivery products
- `GET /products/restaurants` - Get restaurant products
- `GET /products/pet-supplies` - Get pet products
- `GET /products/locations` - Get available locations

### Orders

- `POST /orders` - Create a new order
- `GET /orders` - Get all orders
- `GET /orders/{order_id}` - Get a specific order

## Integration with Frontend

This backend is designed to work with the chatbot frontend. The frontend can communicate with this backend through the provided API endpoints.
