"""A2A client tool – sends a completed summary to the external critic agent."""

import uuid

import httpx

from app import config

# The A2A JSON-RPC endpoint is the base URL (POST /)
# CRITIC_A2A_URL is the agent-card URL, e.g. http://localhost:8001/.well-known/agent.json
_RPC_URL = config.CRITIC_A2A_URL.split("/.well-known")[0].rstrip("/") + "/"


async def critique_summary(summary: str) -> str:
    """Evaluate a summary by calling the external A2A critic agent.

    Sends the summary as a task to the critic agent and returns a structured
    Markdown critique with per-dimension scores and improvement suggestions.

    Args:
        summary: The summary text to be evaluated.

    Returns:
        A Markdown-formatted critique from the critic agent, or an error message
        if the agent is unreachable.
    """
    if not config.CRITIC_A2A_URL:
        return "Critique skipped: CRITIC_A2A_URL is not configured."

    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "message/send",
        "params": {
            "message": {
                "role": "user",
                "parts": [{"kind": "text", "text": summary}],
                "messageId": str(uuid.uuid4()),
            }
        },
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(_RPC_URL, json=payload)
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPError as exc:
        return f"Critique skipped: could not reach critic agent ({exc})."

    if "error" in data:
        msg = data["error"].get("message", "Unknown error")
        return f"Critique agent returned an error: {msg}"

    task = data.get("result", {})

    # Primary: look in artifacts
    for artifact in task.get("artifacts", []):
        for part in artifact.get("parts", []):
            if isinstance(part, dict) and part.get("kind") == "text":
                return part["text"]

    # Fallback: look in the completion status message
    status_msg = task.get("status", {}).get("message") or {}
    for part in status_msg.get("parts", []):
        if isinstance(part, dict) and part.get("kind") == "text":
            return part["text"]

    return "Critique agent responded but returned no text."
