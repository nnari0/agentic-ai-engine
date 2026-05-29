"""Session state tools for the Summarizer agent.

ADK injects ``tool_context`` automatically when a tool function declares it
as a parameter typed as ``ToolContext``.  The state object it exposes is the
agent's scratchpad for the current session — a key-value store that persists
across turns for the lifetime of the session.

State key prefixes (ADK convention):
  (no prefix)  session-scoped  – default, lives for one session
  user:        user-scoped     – survives session resets (Vertex backend only)
  app:         app-scoped      – shared across all users
  temp:        temporary       – discarded at the end of the current turn
"""

import json

import structlog

from google.adk.tools import ToolContext

logger = structlog.get_logger(__name__)


def save_to_state(key: str, value: str, tool_context: ToolContext) -> str:
    """Save a key-value pair to the current session state.

    Use this to remember facts across turns within the same session,
    for example the topic of the last summarized document or a running
    document count.

    Args:
        key:   State key.  Use ``user:<key>`` to persist across session
               resets (requires Vertex AI session backend).
        value: String value to store.

    Returns:
        Confirmation message.
    """
    tool_context.state[key] = value
    logger.info("State saved", key=key, value=value)
    return f"Saved state['{key}'] = '{value}'."


def load_from_state(key: str, tool_context: ToolContext) -> str:
    """Load a single value from the current session state.

    Args:
        key: The state key to retrieve.

    Returns:
        The stored value, or a message saying the key does not exist.
    """
    value = tool_context.state.get(key)
    logger.info("State loaded", key=key, found=value is not None)
    if value is None:
        return f"No value found for state key '{key}'."
    return f"state['{key}'] = '{value}'"


def list_state(tool_context: ToolContext) -> str:
    """Return all current session state entries as a formatted JSON string.

    Use this to give the user a full view of what the agent has remembered
    during this session.

    Returns:
        JSON-formatted string of the entire state dict.
    """
    state_dict = tool_context.state.to_dict()
    logger.info("State listed", num_keys=len(state_dict))
    if not state_dict:
        return "Session state is empty."
    return json.dumps(state_dict, indent=2, ensure_ascii=False)
