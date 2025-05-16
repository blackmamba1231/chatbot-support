# WooCommerce AI Assistant with Voice Integration

This AI-powered assistant integrates with your WooCommerce store to provide intelligent product discovery using natural language and voice commands. It includes both a CLI interface and a REST API server for frontend integration.

## Features

- **Complete WooCommerce Integration**: Fetches and displays both products AND categories from your store
- **Voice Input**: Speak commands and questions to interact with your WooCommerce store
- **Intent Detection**: AI-powered understanding of user queries
- **Product Discovery**: Intelligent retrieval of products based on categories and locations
- **Voice Output**: Text-to-speech responses for a hands-free experience
- **Sentiment Analysis**: Understanding of user sentiment to improve responses
- **Interactive Mode**: Chat-like interface for easy interaction

## Requirements

- Python 3.8+
- OpenAI API Key
- PyAudio (for voice recording)
- WooCommerce store with REST API access

## Installation

1. Install required packages:

```bash
pip install openai requests requests-oauthlib python-dotenv pyaudio
```

2. Set up your environment variables:

   - Copy `.env.example` to `.env`
   - Fill in your WooCommerce API credentials and OpenAI API key
   - The application will also attempt to use credentials from `apps/backend/.env` if local .env is not found

## Usage

### CLI Mode

Run the assistant in interactive mode:

```bash
python woocommerce_ai_assistant.py --interactive
```

**Fetch both products and categories**:

```bash
python woocommerce_ai_assistant.py --fetch-all
```

List all products:

```bash
python woocommerce_ai_assistant.py --list-products
```

### API Server Mode (for Frontend Integration)

Run the API server which provides REST endpoints for the frontend chatbot:

```bash
python api_server.py
```

This will start a FastAPI server on port 8000 (or the port specified in your .env file) with the following endpoints:

- `/chat` - Process user chat messages with AI intent detection
- `/api/ai-shopping/chat` - Alias for /chat (compatible with frontend)
- `/api/ai-shopping/search` - Search for products using natural language
- `/api/ai-shopping/mall-delivery` - Get mall delivery products by location
- `/api/ai-shopping/categories/{category_id}/products` - Get products by category
- `/api/mobile/mall-delivery/locations` - Get all available locations

The API server integrates all the AI capabilities (intent detection, voice, product fetching) with your WooCommerce store and serves them to the frontend.

List all categories:

```bash
python woocommerce_ai_assistant.py --list-categories
```

Get products from a specific category:

```bash
python woocommerce_ai_assistant.py --category-id 223  # Mall Delivery category
```

Process a text query:

```bash
python woocommerce_ai_assistant.py --text "Do you have any bio food products in Alba Iulia?"
```

## Voice Commands

In interactive mode, type `voice` to activate voice input. The assistant will:

1. Record your voice (speak clearly after the prompt)
2. Transcribe your speech using OpenAI's Whisper model
3. Process your request using intent detection
4. Find relevant products from your WooCommerce store
5. Generate a natural language response

## Category IDs

The system is set up to work with the following WooCommerce categories:

- Mall Delivery (ID: 223)
- Kids Activities (ID: 563)
- Bio Food (ID: 346)
- Antipasti (ID: 347)
- Pet Care (ID: 547)
- Allergies (ID: 548)

## Available Locations

The system supports these Romanian locations:

- Alba Iulia
- Arad
- Miercurea Ciuc
- Vaslui
- Târgu Mureș
- Suceava
- Târgu-Jiu

## Example Commands

- "Show me mall delivery services in Vaslui"
- "Do you have any bio food products?"
- "Tell me about kids activities in Alba Iulia"
- "What antipasti do you deliver in Arad?"
- "I'm looking for pet care products in Suceava"
