import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import Dict, Any

# Dynamic timezone mapping or zoneinfo standard library (Python 3.9+)
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback if zoneinfo is not available, try pytz
    try:
        import pytz
        ZoneInfo = pytz.timezone
    except ImportError:
        ZoneInfo = None

def get_current_time(location: str) -> Dict[str, Any]:
    """
    Return the current local time for a city or location.
    
    Args:
        location: City or location name
        
    Returns:
        A dictionary containing location, timezone, and current_time.
    """
    if not location or not isinstance(location, str) or not location.strip():
        return {
            "error": "Invalid location format provided."
        }
        
    location = location.strip()
    
    # Query Open-Meteo Geocoding API to resolve location name to timezone
    geocoding_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(location)}&count=1&language=en&format=json"
    
    try:
        req = urllib.request.Request(geocoding_url, headers={"User-Agent": "UtilityAIAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return {"error": f"Geocoding service returned status code {response.status}."}
            
            geo_data = json.loads(response.read().decode("utf-8"))
            
            if not geo_data.get("results"):
                return {"error": f"Location '{location}' not found."}
            
            result = geo_data["results"][0]
            timezone_str = result.get("timezone")
            resolved_name = result.get("name", location)
            country = result.get("country", "")
            full_location = f"{resolved_name}, {country}" if country else resolved_name
            
            if not timezone_str:
                return {"error": f"Could not determine timezone for location '{location}'."}
                
    except urllib.error.URLError as e:
        return {"error": f"Network error during timezone lookup: {str(e.reason)}"}
    except TimeoutError:
        return {"error": "Request timed out during timezone lookup."}
    except Exception as e:
        return {"error": f"Failed to locate timezone: {str(e)}"}

    # Calculate local time using Resolved Timezone
    if ZoneInfo is None:
        return {
            "error": "No timezone library (zoneinfo/pytz) available to parse timezone information."
        }
        
    try:
        tz = ZoneInfo(timezone_str)
        local_time = datetime.now(tz)
        # Format as "10:30 PM" (or "10:30:45 PM" / "%I:%M %p")
        formatted_time = local_time.strftime("%I:%M %p")
        
        return {
            "location": full_location,
            "timezone": timezone_str,
            "current_time": formatted_time
        }
    except Exception as e:
        return {"error": f"Error calculating local time for timezone '{timezone_str}': {str(e)}"}
