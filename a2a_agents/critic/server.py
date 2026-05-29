"""A2A Summary Critic Server.

Exposes a critique skill over the A2A protocol (JSON-RPC over HTTP).
The Summarizer agent calls this server as an external evaluation step.

Run locally:
    python server.py   (reads .env from the project root automatically)

Docker:
    docker build -t a2a-critic . && docker run -p 8001:8001 \
      -v ~/.config/gcloud:/root/.config/gcloud:ro \
      -e GOOGLE_APPLICATION_CREDENTIALS=/root/.config/gcloud/application_default_credentials.json \
      -e GOOGLE_CLOUD_PROJECT=<project-id> \
      a2a-critic

HuggingFace Spaces:
    Set GOOGLE_APPLICATION_CREDENTIALS_JSON, GOOGLE_CLOUD_PROJECT, and AGENT_URL secrets.
"""

import os
from pathlib import Path

# Load .env for local development — walk up to the project root.
# In Docker / Cloud Run the file won't exist and this is a no-op.
try:
    from dotenv import load_dotenv
    for _parent in [Path(__file__).parent, *Path(__file__).parents]:
        if (_parent / ".env").exists():
            load_dotenv(_parent / ".env")
            break
except ImportError:
    pass

import uvicorn
from a2a.server.apps.jsonrpc.fastapi_app import A2AFastAPIApplication
from a2a.server.events.in_memory_queue_manager import InMemoryQueueManager
from a2a.server.request_handlers.default_request_handler import DefaultRequestHandler
from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentSkill

from agent import CriticAgentExecutor

HOST: str = os.getenv("A2A_HOST", "0.0.0.0")
PORT: int = int(os.getenv("A2A_PORT", "8001"))
# Public URL reported in the Agent Card (update when deployed to HuggingFace)
AGENT_URL: str = os.getenv("AGENT_URL", f"http://localhost:{PORT}/")

agent_card = AgentCard(
    name="Summary Critic",
    description=(
        "Evaluates AI-generated summaries for accuracy, completeness, "
        "clarity, and conciseness. Returns a structured Markdown critique "
        "with per-dimension scores and improvement suggestions."
    ),
    url=AGENT_URL,
    version="1.0.0",
    capabilities=AgentCapabilities(streaming=False),
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
    skills=[
        AgentSkill(
            id="critique_summary",
            name="Critique Summary",
            description=(
                "Receives a summary text and returns a structured critique "
                "with scores (1–10) on accuracy, completeness, clarity, and "
                "conciseness, plus actionable improvement suggestions."
            ),
            tags=["evaluation", "critique", "summary", "quality"],
            input_modes=["text/plain"],
            output_modes=["text/plain"],
        )
    ],
)

request_handler = DefaultRequestHandler(
    agent_executor=CriticAgentExecutor(),
    task_store=InMemoryTaskStore(),
    queue_manager=InMemoryQueueManager(),
)

app = A2AFastAPIApplication(
    agent_card=agent_card,
    http_handler=request_handler,
).build()

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT)
