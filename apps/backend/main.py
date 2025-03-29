from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

app = FastAPI(title="Vogo.Family Chatbot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "en"
    voice_input: Optional[bool] = False

@app.get("/")
async def root():
    return {"status": "ok", "message": "Vogo.Family Chatbot API is running"}

@app.post("/chat")
async def chat(chat_message: ChatMessage):
    try:
        # TODO: Implement RAG system integration
        # For now, return a mock response
        return {
            "response": "This is a demo response. RAG system integration pending.",
            "confidence": 0.9,
            "requires_human": False
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
