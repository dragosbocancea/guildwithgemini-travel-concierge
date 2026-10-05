# Copyright 2026 Google LLC
# Firestore tools for travel-concierge agent

import logging
from typing import Any
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcode project ID as string (never use project number from GOOGLE_CLOUD_PROJECT or auth.default)
PROJECT_ID = "qwiklabs-gcp-01-127c602b3efe"


def _get_firestore_client() -> firestore.Client:
    return firestore.Client(project=PROJECT_ID)


def search_destinations(query: str = "", category: str = "") -> list[dict[str, Any]]:
    """Search travel destinations stored in Firestore by query string or category.

    Args:
        query: Optional search term matching name, climate, or highlights.
        category: Optional category filter (e.g., 'Coastal City', 'Cultural Metropolis').

    Returns:
        List of matching destination dictionaries.
    """
    logger.info(f"Searching Firestore destinations (query='{query}', category='{category}')")
    db = _get_firestore_client()
    docs = db.collection("destinations").stream()

    results = []
    q_lower = query.lower()
    cat_lower = category.lower()

    for doc in docs:
        data = doc.to_dict()
        if not data:
            continue

        name_match = q_lower in data.get("name", "").lower()
        desc_match = q_lower in data.get("description", "").lower()
        climate_match = q_lower in data.get("climate", "").lower()
        highlights_match = any(q_lower in h.lower() for h in data.get("highlights", []))

        matches_query = not query or (name_match or desc_match or climate_match or highlights_match)
        matches_category = not category or (cat_lower in data.get("category", "").lower())

        if matches_query and matches_category:
            results.append(data)

    logger.info(f"Found {len(results)} matching destinations.")
    return results


def get_destination_details(destination_id: str) -> dict[str, Any]:
    """Retrieve detailed information for a specific travel destination from Firestore.

    Args:
        destination_id: Document ID of the destination (e.g., 'san-francisco', 'tokyo').

    Returns:
        Destination details dictionary, or error dict if not found.
    """
    logger.info(f"Retrieving destination details for ID: {destination_id}")
    db = _get_firestore_client()
    doc_ref = db.collection("destinations").document(destination_id)
    doc = doc_ref.get()

    if doc.exists:
        return doc.to_dict()  # type: ignore
    else:
        return {"error": f"Destination with ID '{destination_id}' not found."}


def add_destination(
    destination_id: str,
    name: str,
    category: str,
    climate: str,
    budget_tier: str,
    highlights: list[str],
    recommended_days: int,
    description: str,
) -> str:
    """Add or update a travel destination in Firestore.

    Args:
        destination_id: Unique identifier for destination (slug, e.g. 'rome').
        name: Name of destination (e.g. 'Rome, Italy').
        category: Category description.
        climate: Climate description.
        budget_tier: Budget tier string ('$', '$$', '$$$').
        highlights: List of top attraction highlights.
        recommended_days: Recommended number of days for visit.
        description: Overview summary.

    Returns:
        Confirmation message string.
    """
    logger.info(f"Adding destination to Firestore: {name} ({destination_id})")
    db = _get_firestore_client()
    doc_data = {
        "id": destination_id,
        "name": name,
        "category": category,
        "climate": climate,
        "budget_tier": budget_tier,
        "highlights": highlights,
        "recommended_days": recommended_days,
        "description": description,
    }
    db.collection("destinations").document(destination_id).set(doc_data)
    return f"Successfully added destination '{name}' to Firestore with ID '{destination_id}'."
