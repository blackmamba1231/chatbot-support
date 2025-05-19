from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
import httpx
import os
import logging
import tempfile
from src.api.chat import ChatRequest, ChatResponse
from src.rag.engine import RAGEngine
from src.services.woocommerce_service import WooCommerceService

logger = logging.getLogger(__name__)

# Define router
voice_router = APIRouter()

async def transcribe_audio(file_path: str, language: Optional[str] = None) -> str:
    """
    Transcribe audio file using OpenAI Whisper API.
    
    Args:
        file_path: Path to audio file
        language: Optional language hint (en, ro, etc.)
        
    Returns:
        Transcribed text
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OpenAI API key not set. Cannot transcribe audio.")
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        with open(file_path, "rb") as audio_file:
            # Prepare headers with API key
            headers = {
                "Authorization": f"Bearer {api_key}"
            }
            
            # Prepare form data
            form_data = {
                "model": "whisper-1",
            }
            
            if language:
                form_data["language"] = language
            
            files = {
                "file": audio_file
            }
            
            # Call Whisper API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers=headers,
                    data=form_data,
                    files=files,
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Whisper API error: {response.text}")
                    raise HTTPException(status_code=response.status_code, detail=f"Transcription failed: {response.text}")
                
                result = response.json()
                return result.get("text", "")
                
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing audio: {str(e)}")

@voice_router.post("/transcribe")
async def process_voice(
    audio: UploadFile = File(...),
    user_id: str = Form(...),
    session_id: str = Form(...)
):
    # Log received data
    logger.info(f"Received audio file: {audio.filename}, content_type: {audio.content_type}")
    logger.info(f"User ID: {user_id}, Session ID: {session_id}")
    
    try:
        # Save uploaded file to temp directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(await audio.read())
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio
            transcribed_text = await transcribe_audio(temp_file_path)
            
            # Process transcribed text with RAG engine
            rag_engine = RAGEngine()
            result = await rag_engine.generate_response(transcribed_text)
            
            return {
                "response": result["response"],
                "transcription": transcribed_text,
                "products": result.get("products", [])
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    """
    Process voice message:
    1. Receive audio file
    2. Transcribe using Whisper API
    3. Process transcribed text using RAG engine
    4. Return AI response
    
    Args:
        audio: Audio file (mp3, wav, etc.)
        language: Optional language hint (en, ro, etc.)
        user_id: Optional user identifier
        session_id: Optional session identifier
        
    Returns:
        AI response with relevant product recommendations
    """
    try:
        # Save uploaded file to temp directory
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(await audio.read())
            temp_file_path = temp_file.name
        
        try:
            # Transcribe audio
            transcribed_text = await transcribe_audio(temp_file_path, language)
            
            # Remove temp file
            os.unlink(temp_file_path)
            
            if not transcribed_text:
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Could not transcribe audio. Please try again with a clearer recording."}
                )
            
            # Create chat request from transcribed text
            chat_request = ChatRequest(
                message=transcribed_text,
                user_id=user_id,
                session_id=session_id
            )
            
            # Process transcribed text with RAG engine
            result = await rag_engine.generate_response(chat_request.message)
            
            return ChatResponse(
                response=result["response"],
                products=result.get("products"),
                transcription=transcribed_text  # Include original transcription
            )
            
        except Exception as e:
            # Ensure temp file is deleted even if an error occurs
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            raise
            
    except Exception as e:
        logger.error(f"Error processing voice message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing voice message: {str(e)}")
