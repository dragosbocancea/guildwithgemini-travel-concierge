import os
from google.adk.cli.service_registry import get_service_registry
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService

# Set the Agent Engine ID for auto-detection in service_factory
if "GOOGLE_CLOUD_AGENT_ENGINE_ID" not in os.environ:
    os.environ["GOOGLE_CLOUD_AGENT_ENGINE_ID"] = "7882988472636538880"

def custom_memory_factory(uri: str, **kwargs):
    return VertexAiMemoryBankService(
        project=os.environ.get("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-01-127c602b3efe"),
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
        agent_engine_id="7882988472636538880",
    )

# Register for memory scheme
get_service_registry().register_memory_service("memory", custom_memory_factory)
