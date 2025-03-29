# Vogo.Family Chatbot Backend

This is the backend service for the Vogo.Family AI-powered chatbot. It implements a Retrieval-Augmented Generation (RAG) system to provide accurate and contextually relevant responses.

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and fill in your configuration:
```bash
cp .env.example .env
```

4. Run the development server:
```bash
python main.py
```

The server will start at `http://localhost:8000`

## API Endpoints

- `GET /`: Health check endpoint
- `POST /chat`: Main chat endpoint
  - Accepts JSON payload with:
    - `message`: User's message
    - `language`: Language code (default: "en")
    - `voice_input`: Boolean flag for voice input

## Project Structure

```
backend/
├── app/
│   ├── rag/
│   │   ├── engine.py    # RAG implementation
│   │   └── __init__.py
│   └── __init__.py
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
└── .env.example        # Environment variables template
```

## First Milestone Features

- [x] Basic FastAPI setup
- [x] RAG system skeleton
- [x] API endpoint structure
- [ ] OpenAI integration
- [ ] Basic error handling
- [ ] CORS configuration
