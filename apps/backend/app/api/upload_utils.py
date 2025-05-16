import os
import tempfile
import logging
from fastapi import UploadFile
from typing import Optional

logger = logging.getLogger(__name__)

async def save_upload_file_temp(upload_file: UploadFile) -> Optional[str]:
    """
    Save an upload file temporarily and return the path to the saved file
    
    Args:
        upload_file: The uploaded file
        
    Returns:
        Path to the saved file or None if saving failed
    """
    try:
        # Create a temporary file
        suffix = os.path.splitext(upload_file.filename)[1] if upload_file.filename else ".tmp"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            # Read the uploaded file in chunks and write to the temporary file
            content = await upload_file.read()
            temp.write(content)
            temp_path = temp.name
            
        logger.info(f"Saved uploaded file to {temp_path}")
        return temp_path
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        return None

def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up a temporary file
    
    Args:
        file_path: Path to the file to clean up
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
            logger.info(f"Cleaned up temporary file {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up temporary file {file_path}: {str(e)}")
