import os
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from ..rag.engine import RAGEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize API router
chat_router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize RAG engine
rag_engine = RAGEngine()

# Pydantic models for request/response validation
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    products: list

class VoiceResponse(BaseModel):
    transcription: Optional[str]
    response: str
    products: list

# Initialize RAG engine on module import
success = rag_engine.initialize()
if not success:
    logger.error("Failed to initialize RAG engine")

@chat_router.post("/message", response_model=ChatResponse)
async def process_message(request: ChatRequest) -> Dict[str, Any]:
    """Process a text chat message and return a response with relevant products.
    
    Args:
        request: ChatRequest object containing the user's message
        
    Returns:
        Dictionary containing the response text and relevant products
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        if not request.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
            
        # Add a timeout to prevent hanging
        try:
            result = await rag_engine.generate_response(request.message)
            return result
        except Exception as timeout_error:
            logger.error(f"Timeout or error generating response: {str(timeout_error)}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                "products": []
            }
            
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request"
        )

@chat_router.post("/voice", response_model=VoiceResponse)
async def process_voice(file: UploadFile = File(...)) -> Dict[str, Any]:
    """Process a voice message and return a response with transcription and relevant products.
    
    Args:
        file: Audio file upload (supports various formats including wav, mp3, etc.)
        
    Returns:
        Dictionary containing transcription, response text, and relevant products
        
    Raises:
        HTTPException: If there's an error processing the request
    """
    try:
        # Read the audio file
        audio_data = await file.read()
        if not audio_data:
            raise HTTPException(status_code=400, detail="Empty audio file")
            
        # Process the voice request with timeout handling
        try:
            result = await rag_engine.process_voice_request(audio_data)
            return result
        except Exception as timeout_error:
            logger.error(f"Timeout or error processing voice: {str(timeout_error)}")
            return {
                "transcription": "",
                "response": "I apologize, but I'm having trouble processing your voice message right now. Please try again.",
                "products": []
            }
            
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your voice message"
        )

@chat_router.get("/health")
async def health_check() -> Dict[str, str]:
    """Simple health check endpoint.
    
    Returns:
        Dictionary with status message
    """
    return {"status": "healthy"}
