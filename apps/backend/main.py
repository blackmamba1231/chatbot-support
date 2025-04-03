from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import os
from app.rag.engine import RAGEngine

app = FastAPI(title="Vogo.Family Chatbot API")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG engine
rag_engine = RAGEngine()

class Location(BaseModel):
    latitude: float
    longitude: float

class ChatMessage(BaseModel):
    message: str
    language: Optional[str] = "en"
    voice_input: Optional[bool] = False
    conversation_id: Optional[str] = None
    location: Optional[Location] = None
    conversation_state: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    confidence: float
    requires_human: bool
    services: Optional[List[str]] = None
    expecting: Optional[str] = None
    action: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None

@app.get("/")
async def root():
    return {"status": "ok", "message": "Vogo.Family Chatbot API is running"}

@app.post("/chat", response_model=ChatResponse)
async def chat(chat_message: ChatMessage):
    try:
        # Process the message through the RAG engine
        result = await rag_engine.process_query(
            query=chat_message.message,
            language=chat_message.language,
            location=chat_message.location.dict() if chat_message.location else None,
            conversation_state=chat_message.conversation_state or {}
        )
        
        return ChatResponse(
            response=result["response"],
            confidence=result["confidence"],
            requires_human=result["requires_human"],
            services=result.get("services"),
            expecting=result.get("expecting"),
            action=result.get("action"),
            date=result.get("date"),
            time=result.get("time")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Endpoint to simulate calendar integration
@app.post("/calendar/add")
async def add_to_calendar(data: Dict[str, Any]):
    try:
        # In a real implementation, this would connect to a calendar API
        # For now, we'll just return success
        return {
            "status": "success",
            "message": "Event added to calendar",
            "event_details": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to simulate email sending
@app.post("/email/send")
async def send_email(data: Dict[str, Any]):
    try:
        # In a real implementation, this would connect to an email service
        # For now, we'll just return success
        return {
            "status": "success",
            "message": "Email sent successfully",
            "email_details": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to request human operator
@app.post("/operator/request")
async def request_operator(data: Dict[str, Any]):
    try:
        # In a real implementation, this would create a ticket in a CRM system
        # For now, we'll just return success
        return {
            "status": "success",
            "message": "Human operator request received",
            "ticket_id": "TKT-" + str(hash(str(data)))[1:8]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
