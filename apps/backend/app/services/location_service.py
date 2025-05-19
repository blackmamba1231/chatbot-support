from typing import List, Dict, Any

class LocationService:
    def __init__(self):
        # Initialize with locations from configuration
        self._locations = [
            {
                "city": "Alba Iulia",
                "state": "Alba",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Mall delivery from Alba Mall",
                "mall": "Alba Mall"
            },
            {
                "city": "Arad",
                "state": "Arad",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Mall delivery from Atrium Mall",
                "mall": "Atrium Mall"
            },
            {
                "city": "Miercurea Ciuc",
                "state": "Harghita",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Mall delivery from Nest Park Retail",
                "mall": "Nest Park Retail"
            },
            {
                "city": "Vaslui",
                "state": "Vaslui",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Mall delivery from Proxima Shopping Center",
                "mall": "Proxima Shopping Center"
            },
            {
                "city": "Târgu Mureș",
                "state": "Mureș",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Mall delivery from PlazaM Târgu Mureș",
                "mall": "PlazaM Târgu Mureș"
            },
            {
                "city": "Suceava",
                "state": "Suceava",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Mall delivery from Iulius Mall and Shopping City",
                "malls": ["Iulius Mall Suceava", "Shopping City Suceava"]
            },
            {
                "city": "Târgu-Jiu",
                "state": "Gorj",
                "is_active": True,
                "services": ["mall_delivery"],
                "description": "Mall delivery from Shopping City",
                "mall": "Shopping City Târgu-Jiu"
            }
        ]
    
    def get_active_locations(self) -> List[Dict[str, Any]]:
        """Get all active delivery locations"""
        return [loc for loc in self._locations if loc["is_active"]]
    
    def get_locations_by_service(self, service_type: str) -> List[Dict[str, Any]]:
        """Get locations that offer a specific service type"""
        return [loc for loc in self._locations if loc["is_active"] and service_type in loc["services"]]
    
    def get_location_details(self, city: str) -> Dict[str, Any]:
        """Get detailed information about a specific location"""
        for location in self._locations:
            if location["city"].lower() == city.lower() and location["is_active"]:
                return location
        return None
