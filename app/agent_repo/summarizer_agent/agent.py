"""Summarizer agent – reads uploaded text documents and produces structured summaries."""

import structlog

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools import preload_memory, load_memory
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

from app import config
from app.agent_repo.summarizer_agent.critique_tool import critique_summary
from app.agent_repo.summarizer_agent.prompt import SUMMARIZER_AGENT_INSTRUCTION
from app.agent_repo.summarizer_agent.state_tools import save_to_state, load_from_state, list_state
from app.context.memory.memory_bank_handler import memory_bank_handler

logger = structlog.get_logger(__name__)


async def _memorize_session(callback_context: CallbackContext) -> None:
    """After-agent callback: persist the current session to the Memory Bank.

    Called automatically by the ADK runner after every agent turn when a
    memory service is wired into the runner.  Stores the full conversation
    so the agent can recall it in future sessions via preload_memory /
    load_memory.
    """
    if memory_bank_handler.service is None:
        return
    try:
        await callback_context.add_session_to_memory()
        logger.info("Session saved to memory bank")
    except Exception:
        logger.warning("Failed to save session to memory bank", exc_info=True)


# google_search cannot be combined with function-calling tools (McpToolset) —
# the Gemini API only allows multiple tools when they are all search tools.
# Web lookup is covered by the fetch_page MCP tool instead.
_tools = [
    # Long-term memory: automatically injects relevant past conversations
    # into each request and lets the model search memory on demand.
    preload_memory,
    load_memory,
    # Quality evaluation via external A2A critic agent.
    critique_summary,
    # Short-term session scratchpad.
    save_to_state,
    load_from_state,
    list_state,
]

if config.MCP_FETCH_URL:
    _tools.append(
        McpToolset(
            connection_params=SseConnectionParams(url=config.MCP_FETCH_URL)
        )
    )

summarizer_agent = LlmAgent(
    name="summarizer_agent",
    model=config.DEFAULT_LLM_MODEL,
    description="Summarizes uploaded text documents into structured key points and a concise summary.",
    instruction=SUMMARIZER_AGENT_INSTRUCTION,
    tools=_tools,
    # Save the session to the Memory Bank after every agent turn so past
    # summaries and conversations are available in future sessions.
    after_agent_callback=_memorize_session,
)
