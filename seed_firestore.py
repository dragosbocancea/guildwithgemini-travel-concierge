# Copyright 2026 Google LLC
# Seed script for travel-concierge Firestore collection

import logging
from google.cloud import firestore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hardcode project ID as string (never use project number from GOOGLE_CLOUD_PROJECT or auth.default)
PROJECT_ID = "qwiklabs-gcp-01-127c602b3efe"

DESTINATIONS = [
    {
        "id": "san-francisco",
        "name": "San Francisco, USA",
        "category": "Coastal City",
        "climate": "Mild / Foggy",
        "budget_tier": "$$",
        "highlights": ["Golden Gate Bridge", "Alcatraz Island", "Fisherman's Wharf", "Cable Cars"],
        "recommended_days": 3,
        "description": "Iconic Northern California city known for steep rolling hills, cool summer fog, vibrant culture, and tech innovation."
    },
    {
        "id": "tokyo",
        "name": "Tokyo, Japan",
        "category": "Cultural Metropolis",
        "climate": "Temperate",
        "budget_tier": "$$$",
        "highlights": ["Shibuya Crossing", "Senso-ji Temple", "Tokyo Tower", "Akihabara"],
        "recommended_days": 5,
        "description": "Dynamic capital combining ultra-modern skyscrapers, historic temples, world-class cuisine, and anime culture."
    },
    {
        "id": "paris",
        "name": "Paris, France",
        "category": "Historic & Romantic",
        "climate": "Temperate",
        "budget_tier": "$$$",
        "highlights": ["Eiffel Tower", "Louvre Museum", "Notre-Dame Cathedral", "Montmartre"],
        "recommended_days": 4,
        "description": "The City of Light, famed for art, fashion, gastronomy, and historic architecture along the Seine River."
    },
    {
        "id": "kyoto",
        "name": "Kyoto, Japan",
        "category": "Historic Heritage",
        "climate": "Temperate",
        "budget_tier": "$$",
        "highlights": ["Fushimi Inari Shrine", "Arashiyama Bamboo Grove", "Kinkaku-ji (Golden Pavilion)"],
        "recommended_days": 3,
        "description": "Cultural heart of Japan filled with classical Buddhist temples, gardens, imperial palaces, and traditional wooden houses."
    },
    {
        "id": "barcelona",
        "name": "Barcelona, Spain",
        "category": "Coastal City & Art",
        "climate": "Mediterranean",
        "budget_tier": "$$",
        "highlights": ["Sagrada Familia", "Park Güell", "Gothic Quarter", "La Barceloneta Beach"],
        "recommended_days": 4,
        "description": "Vibrant Catalan seaside city renowned for Antoni Gaudí architecture, tapas dining, and sun-soaked Mediterranean beaches."
    }
]


def seed():
    logger.info(f"Initializing Firestore client for project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    collection_ref = db.collection("destinations")

    for dest in DESTINATIONS:
        doc_id = dest["id"]
        doc_ref = collection_ref.document(doc_id)
        doc_ref.set(dest)
        logger.info(f"Seeded destination: {dest['name']} ({doc_id})")

    logger.info("Firestore seeding completed successfully.")


if __name__ == "__main__":
    seed()
