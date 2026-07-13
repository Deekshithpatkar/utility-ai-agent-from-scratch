import json
import urllib.request
import urllib.parse
from typing import Dict, Any

def get_weather(location: str) -> Dict[str, Any]:
    """
    Retrieve current weather information for a city or location.
    
    Args:
        location: City or location name
        
    Returns:
        A dictionary containing location, temperature, temperature_unit, condition, and humidity.
    """
    if not location or not isinstance(location, str) or not location.strip():
        return {
            "error": "Invalid location format provided."
        }
    
    location = location.strip()
    
    # Step 1: Geocode the city name to latitude and longitude
    # Open-Meteo Geocoding API (free, no API key required)
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
            lat = result["latitude"]
            lon = result["longitude"]
            resolved_name = result.get("name", location)
            country = result.get("country", "")
            full_location = f"{resolved_name}, {country}" if country else resolved_name
            
    except urllib.error.URLError as e:
        return {"error": f"Network error during location lookup: {str(e.reason)}"}
    except TimeoutError:
        return {"error": "Request timed out during location lookup."}
    except Exception as e:
        return {"error": f"Failed to geocode location: {str(e)}"}

    # Step 2: Fetch current weather for coordinates
    # Open-Meteo Forecast API with current_weather and relative_humidity_2m
    weather_url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code"
    )
    
    try:
        req = urllib.request.Request(weather_url, headers={"User-Agent": "UtilityAIAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status != 200:
                return {"error": f"Weather service returned status code {response.status}."}
            
            weather_data = json.loads(response.read().decode("utf-8"))
            current = weather_data.get("current", {})
            
            if not current:
                return {"error": "Missing current weather information from API response."}
            
            temp = current.get("temperature_2m")
            humidity = current.get("relative_humidity_2m")
            code = current.get("weather_code", 0)
            
            # WMO Weather interpretation codes (WMO code)
            # Map code to simple conditions
            wmo_codes = {
                0: "Clear sky",
                1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
                45: "Fog", 48: "Depositing rime fog",
                51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
                61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
                71: "Slight snow fall", 73: "Moderate snow fall", 75: "Heavy snow fall",
                77: "Snow grains",
                80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
                85: "Slight snow showers", 86: "Heavy snow showers",
                95: "Thunderstorm", 96: "Thunderstorm with slight hail", 99: "Thunderstorm with heavy hail"
            }
            
            condition = wmo_codes.get(code, "Unknown")
            
            return {
                "location": full_location,
                "temperature": temp,
                "temperature_unit": "Celsius",
                "condition": condition,
                "humidity": humidity
            }
            
    except urllib.error.URLError as e:
        return {"error": f"Network error during weather fetch: {str(e.reason)}"}
    except TimeoutError:
        return {"error": "Request timed out during weather fetch."}
    except Exception as e:
        return {"error": f"Failed to retrieve weather data: {str(e)}"}
