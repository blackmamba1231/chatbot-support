import os
import logging
import datetime
from typing import Dict, Any, List, Optional
import json

logger = logging.getLogger(__name__)

class ShoppingListService:
    """Service for managing shopping lists"""
    
    def __init__(self):
        """Initialize the shopping list service"""
        # For demo purposes, we'll use a local file to store shopping lists
        self.shopping_list_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            "knowledge_base", 
            "shopping_lists.json"
        )
        
        # Create shopping list file if it doesn't exist
        if not os.path.exists(self.shopping_list_file):
            with open(self.shopping_list_file, 'w') as f:
                json.dump({"lists": [{"name": "default", "items": []}]}, f)
    
    def add_item(self, item: str, list_name: str = "default") -> Dict[str, Any]:
        """
        Add an item to a shopping list
        
        Args:
            item: Item to add
            list_name: Name of the shopping list (default: "default")
            
        Returns:
            Dictionary with status and item details
        """
        try:
            # Load shopping lists
            with open(self.shopping_list_file, 'r') as f:
                data = json.load(f)
            
            # Check if list exists
            list_exists = False
            for shopping_list in data["lists"]:
                if shopping_list["name"] == list_name:
                    # Add item to list
                    item_obj = {
                        "id": f"item_{datetime.datetime.now().timestamp()}",
                        "name": item,
                        "added_at": datetime.datetime.now().isoformat(),
                        "completed": False
                    }
                    shopping_list["items"].append(item_obj)
                    list_exists = True
                    break
            
            # Create list if it doesn't exist
            if not list_exists:
                data["lists"].append({
                    "name": list_name,
                    "items": [{
                        "id": f"item_{datetime.datetime.now().timestamp()}",
                        "name": item,
                        "added_at": datetime.datetime.now().isoformat(),
                        "completed": False
                    }]
                })
            
            # Save shopping lists
            with open(self.shopping_list_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Item '{item}' added to shopping list '{list_name}'")
            return {
                "status": "success",
                "message": f"Item '{item}' added to shopping list",
                "item": item,
                "list_name": list_name
            }
            
        except Exception as e:
            logger.error(f"Error adding item to shopping list: {str(e)}")
            return {
                "status": "error",
                "message": f"Error adding item to shopping list: {str(e)}",
                "item": item,
                "list_name": list_name
            }
    
    def get_items(self, list_name: str = "default", include_completed: bool = False) -> Dict[str, Any]:
        """
        Get items from a shopping list
        
        Args:
            list_name: Name of the shopping list (default: "default")
            include_completed: Whether to include completed items (default: False)
            
        Returns:
            Dictionary with status and items
        """
        try:
            # Load shopping lists
            with open(self.shopping_list_file, 'r') as f:
                data = json.load(f)
            
            # Find the requested list
            items = []
            for shopping_list in data["lists"]:
                if shopping_list["name"] == list_name:
                    if include_completed:
                        items = shopping_list["items"]
                    else:
                        items = [item for item in shopping_list["items"] if not item["completed"]]
                    break
            
            logger.info(f"Retrieved {len(items)} items from shopping list '{list_name}'")
            return {
                "status": "success",
                "items": items,
                "list_name": list_name
            }
            
        except Exception as e:
            logger.error(f"Error getting items from shopping list: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting items from shopping list: {str(e)}",
                "items": [],
                "list_name": list_name
            }
    
    def mark_item_completed(self, item_id: str, list_name: str = "default") -> Dict[str, Any]:
        """
        Mark an item as completed
        
        Args:
            item_id: ID of the item to mark as completed
            list_name: Name of the shopping list (default: "default")
            
        Returns:
            Dictionary with status and item details
        """
        try:
            # Load shopping lists
            with open(self.shopping_list_file, 'r') as f:
                data = json.load(f)
            
            # Find the item and mark it as completed
            item_found = False
            for shopping_list in data["lists"]:
                if shopping_list["name"] == list_name:
                    for item in shopping_list["items"]:
                        if item["id"] == item_id:
                            item["completed"] = True
                            item["completed_at"] = datetime.datetime.now().isoformat()
                            item_found = True
                            break
                    if item_found:
                        break
            
            if not item_found:
                logger.warning(f"Item with ID '{item_id}' not found in shopping list '{list_name}'")
                return {
                    "status": "error",
                    "message": f"Item not found",
                    "item_id": item_id,
                    "list_name": list_name
                }
            
            # Save shopping lists
            with open(self.shopping_list_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"Item with ID '{item_id}' marked as completed in shopping list '{list_name}'")
            return {
                "status": "success",
                "message": "Item marked as completed",
                "item_id": item_id,
                "list_name": list_name
            }
            
        except Exception as e:
            logger.error(f"Error marking item as completed: {str(e)}")
            return {
                "status": "error",
                "message": f"Error marking item as completed: {str(e)}",
                "item_id": item_id,
                "list_name": list_name
            }
    
    def get_all_lists(self) -> Dict[str, Any]:
        """
        Get all shopping lists
        
        Returns:
            Dictionary with status and lists
        """
        try:
            # Load shopping lists
            with open(self.shopping_list_file, 'r') as f:
                data = json.load(f)
            
            logger.info(f"Retrieved {len(data['lists'])} shopping lists")
            return {
                "status": "success",
                "lists": data["lists"]
            }
            
        except Exception as e:
            logger.error(f"Error getting shopping lists: {str(e)}")
            return {
                "status": "error",
                "message": f"Error getting shopping lists: {str(e)}",
                "lists": []
            }
