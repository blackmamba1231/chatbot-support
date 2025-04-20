import whisper
import tempfile
import os
from typing import BinaryIO
import logging

logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        try:
            self.model = whisper.load_model("base")
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading Whisper model: {str(e)}")
            raise

    async def transcribe_audio(self, audio_file: BinaryIO) -> str:
        try:
            # Create a temporary file to store the audio
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                temp_file.write(audio_file.read())
                temp_path = temp_file.name

            # Transcribe the audio
            result = self.model.transcribe(temp_path)
            
            # Clean up the temporary file
            os.unlink(temp_path)
            
            return result["text"]
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            raise
