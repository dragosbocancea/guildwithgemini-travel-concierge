# Copyright 2026 Google LLC
# Google Maps Geocoding and Places (New) API tools

import os
import logging
import httpx
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not key:
        raise ValueError("GOOGLE_MAPS_API_KEY environment variable is not set in .env")
    return key


def geocode_address(address: str) -> dict:
    """Converts a street address or landmark name into geographic coordinates (latitude and longitude).

    Args:
        address: The address or landmark name to geocode (e.g., 'Eiffel Tower, Paris', 'Shibuya Crossing, Tokyo').

    Returns:
        Dictionary containing formatted address and location coordinates (latitude, longitude).
    """
    logger.info(f"Geocoding address: {address}")
    try:
        api_key = _get_api_key()
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        res = httpx.get(url, params={"address": address, "key": api_key}, timeout=5.0)
        data = res.json()

        if data.get("status") == "OK" and data.get("results"):
            first_result = data["results"][0]
            location = first_result["geometry"]["location"]
            return {
                "formatted_address": first_result.get("formatted_address"),
                "location": {
                    "latitude": location.get("lat"),
                    "longitude": location.get("lng"),
                },
            }
        else:
            return {"error": f"Geocoding failed for '{address}': {data.get('status', 'NO_RESULTS')}"}
    except Exception as e:
        logger.error(f"Error in geocode_address: {e}")
        return {"error": f"Failed to geocode address: {str(e)}"}


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "tourist_attraction",
    radius_meters: float = 1000.0,
) -> list[dict]:
    """Finds nearby places of a specified type around a geographic location using Places API (New).

    Args:
        latitude: Latitude coordinate of the center point.
        longitude: Longitude coordinate of the center point.
        place_type: Type of place to search for (e.g., 'tourist_attraction', 'restaurant', 'museum', 'cafe', 'park').
        radius_meters: Search radius in meters (default 1000.0).

    Returns:
        List of nearby place dictionaries containing name, address, location, rating, and types.
    """
    logger.info(f"Finding nearby places ({place_type}) near lat={latitude}, lng={longitude}")
    try:
        api_key = _get_api_key()
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location,places.types,places.rating",
        }
        body = {
            "includedTypes": [place_type],
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {
                        "latitude": latitude,
                        "longitude": longitude,
                    },
                    "radius": radius_meters,
                }
            },
        }

        res = httpx.post(url, headers=headers, json=body, timeout=5.0)
        data = res.json()

        results = []
        for place in data.get("places", []):
            display_name = place.get("displayName", {}).get("text")
            results.append({
                "name": display_name,
                "address": place.get("formattedAddress"),
                "location": {
                    "latitude": place.get("location", {}).get("latitude"),
                    "longitude": place.get("location", {}).get("longitude"),
                },
                "rating": place.get("rating"),
                "types": place.get("types", []),
            })

        logger.info(f"Found {len(results)} nearby places.")
        return results
    except Exception as e:
        logger.error(f"Error in find_nearby_places: {e}")
        return [{"error": f"Failed to find nearby places: {str(e)}"}]
