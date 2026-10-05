# ruff: noqa
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

import datetime
from zoneinfo import ZoneInfo

import json
import os

if "GOOGLE_CLOUD_AGENT_ENGINE_ID" not in os.environ:
    os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ID"] = "7882988472636538880"


from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.genai import types


from app.a2ui_utils import a2ui_callback
from app.budget_tools import calculate_trip_budget
from app.firestore_tools import (
    add_destination,
    get_destination_details,
    search_destinations,
)
from app.image_tools import generate_destination_image
from app.maps_tools import find_nearby_places, geocode_address
from app.memory_tools import remember_place_of_interest, search_user_memory
from app.travel_api_tools import get_live_destination_info
from app.video_tools import generate_destination_video


def _get_agent_engine_resource_name() -> str | None:
    # Read agent engine resource name from deployment_metadata.json if available
    for meta_path in ["deployment_metadata.json", "../deployment_metadata.json"]:
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r") as f:
                    data = json.load(f)
                    res_id = data.get("remote_agent_runtime_id")
                    if res_id:
                        return res_id
            except Exception:
                pass
    return None


engine_resource_name = _get_agent_engine_resource_name()
engine_id = engine_resource_name.split("/")[-1] if engine_resource_name else "2353974680475402240"

# Memory service configured for redeployment
memory_service = VertexAiMemoryBankService(
    project="qwiklabs-gcp-01-127c602b3efe",
    location="us-central1",
    agent_engine_id=engine_id,
)

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=engine_resource_name
)


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are an expert Travel & Itinerary Concierge. "
        "You have access to a Python code execution sandbox to safely run Python scripts for complex mathematical calculations, data processing, or custom formatting. "
        "You MUST remember all places of interest, favorite attractions, and preferred visiting locations specified by the user. "
        "Whenever a traveler mentions a place they like, want to visit, or express interest in, call remember_place_of_interest to save it directly into their long-term Memory Bank. "
        "Use load_memory_tool or preload_memory_tool to search and recall past user preferences, places of interest, and personal itinerary notes across sessions. "
        "Use your Firestore tools (search_destinations, get_destination_details, add_destination) "
        "to look up destinations, answer traveler questions, and save new destinations to the database. "
        "Use calculate_trip_budget to compute daily trip budget breakdowns and convert costs to destination currencies. "
        "Use get_live_destination_info to fetch real-time location details, population, and live weather conditions for any city. "
        "Use geocode_address to convert addresses or landmarks into lat/lng coordinates, "
        "use find_nearby_places to discover tourist attractions, restaurants, or museums near a location, "
        "use generate_destination_image to generate visual preview images for landmarks, and "
        "use generate_destination_video to generate short video clips for destinations using Google's Omni model (gemini-omni-flash-preview)."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-3.8-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    after_model_callback=a2ui_callback,
    tools=[
        get_weather,
        get_current_time,
        search_destinations,
        get_destination_details,
        add_destination,
        calculate_trip_budget,
        get_live_destination_info,
        geocode_address,
        find_nearby_places,
        generate_destination_image,
        generate_destination_video,
        search_user_memory,
        remember_place_of_interest,
    ],
)


app = App(
    root_agent=root_agent,
    name="app",
)
