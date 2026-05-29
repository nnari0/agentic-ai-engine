"""Agent listing API – v1."""

import base64

from fastapi import APIRouter, Query
from fastapi.responses import Response
from pydantic import BaseModel

from app.agent_repo import list_agents
from app import config
from app.context.artifacts.artifact_service_handler import artifact_service_handler
from app.context.memory.memory_bank_handler import memory_bank_handler
from app.context.rag.rag_engine_handler import rag_engine_handler
from app.handlers.session_handler import session_handler

agent_router = APIRouter(prefix="/api/v1", tags=["agents"])


@agent_router.get("/agents")
async def get_agents() -> dict:
    """Return all registered agents and the current default."""
    return {"agents": list_agents(), "default": config.DEFAULT_AGENT_ID}


@agent_router.get("/artifacts")
async def get_artifacts(agent_id: str = Query(..., description="Agent ID")) -> dict:
    """Return all artifact filenames for the given agent's current session."""
    app_name = f"{agent_id}_app"
    session_id = session_handler._agent_session_mapping.get(agent_id)
    if not session_id:
        return {"artifacts": []}
    keys = await artifact_service_handler.service.list_artifact_keys(
        app_name=app_name,
        user_id=config.USER_ID,
        session_id=session_id,
    )
    return {"artifacts": keys}


@agent_router.get("/artifacts/download")
async def download_artifact(
    agent_id: str = Query(..., description="Agent ID"),
    filename: str = Query(..., description="Artifact filename"),
) -> Response:
    """Download a single artifact by filename."""
    app_name = f"{agent_id}_app"
    session_id = session_handler._agent_session_mapping.get(agent_id)
    if not session_id:
        return Response(content="No session found", status_code=404)

    part = await artifact_service_handler.service.load_artifact(
        app_name=app_name,
        user_id=config.USER_ID,
        session_id=session_id,
        filename=filename,
    )
    if part is None:
        return Response(content="Artifact not found", status_code=404)

    if part.text:
        data = part.text.encode("utf-8")
        mime = "text/plain"
    elif part.inline_data:
        data = part.inline_data.data
        mime = part.inline_data.mime_type or "application/octet-stream"
    else:
        return Response(content="Artifact has no content", status_code=404)

    return Response(
        content=data,
        media_type=mime,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@agent_router.get("/memories")
async def get_memories(
    agent_id: str = Query(..., description="Agent ID"),
    query: str = Query("*", description="Search query for memory facts"),
) -> dict:
    """Return memory facts for the given agent's user scope."""
    app_name = f"{agent_id}_app"
    if memory_bank_handler.service is None:
        return {"memories": [], "error": "Memory bank not available"}
    try:
        result = await memory_bank_handler.service.search_memory(
            app_name=app_name,
            user_id=config.USER_ID,
            query=query,
        )
        facts = [
            {
                "text": entry.content.parts[0].text if entry.content and entry.content.parts else "",
                "timestamp": entry.timestamp or "",
            }
            for entry in (result.memories or [])
        ]
        return {"memories": facts}
    except Exception as e:
        return {"memories": [], "error": str(e)}


# ── RAG corpus management ───────────────────────────────────────────────


@agent_router.get("/rag/files")
async def get_rag_files() -> dict:
    """List all files in the RAG corpus."""
    if not rag_engine_handler.available:
        return {"files": [], "error": "RAG engine not available"}
    return {"files": await rag_engine_handler.list_files()}


class RagImportRequest(BaseModel):
    gcs_uris: list[str]


@agent_router.post("/rag/import")
async def import_rag_files(body: RagImportRequest) -> dict:
    """Import files from GCS URIs into the RAG corpus."""
    if not rag_engine_handler.available:
        return {"status": "error", "message": "RAG engine not available"}
    return await rag_engine_handler.import_files(body.gcs_uris)


@agent_router.delete("/rag/files")
async def delete_rag_file(
    file_name: str = Query(..., description="RAG file resource name"),
) -> dict:
    """Delete a file from the RAG corpus."""
    if not rag_engine_handler.available:
        return {"status": "error", "message": "RAG engine not available"}
    return await rag_engine_handler.delete_file(file_name)


# ── Session state inspection ────────────────────────────────────────────


@agent_router.get("/session/state")
async def get_session_state(agent_id: str = Query(..., description="Agent ID")) -> dict:
    """Return the current session state (scratchpad) for an agent.

    The state is the key-value store the agent reads and writes during a session.
    It is populated by the save_to_state / load_from_state tools.
    """
    app_name = f"{agent_id}_app"
    session_id = session_handler._agent_session_mapping.get(agent_id)
    if not session_id:
        return {"state": {}, "session_id": None}

    session = await session_handler.service.get_session(
        app_name=app_name,
        user_id=config.USER_ID,
        session_id=session_id,
    )
    if session is None:
        return {"state": {}, "session_id": session_id}

    return {"state": session.state, "session_id": session_id}


@agent_router.get("/session/events")
async def get_session_events(
    agent_id: str = Query(..., description="Agent ID"),
    limit: int = Query(20, description="Maximum number of recent events to return"),
) -> dict:
    """Return recent session events (conversation history) for an agent.

    Each event captures one turn: a user message, an agent response, or a
    tool call/result.  This endpoint is useful for investigating the session
    flow and understanding what happened in a conversation.
    """
    app_name = f"{agent_id}_app"
    session_id = session_handler._agent_session_mapping.get(agent_id)
    if not session_id:
        return {"events": [], "session_id": None}

    session = await session_handler.service.get_session(
        app_name=app_name,
        user_id=config.USER_ID,
        session_id=session_id,
    )
    if session is None:
        return {"events": [], "session_id": session_id}

    events = []
    for ev in (session.events or [])[-limit:]:
        text = ""
        if ev.content and ev.content.parts:
            text = " ".join(p.text for p in ev.content.parts if p.text).strip()
        state_delta = {}
        if ev.actions and ev.actions.state_delta:
            state_delta = dict(ev.actions.state_delta)
        events.append({
            "author": ev.author,
            "text": text[:500] if text else "",
            "state_delta": state_delta,
            "timestamp": ev.timestamp,
        })

    return {"events": events, "session_id": session_id}
