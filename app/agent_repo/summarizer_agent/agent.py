"""Summarizer agent – reads uploaded text documents and produces structured summaries."""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams

from app import config
from app.agent_repo.summarizer_agent.critique_tool import critique_summary
from app.agent_repo.summarizer_agent.prompt import SUMMARIZER_AGENT_INSTRUCTION

# google_search cannot be combined with function-calling tools (McpToolset) —
# the Gemini API only allows multiple tools when they are all search tools.
# Web lookup is covered by the fetch_page MCP tool instead.
_tools = [critique_summary]

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
)
