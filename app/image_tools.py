# Copyright 2026 Google LLC
# Image generation tool for travel concierge agent

import uuid
import logging
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

PROJECT_ID = "qwiklabs-gcp-01-127c602b3efe"
BUCKET_NAME = "travel-concierge-assets-qwiklabs-gcp-01-127c602b3efe"


async def generate_destination_image(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generates an image for a travel destination or landmark using gemini-3.1-flash-lite-image in global location.

    Saves the generated image as an artifact for Playground visualization and uploads the bytes to Cloud Storage.

    Args:
        prompt: Detailed description of the travel image to generate (e.g. 'A scenic view of Mt Fuji with cherry blossoms').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        Dictionary containing public Cloud Storage HTTPS URL, filename, and status.
    """
    logger.info(f"Generating image with prompt: '{prompt}'")

    # 1. Generate image using gemini-3.1-flash-lite-image in global location
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
    )

    part = response.candidates[0].content.parts[0]
    image_bytes = part.inline_data.data
    mime_type = part.inline_data.mime_type or "image/jpeg"

    ext = "png" if "png" in mime_type.lower() else "jpeg"
    filename = f"destination_{uuid.uuid4().hex[:8]}.{ext}"

    # 2. Save image as artifact so it appears in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 3. Upload same image bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "filename": filename,
        "image_url": public_url,
        "prompt": prompt,
    }
