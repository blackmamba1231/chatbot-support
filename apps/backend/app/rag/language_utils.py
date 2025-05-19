import re
import logging
import translators as ts
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def detect_language(text: str, default_language: str = "en") -> str:
    """
    Detect the language of the input text
    
    Args:
        text: Input text
        default_language: Default language code to return if detection fails
        
    Returns:
        Language code (e.g., 'en', 'ro', 'fr')
    """
    try:
        # Simple language detection based on common words
        text = text.lower()
        
        # Romanian specific words and patterns
        romanian_patterns = [
            r'\bsunt\b', r'\beste\b', r'\bși\b', r'\bla\b', r'\bcu\b', 
            r'\bîn\b', r'\bpe\b', r'\bde\b', r'\bpentru\b', r'\bvă\b',
            r'\bvă rog\b', r'\bmulțumesc\b', r'\bbună\b', r'\bsalut\b'
        ]
        
        # French specific words and patterns
        french_patterns = [
            r'\bje\b', r'\btu\b', r'\bil\b', r'\belle\b', r'\bnous\b', 
            r'\bvous\b', r'\best\b', r'\bsont\b', r'\bbonjour\b', r'\bmerci\b',
            r'\bs\'il vous plaît\b', r'\bau revoir\b', r'\bje suis\b'
        ]
        
        # Count matches for each language
        ro_matches = sum(1 for pattern in romanian_patterns if re.search(pattern, text))
        fr_matches = sum(1 for pattern in french_patterns if re.search(pattern, text))
        
        # Determine language based on matches
        if ro_matches > fr_matches and ro_matches > 0:
            return "ro"
        elif fr_matches > ro_matches and fr_matches > 0:
            return "fr"
        
        # Default to English if no clear match
        return default_language
    except Exception as e:
        logger.error(f"Error detecting language: {str(e)}")
        return default_language

def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language
    
    Args:
        text: Text to translate
        source_lang: Source language code
        target_lang: Target language code
        
    Returns:
        Translated text
    """
    if source_lang == target_lang:
        return text
        
    try:
        # Use the translators library for translation
        translated_text = ts.translate_text(
            query_text=text,
            from_language=source_lang,
            to_language=target_lang
        )
        return translated_text
    except Exception as e:
        logger.error(f"Error translating text: {str(e)}")
        # If translation fails, return original text
        return text
