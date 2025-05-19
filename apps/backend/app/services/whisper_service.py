import os
import tempfile
import logging
from typing import BinaryIO
from openai import OpenAI

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        """Initialize WhisperService with OpenAI API"""
        try:
            self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            logger.info("OpenAI client initialized for WhisperService")
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {str(e)}")
            raise

    async def transcribe_audio(self, audio_file: BinaryIO) -> str:
        """Transcribe audio using OpenAI's Whisper API"""
        try:
            # Create a temporary file to store the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_file.read())
                temp_path = temp_file.name

            # Transcribe using OpenAI's Whisper API
            with open(temp_path, "rb") as audio:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    language="en"
                )

            # Clean up the temporary file
            os.unlink(temp_path)
            
            return response.text

        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            # Clean up temporary file if it exists
            if 'temp_path' in locals():
                try:
                    os.unlink(temp_path)
                except:
                    pass
            raise
