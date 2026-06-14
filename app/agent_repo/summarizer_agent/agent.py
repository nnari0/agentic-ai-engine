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
from app.agent_repo.summarizer_agent.search_tool import google_search_tool
from app.agent_repo.summarizer_agent.state_tools import save_to_state, load_from_state, list_state
from app.context.artifacts.artifact_tools import save_artifact, load_artifact, list_artifacts
from app.context.memory.memory_bank_handler import memory_bank_handler
from app.context.metrics import compose, on_after_agent, on_after_tool, on_before_model, on_after_model
from app.context.rag.rag_retrieval_tool import retrieve_from_corpus

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


# google_search cannot be combined with function-calling tools (McpToolset,
# critique_summary, …) in the same Gemini request — when several tools are
# present they must all be search tools.  We therefore expose web search via
# google_search_tool, an AgentTool wrapping a search-only sub-agent: the inner
# agent runs in its own request (google_search is its only tool), while the
# summarizer invokes it as an ordinary function call.
_tools = [
    # Live web search via a search-only sub-agent (AgentTool wrapper).
    google_search_tool,
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
    # GCS artifact storage: persist summaries and findings as downloadable files.
    save_artifact,
    load_artifact,
    list_artifacts,
    # RAG corpus search – plain function call, compatible with all other tools.
    retrieve_from_corpus,
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
    after_agent_callback=compose(_memorize_session, on_after_agent),
    after_tool_callback=on_after_tool,
    before_model_callback=on_before_model,
    after_model_callback=on_after_model,
)

# ADK's CLI/web agent loader discovers the entry-point agent through a
# module-level attribute named ``root_agent``. Expose the summarizer under
# that name so `adk web` and `adk eval` can load it.
root_agent = summarizer_agent
