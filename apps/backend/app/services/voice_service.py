import os
import logging
import tempfile
import openai
from typing import Optional

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for handling voice transcription using OpenAI's Whisper API"""
    
    def __init__(self):
        """Initialize the voice service"""
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        
        # Initialize OpenAI client
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized for voice service")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client for voice service: {str(e)}")
            self.client = None
    
    def transcribe_audio(self, audio_data: bytes, language: str = "en") -> Optional[str]:
        """
        Transcribe audio data to text using OpenAI's Whisper API
        
        Args:
            audio_data: Binary audio data
            language: Language code (default: 'en' for English)
            
        Returns:
            Transcribed text or None if transcription failed
        """
        if not self.client:
            logger.error("OpenAI client not initialized for voice service")
            return None
            
        try:
            # Save audio data to a temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file_path = temp_file.name
                temp_file.write(audio_data)
            
            # Transcribe audio using Whisper API
            with open(temp_file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language
                )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            # Return transcribed text
            return response.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            # Clean up temporary file if it exists
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
            return None
    
    def is_available(self) -> bool:
        """Check if the voice service is available"""
        return self.client is not None
