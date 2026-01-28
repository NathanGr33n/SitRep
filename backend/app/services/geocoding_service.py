"""
Geocoding service using Nominatim (OpenStreetMap).
Converts location names to coordinates with rate limiting.
"""
import logging
import time
from typing import Optional, Tuple, List
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = logging.getLogger(__name__)


class GeocodingService:
    """
    Service for geocoding location names to coordinates.
    Uses Nominatim with rate limiting and retry logic.
    """
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent=settings.geocoding_user_agent)
        self.last_request_time = 0
        self.rate_limit = settings.geocoding_rate_limit  # Requests per second
        
    def _rate_limit(self):
        """Enforce rate limiting between requests."""
        if self.rate_limit > 0:
            min_interval = 1.0 / self.rate_limit
            elapsed = time.time() - self.last_request_time
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
        self.last_request_time = time.time()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def geocode_location(self, location_name: str) -> Optional[Tuple[float, float]]:
        """
        Geocode a location name to (latitude, longitude).
        Returns None if location cannot be geocoded.
        """
        try:
            self._rate_limit()
            location = self.geocoder.geocode(location_name, timeout=10)
            
            if location:
                logger.info(f"Geocoded '{location_name}' to ({location.latitude}, {location.longitude})")
                return (location.latitude, location.longitude)
            else:
                logger.warning(f"Could not geocode location: {location_name}")
                return None
                
        except (GeocoderTimedOut, GeocoderServiceError) as e:
            logger.error(f"Geocoding error for '{location_name}': {e}")
            return None
    
    def geocode_multiple(self, location_names: List[str]) -> List[dict]:
        """
        Geocode multiple locations.
        Returns list of {"name": str, "lat": float, "lon": float} or empty for failures.
        """
        results = []
        
        for name in location_names:
            coords = self.geocode_location(name)
            if coords:
                results.append({
                    "name": name,
                    "lat": coords[0],
                    "lon": coords[1]
                })
            else:
                logger.warning(f"Skipping location due to geocoding failure: {name}")
        
        return results
    
    def identify_primary_location(self, locations: List[str]) -> Optional[str]:
        """
        Identify the most likely primary location from a list.
        Uses heuristics: first mentioned, or most specific (city over country).
        """
        if not locations:
            return None
        
        # Simple heuristic: return first location
        # TODO: Improve with entity resolution and context analysis
        return locations[0]


# Singleton instance
geocoding_service = GeocodingService()
