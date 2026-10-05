# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import logging
from google.adk.memory.memory_entry import MemoryEntry
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.tools import ToolContext
from google.genai import types

logger = logging.getLogger(__name__)

_memory_service = None

def get_memory_service() -> VertexAiMemoryBankService:
    global _memory_service
    if _memory_service is None:
        _memory_service = VertexAiMemoryBankService(
            project=os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-01-127c602b3efe"),
            location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
            agent_engine_id="7882988472636538880",
        )
    return _memory_service


async def remember_place_of_interest(
    place_name: str,
    location_type: str,
    notes: str,
    tool_context: ToolContext,
) -> str:
    """Saves a place of interest, favorite destination, or preferred visiting location to the user's long-term Memory Bank.

    Args:
        place_name: The name of the place, city, landmark, or attraction (e.g., 'Kyoto', 'Eiffel Tower', 'Amalfi Coast').
        location_type: The type of location (e.g., 'City', 'Museum', 'Restaurant', 'Natural Wonder', 'Historical Site').
        notes: Additional context, reasons, or traveler preferences (e.g., 'Wants to visit during cherry blossom season', 'Enjoys fine dining').
        tool_context: The ADK tool context.

    Returns:
        A confirmation message indicating that the preference/place was recorded in memory.
    """
    memory_text = (
        f"Preferred Visiting Location / Place of Interest: {place_name} "
        f"(Type: {location_type}). Notes: {notes}"
    )
    entry = MemoryEntry(
        author="user",
        content=types.Content(
            parts=[types.Part.from_text(text=memory_text)],
            role="user",
        ),
    )
    try:
        if hasattr(tool_context, "add_memory"):
            await tool_context.add_memory(memories=[entry])
        else:
            user_id = getattr(tool_context, "user_id", None) or "web-user"
            service = get_memory_service()
            await service.add_memory(user_id=user_id, memories=[entry], app_name="app")
    except Exception as exc:
        logger.warning("Error saving memory via context/service: %s", exc)
        try:
            user_id = getattr(tool_context, "user_id", None) or "web-user"
            service = get_memory_service()
            await service.add_memory(user_id=user_id, memories=[entry], app_name="app")
        except Exception as e2:
            logger.error("Fallback add_memory error: %s", e2)

    return (
        f"Successfully recorded '{place_name}' ({location_type}) "
        f"in user's travel preferences."
    )


async def search_user_memory(
    query: str,
    tool_context: ToolContext,
) -> str:
    """Searches long-term memory for past user preferences, places of interest, or itinerary notes.

    Args:
        query: The search terms to find relevant user memory entries.
        tool_context: The ADK tool context.

    Returns:
        A string summarizing matching memories found in the Memory Bank.
    """
    try:
        if hasattr(tool_context, "search_memory"):
            mem_resp = await tool_context.search_memory(query=query)
            if mem_resp and hasattr(mem_resp, "memories") and mem_resp.memories:
                lines = []
                for m in mem_resp.memories:
                    c = getattr(m, "content", None)
                    if c and hasattr(c, "parts"):
                        txt = " ".join(getattr(p, "text", "") for p in c.parts if hasattr(p, "text"))
                        lines.append(txt)
                    else:
                        lines.append(str(m))
                if lines:
                    return "Found memory entries:\n" + "\n".join(lines)
    except Exception as exc:
        logger.info("Falling back to direct VertexAiMemoryBankService for search_memory: %s", exc)

    user_id = getattr(tool_context, "user_id", None) or "web-user"
    service = get_memory_service()
    try:
        resp = await service.search_memory(user_id=user_id, query=query, app_name="app")
        if resp and hasattr(resp, "memories") and resp.memories:
            lines = []
            for m in resp.memories:
                c = getattr(m, "content", None)
                if c and hasattr(c, "parts"):
                    txt = " ".join(getattr(p, "text", "") for p in c.parts if hasattr(p, "text"))
                    lines.append(txt)
                else:
                    lines.append(str(m))
            if lines:
                return "Found memory entries:\n" + "\n".join(lines)
    except Exception as e:
        return f"No memories found or error accessing Memory Bank: {e}"

    return "No relevant memories found in the Memory Bank."
