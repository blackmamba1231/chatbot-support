"""
Voice Service
This module handles voice input and output using OpenAI's speech APIs.
"""

import os
import tempfile
import logging
from typing import Optional, BinaryIO
import pyaudio
import wave
import time
import threading
from openai import OpenAI

logger = logging.getLogger(__name__)

class VoiceService:
    """Service for handling voice input and output"""
    
    def __init__(self, openai_client=None):
        """Initialize the voice service"""
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_client and not self.api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        self.client = openai_client or OpenAI(api_key=self.api_key)
        
        # Audio recording settings
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        self.chunk = 1024
        self.record_seconds = 5
        
        logger.info("Voice service initialized")
    
    def transcribe_audio_file(self, audio_file: BinaryIO) -> str:
        """
        Transcribe audio file using OpenAI's Whisper API
        
        Args:
            audio_file: Audio file opened in binary mode
            
        Returns:
            Transcription text
        """
        try:
            logger.info("Transcribing audio...")
            
            # Call OpenAI's speech-to-text API
            response = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
            
            transcription = response.text
            logger.info(f"Transcription complete: {transcription}")
            return transcription
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return "Sorry, I couldn't understand that audio."
    
    def text_to_speech(self, text: str, output_file: str = None) -> str:
        """
        Convert text to speech using OpenAI's TTS API
        
        Args:
            text: Text to convert to speech
            output_file: Optional path to save the audio file
            
        Returns:
            Path to the saved audio file
        """
        try:
            logger.info("Converting text to speech...")
            
            # If no output file is specified, create a temporary one
            if not output_file:
                temp_dir = tempfile.gettempdir()
                output_file = os.path.join(temp_dir, f"tts_{int(time.time())}.mp3")
            
            # Call OpenAI's text-to-speech API
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="alloy",
                input=text
            )
            
            # Save the audio to the output file
            response.stream_to_file(output_file)
            
            logger.info(f"Speech generated and saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error generating speech: {str(e)}")
            return None
    
    def record_audio(self, output_file: str = None, duration: int = None) -> str:
        """
        Record audio from microphone
        
        Args:
            output_file: Optional path to save the audio file
            duration: Recording duration in seconds (default: 5)
            
        Returns:
            Path to the saved audio file
        """
        try:
            # If no output file is specified, create a temporary one
            if not output_file:
                temp_dir = tempfile.gettempdir()
                output_file = os.path.join(temp_dir, f"recording_{int(time.time())}.wav")
            
            # Set duration
            record_seconds = duration or self.record_seconds
            
            logger.info(f"Recording audio for {record_seconds} seconds...")
            
            # Initialize PyAudio
            audio = pyaudio.PyAudio()
            
            # Open stream
            stream = audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk
            )
            
            print("🎤 Recording...")
            
            # Record audio
            frames = []
            for i in range(0, int(self.rate / self.chunk * record_seconds)):
                data = stream.read(self.chunk)
                frames.append(data)
            
            print("✅ Recording complete!")
            
            # Stop and close stream
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            # Save audio to file
            wf = wave.open(output_file, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(audio.get_sample_size(self.format))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(frames))
            wf.close()
            
            logger.info(f"Audio recorded and saved to {output_file}")
            return output_file
            
        except Exception as e:
            logger.error(f"Error recording audio: {str(e)}")
            return None
    
    def listen_and_transcribe(self) -> str:
        """
        Listen for voice input and transcribe it to text
        
        Returns:
            Transcribed text
        """
        try:
            # Record audio
            audio_file = self.record_audio()
            
            if not audio_file:
                return "Sorry, there was an error recording audio."
            
            # Transcribe audio
            with open(audio_file, 'rb') as f:
                transcription = self.transcribe_audio_file(f)
            
            # Clean up the temporary file
            try:
                os.remove(audio_file)
            except:
                pass
            
            return transcription
            
        except Exception as e:
            logger.error(f"Error in listen_and_transcribe: {str(e)}")
            return "Sorry, I couldn't process your voice input."
    
    def speak_text(self, text: str) -> None:
        """
        Convert text to speech and play it
        
        Args:
            text: Text to speak
        """
        try:
            # Convert text to speech
            audio_file = self.text_to_speech(text)
            
            if not audio_file:
                logger.error("Failed to generate speech")
                return
            
            # Play the audio file (platform-dependent)
            if os.name == 'posix':  # macOS or Linux
                os.system(f"afplay {audio_file}")
            elif os.name == 'nt':  # Windows
                os.system(f"start {audio_file}")
            else:
                logger.warning(f"Unsupported platform: {os.name}, cannot play audio")
            
            # Clean up the temporary file
            try:
                # Wait a bit to ensure the file is fully played
                threading.Timer(5, lambda: os.remove(audio_file)).start()
            except:
                pass
                
        except Exception as e:
            logger.error(f"Error in speak_text: {str(e)}")
