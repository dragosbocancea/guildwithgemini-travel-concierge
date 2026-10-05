# Travel & Itinerary Concierge Agent

A conversational AI travel concierge powered by Google Agent Development Kit (ADK), Gemini, and Google Cloud services. The agent helps travelers discover destinations, research attractions, save personal travel preferences, calculate trip budgets, and generate visual preview media.

![Travel Concierge Demo](demo.gif)

---

## 🌟 Capabilities & Implemented Tools

The agent is built using Python ADK (`gemini-3.8-flash`) and integrates the following Google Cloud services and tools:

- **🧠 Vertex AI Memory Bank Service**: Persists traveler preferences, favorite attractions, and pace notes across sessions (`remember_place_of_interest`, `search_user_memory`).
- **🗄️ Google Cloud Firestore**: Queries and manages a curated database of travel destinations (`search_destinations`, `get_destination_details`, `add_destination`).
- **🎨 Vertex AI Image Generation**: Generates landmark and destination preview images using Google's `imagen-3.0-generate-002` model (`generate_destination_image`).
- **🎬 Vertex AI Omni Model Video Generation**: Generates scenic destination video clips using `gemini-omni-flash-preview` in the `global` location (`generate_destination_video`).
- **☁️ Google Cloud Storage (GCS)**: Stores generated image and video assets in a public bucket for rendering in the UI.
- **📍 Google Maps Platform**:
  - **Geocoding API**: Converts landmarks and addresses into geographic coordinates (`geocode_address`).
  - **Places API**: Discovers nearby attractions, restaurants, and points of interest (`find_nearby_places`).
- **💻 Vertex AI Code Execution Sandbox**: Safely executes Python code inside an isolated sandbox to calculate exact trip budgets and expense breakdowns (`calculate_trip_budget`).
- **🌦️ Live Destination Info & Weather**: Retrieves live weather conditions and location metadata (`get_live_destination_info`).
- **📱 Agent-to-UI (A2UI)**: Formats structured UI payloads (cards, columns, rows, images) rendered dynamically by the web frontend via an `after_model_callback`.

---

## 🏗️ Architecture Overview

- **Agent Backend (`app/`)**: Defined using `google-adk`, running on Google Cloud Agent Engine / Reasoning Engine with `A2uiSchemaManager`.
- **Frontend (`frontend/`)**: Plain HTML/CSS chat UI served by a minimal FastAPI backend utilizing `a2a-sdk` for A2A proxying.

---

## 🚀 Setup & Local Execution

### Prerequisites

- Python 3.11+
- `uv` or `pip`
- Google Cloud Project with Vertex AI, Firestore, GCS, and Maps APIs enabled

### 1. Environment Setup

Copy or create an environment configuration file:

```bash
export GOOGLE_CLOUD_PROJECT="<your-gcp-project-id>"
export GOOGLE_CLOUD_REGION="us-central1"
export GOOGLE_MAPS_API_KEY="<your-google-maps-api-key>"
```

### 2. Install Dependencies

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install backend dependencies
pip install -e .

# Install frontend dependencies
cd frontend
pip install -r requirements.txt
cd ..
```

### 3. Run the Frontend Locally

Set the target reasoning engine resource name and agent directory, then start the FastAPI server:

```bash
export AGENT_ENGINE_RESOURCE_NAME="projects/<project-number>/locations/us-east1/reasoningEngines/<engine-id>"
export AGENT_DIRECTORY="app"

python3 -m uvicorn frontend.main:app --host 0.0.0.0 --port 8080
```

Open a browser and navigate to port `8080` on your local host to interact with the concierge.

---

## 📦 Deployment Instructions

### Deploy Agent to Agent Runtime

```bash
agents-cli deploy --project <your-gcp-project-id> --no-confirm-project
```

### Deploy Frontend to Cloud Run

```bash
gcloud run deploy travel-concierge-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="projects/<project-number>/locations/us-east1/reasoningEngines/<engine-id>",AGENT_DIRECTORY="app"
```
