import json
import urllib.request
import urllib.parse
from typing import Dict, Any

# Local registry of famous landmarks to ensure fast, reliable, offline-capable resolution of POIs
LANDMARK_REGISTRY = {
    "eiffel tower": {
        "place": "Eiffel Tower",
        "city": "Paris",
        "country": "France",
        "latitude": 48.8584,
        "longitude": 2.2945
    },
    "statue of liberty": {
        "place": "Statue of Liberty",
        "city": "New York",
        "country": "United States",
        "latitude": 40.6892,
        "longitude": -74.0445
    },
    "taj mahal": {
        "place": "Taj Mahal",
        "city": "Agra",
        "country": "India",
        "latitude": 27.1751,
        "longitude": 78.0421
    },
    "colosseum": {
        "place": "Colosseum",
        "city": "Rome",
        "country": "Italy",
        "latitude": 41.8902,
        "longitude": 12.4922
    }
}

def get_location_information(location: str) -> Dict[str, Any]:
    """
    Retrieve basic geographic information (geocoding) for a place or city.
    
    Args:
        location: Place name or city name (e.g., "Eiffel Tower" or "Paris")
        
    Returns:
        A dictionary containing place, city, country, latitude, and longitude.
    """
    if not location or not isinstance(location, str) or not location.strip():
        return {
            "error": "Invalid location format provided."
        }
        
    location_clean = location.strip()
    location_lower = location_clean.lower()
    
    # 1. Check local landmark registry first
    for landmark_key, landmark_data in LANDMARK_REGISTRY.items():
        if landmark_key in location_lower:
            return landmark_data
            
    # 2. Fall back to Open-Meteo Geocoding API for cities/regions
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location_clean)}&count=1&language=en&format=json"
    
    try:
        req = urllib.request.Request(geocoding_url, headers={"User-Agent": "UtilityAIAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return {"error": f"Geocoding service returned status code {response.status}."}
                
            geo_data = json.loads(response.read().decode("utf-8"))
            results = geo_data.get("results")
            
            if not results:
                return {"error": f"Place or city '{location_clean}' not found."}
                
            result = results[0]
            place_name = result.get("name", location_clean)
            country = result.get("country", "Unknown")
            
            city = result.get("admin1", "")
            if not city:
                city = result.get("timezone", "").split("/")[-1].replace("_", " ") if "timezone" in result else ""
                
            if result.get("feature_code") in ["PPLC", "PPLA"]:
                city = place_name
                
            return {
                "place": place_name,
                "city": city if city else "N/A",
                "country": country,
                "latitude": result.get("latitude"),
                "longitude": result.get("longitude")
            }
            
    except urllib.error.URLError as e:
        return {"error": f"Network error during geocoding: {str(e.reason)}"}
    except TimeoutError:
        return {"error": "Request timed out during geocoding."}
    except Exception as e:
        return {"error": f"Failed to retrieve location information: {str(e)}"}


