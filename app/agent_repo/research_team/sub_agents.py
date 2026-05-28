"""Sub-agents for the Research Report Team.

web_researcher  – fetches web pages via the MCP Fetch server and extracts
                  the information relevant to a given research goal.
report_writer   – compiles gathered research notes into a structured report.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset

from app import config
from app.agent_repo.research_team.prompt import REPORT_WRITER_INSTRUCTION, WEB_RESEARCHER_INSTRUCTION

# fetch_page is only available when the MCP Fetch server is running.
_researcher_tools = []
if config.MCP_FETCH_URL:
    _researcher_tools.append(
        McpToolset(connection_params=SseConnectionParams(url=config.MCP_FETCH_URL))
    )

web_researcher = LlmAgent(
    name="web_researcher",
    model=config.DEFAULT_LLM_MODEL,
    description=(
        "Fetches a web page via the MCP Fetch server and extracts key facts "
        "relevant to a given research goal."
    ),
    instruction=WEB_RESEARCHER_INSTRUCTION,
    tools=_researcher_tools,
)

report_writer = LlmAgent(
    name="report_writer",
    model=config.DEFAULT_LLM_MODEL,
    description="Compiles research notes into a polished, structured Markdown report.",
    instruction=REPORT_WRITER_INSTRUCTION,
)
