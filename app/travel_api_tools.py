# Copyright 2026 Google LLC
# Real public API tool for live travel destination info and current weather

import os
import logging
import httpx

logger = logging.getLogger(__name__)


def get_live_destination_info(city_name: str) -> dict:
    """Fetch real-time location details and current weather forecast for any destination worldwide via Open-Meteo Public API.

    Args:
        city_name: The name of the city or destination (e.g., 'Paris', 'Kyoto', 'Barcelona', 'Tokyo').

    Returns:
        Dictionary containing real destination coordinates, country, population, timezone, and live weather conditions.
    """
    api_key = os.getenv("TRAVEL_API_KEY")  # Optional API key read from env if provided
    headers = {"User-Agent": "TravelConcierge/1.0"}
    if api_key:
        headers["X-Api-Key"] = api_key

    logger.info(f"Fetching real destination info for: {city_name}")

    try:
        # Step 1: Geocoding lookup for city coordinates & facts
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city_name}&count=1&language=en&format=json"
        geo_res = httpx.get(geo_url, headers=headers, timeout=5.0)
        geo_data = geo_res.json()

        if not geo_data.get("results"):
            return {"error": f"Destination '{city_name}' not found in public geocoding database."}

        loc = geo_data["results"][0]
        lat = loc["latitude"]
        lon = loc["longitude"]

        # Step 2: Fetch live weather forecast
        weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        w_res = httpx.get(weather_url, headers=headers, timeout=5.0)
        w_data = w_res.json().get("current_weather", {})

        temp_c = w_data.get("temperature")
        temp_f = round(temp_c * 9 / 5 + 32, 1) if temp_c is not None else None

        return {
            "city": loc.get("name"),
            "country": loc.get("country"),
            "region": loc.get("admin1"),
            "latitude": lat,
            "longitude": lon,
            "timezone": loc.get("timezone"),
            "population": loc.get("population"),
            "elevation_meters": loc.get("elevation"),
            "current_weather": {
                "temperature_celsius": temp_c,
                "temperature_fahrenheit": temp_f,
                "windspeed_kmh": w_data.get("windspeed"),
                "is_daytime": bool(w_data.get("is_day", 1)),
            },
        }
    except Exception as e:
        logger.error(f"Error calling live public travel API: {e}")
        return {"error": f"Failed to fetch live travel data for '{city_name}': {str(e)}"}
