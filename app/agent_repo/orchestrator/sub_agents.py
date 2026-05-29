"""Sub-agents for the Research Orchestrator.

researcher_agent – fetches web pages via the MCP Fetch server and extracts
                   information relevant to a given research goal.
writer_agent     – compiles gathered research notes into a structured report.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from app import config
from app.agent_repo.orchestrator.prompt import REPORT_WRITER_INSTRUCTION, WEB_RESEARCHER_INSTRUCTION
from app.context.artifacts.artifact_tools import save_artifact, list_artifacts
from app.context.rag.rag_retrieval_tool import retrieve_from_corpus

# fetch_page is only available when the MCP Fetch server is running.
_researcher_tools = [retrieve_from_corpus]
if config.MCP_FETCH_URL:
    _researcher_tools.append(
        McpToolset(connection_params=SseConnectionParams(url=config.MCP_FETCH_URL))
    )

researcher_agent = LlmAgent(
    name="researcher_agent",
    model=config.DEFAULT_LLM_MODEL,
    description=(
        "Fetches a web page via the MCP Fetch server and extracts key facts "
        "relevant to a given research goal."
    ),
    instruction=WEB_RESEARCHER_INSTRUCTION,
    tools=_researcher_tools,
)

writer_agent = LlmAgent(
    name="writer_agent",
    model=config.DEFAULT_LLM_MODEL,
    description="Compiles research notes into a polished, structured Markdown report.",
    instruction=REPORT_WRITER_INSTRUCTION,
    tools=[save_artifact, list_artifacts],
)
