from typing import Any, Dict, Optional
import time

class Cache:
    """
    Simple in-memory cache implementation with TTL (Time To Live).
    """
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get a value from the cache if it exists and hasn't expired.
        
        Args:
            key: The cache key
            
        Returns:
            The cached value or None if not found/expired
        """
        if key not in self._cache:
            return None
        
        cache_item = self._cache[key]
        # Check if the item has expired
        if cache_item["expiry"] < time.time():
            # Remove expired item
            del self._cache[key]
            return None
            
        return cache_item["value"]
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """
        Set a value in the cache with a TTL.
        
        Args:
            key: The cache key
            value: The value to store
            ttl: Time to live in seconds (default: 1 hour)
        """
        expiry = time.time() + ttl
        self._cache[key] = {
            "value": value,
            "expiry": expiry
        }
    
    def delete(self, key: str) -> None:
        """
        Delete a value from the cache.
        
        Args:
            key: The cache key
        """
        if key in self._cache:
            del self._cache[key]
    
    def clear(self) -> None:
        """Clear all items from the cache."""
        self._cache.clear()
        
    def cleanup(self) -> None:
        """Remove all expired items from the cache."""
        current_time = time.time()
        keys_to_delete = [
            key for key, item in self._cache.items() 
            if item["expiry"] < current_time
        ]
        
        for key in keys_to_delete:
            del self._cache[key]
