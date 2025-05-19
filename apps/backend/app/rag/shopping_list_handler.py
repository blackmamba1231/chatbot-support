import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def handle_shopping_list_request(shopping_list_service, query: str) -> Dict[str, Any]:
    """
    Handle shopping list-related requests
    
    Args:
        shopping_list_service: The shopping list service instance
        query: User query
        
    Returns:
        Response with shopping list action results
    """
    try:
        # Extract item from query
        # Look for patterns like "add X to my shopping list" or "put X on my list"
        item = None
        
        add_patterns = [
            r"add\s+(.+?)\s+to\s+(?:my|the)\s+(?:shopping)?\s*list",
            r"put\s+(.+?)\s+on\s+(?:my|the)\s+(?:shopping)?\s*list",
            r"add\s+(.+?)\s+to\s+(?:my|the)\s+cart"
        ]
        
        for pattern in add_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                item = match.group(1).strip()
                break
                
        if not item:
            # Try to find the item after "shopping list" or similar phrases
            list_patterns = [
                r"(?:shopping)?\s*list\s+(.+)",
                r"(?:buy|purchase|get)\s+(.+)"
            ]
            
            for pattern in list_patterns:
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    item = match.group(1).strip()
                    break
        
        if item:
            # Add item to shopping list
            result = shopping_list_service.add_item(item)
            
            if result["status"] == "success":
                return {
                    "response": f"I've added {item} to your shopping list.",
                    "action": "shopping_list_item_added",
                    "item": item
                }
            else:
                return {
                    "response": f"I couldn't add the item to your shopping list. {result.get('message', '')}",
                    "action": "shopping_list_item_failed"
                }
        else:
            return {
                "response": "What would you like to add to your shopping list?",
                "action": "request_more_info",
                "missing_info": ["item"]
            }
            
    except Exception as e:
        logger.error(f"Error handling shopping list request: {str(e)}")
        return {
            "response": "I'm having trouble processing your shopping list request. Could you try again?",
            "action": "error",
            "error": str(e)
        }
