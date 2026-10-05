# Copyright 2026 Google LLC
# Video generation tool for travel concierge agent

import base64
import logging
import uuid
from google import genai
from google.genai import types
from google.cloud import storage
from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)

PROJECT_ID = "qwiklabs-gcp-01-127c602b3efe"
BUCKET_NAME = "travel-concierge-assets-qwiklabs-gcp-01-127c602b3efe"


async def generate_destination_video(
    prompt: str,
    tool_context: ToolContext,
) -> dict:
    """Generates a short video for a travel destination or landmark using gemini-omni-flash-preview in global location.

    Saves the generated video as an artifact for Playground visualization and uploads the bytes to Cloud Storage.

    Args:
        prompt: Detailed description of the travel video to generate (e.g. 'A scenic video clip of Mt Fuji with cherry blossoms').
        tool_context: ADK ToolContext injected automatically by the framework.

    Returns:
        Dictionary containing public Cloud Storage HTTPS URL, filename, and status.
    """
    logger.info(f"Generating video with prompt: '{prompt}'")

    # 1. Initiate interaction stream with gemini-omni-flash-preview in global location
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    stream = client.interactions.create(
        model="gemini-omni-flash-preview",
        input=prompt,
        response_modalities=["text", "video"],
        stream=True,
    )

    interaction_id = None
    for ev in stream:
        if hasattr(ev, "interaction") and ev.interaction and getattr(ev.interaction, "id", None):
            interaction_id = ev.interaction.id

    if not interaction_id:
        raise RuntimeError("Failed to obtain interaction ID for video generation.")

    # 2. Retrieve completed interaction details containing video payload
    final_interaction = client.interactions.get(id=interaction_id)

    output_video = getattr(final_interaction, "output_video", None)
    b64_data = None
    if output_video:
        b64_data = getattr(output_video, "data", None) or (output_video.get("data") if isinstance(output_video, dict) else None)

    if not b64_data:
        dump = final_interaction.model_dump()
        b64_data = dump.get("output_video", {}).get("data")

    if not b64_data:
        raise RuntimeError("No video data returned from gemini-omni-flash-preview interaction.")

    video_bytes = base64.b64decode(b64_data)
    mime_type = "video/mp4"
    filename = f"video_{uuid.uuid4().hex[:8]}.mp4"

    # 3. Save video as artifact so it appears in Playground's Artifacts panel
    artifact_part = types.Part.from_bytes(data=video_bytes, mime_type=mime_type)
    await tool_context.save_artifact(filename=filename, artifact=artifact_part)

    # 4. Upload video bytes to public Cloud Storage bucket
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_string(video_bytes, content_type=mime_type)

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"

    return {
        "status": "success",
        "filename": filename,
        "video_url": public_url,
        "prompt": prompt,
    }
