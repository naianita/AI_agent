from datetime import datetime
import pytz
import requests

def get_current_time() -> str:
    """Get the current time in Vancouver timezone"""
    vancouver_tz = pytz.timezone('America/Vancouver')
    current_time = datetime.now(vancouver_tz)
    return f"Current time in Vancouver: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}"

def calculate(expression: str) -> str:
    """Perform mathematical calculations"""
    try:
        allowed_chars = "0123456789+-*/()., "
        if all(c in allowed_chars for c in expression):
            result = eval(expression)
            return f"Result: {result}"
        else:
            return "Error: Invalid characters in expression"
    except Exception as e:
        return f"Error in calculation: {str(e)}"

def get_weather(city: str = "Vancouver") -> str:
    """Get current weather for a city using Open-Meteo API (no key required)"""
    try:
        # Geocoding to get latitude/longitude
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo_resp = requests.get(geo_url, timeout=5)
        geo_data = geo_resp.json()
        if not geo_data.get('results'):
            return f"Could not find location for {city}."
        lat = geo_data['results'][0]['latitude']
        lon = geo_data['results'][0]['longitude']
        # Get current weather
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        weather_resp = requests.get(weather_url, timeout=5)
        weather_data = weather_resp.json()
        if 'current_weather' not in weather_data:
            return f"Could not get weather data for {city}."
        temp = weather_data['current_weather']['temperature']
        wind = weather_data['current_weather']['windspeed']
        desc = f"Current temperature in {city}: {temp}°C, wind speed: {wind} km/h."
        return desc
    except Exception as e:
        return f"Error getting weather for {city}: {str(e)}"

def search_information(query: str) -> str:
    """Search for information (placeholder, can integrate real API)"""
    return f"Search results for '{query}': [This is a placeholder. In production, integrate with a search API]"