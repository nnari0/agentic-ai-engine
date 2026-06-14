"""Google Search exposed as an AgentTool for the Summarizer agent.

Why an AgentTool wrapper?
-------------------------
The Gemini API rejects any single request that mixes the native
``google_search`` tool with function-calling tools (``McpToolset``,
``critique_summary``, ``save_artifact`` …) — when multiple tools are
present they must *all* be search tools.

Wrapping a search-only ``LlmAgent`` in an ``AgentTool`` sidesteps this:
the inner agent runs in its **own** LLM request where ``google_search``
is the only tool, while the parent Summarizer agent sees a plain
function call (``google_search_agent``).  This keeps web search available
without breaking any of the summarizer's other tools.
"""

from google.adk.agents import LlmAgent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool

from app import config

_SEARCH_AGENT_INSTRUCTION = """\
You are a web search specialist.  Given a query, use the `google_search`
tool to find current, relevant information on the web and return a concise,
factual answer.

- Always ground your answer in the search results — never rely on prior
  knowledge alone.
- Summarise the key findings in a few sentences or bullet points.
- Include the source URLs you used so the caller can cite them.
- If the search yields nothing useful, say so plainly.
"""

# Search-only agent: google_search is its single tool, so its requests
# never mix search with function-calling tools.
google_search_agent = LlmAgent(
    name="google_search_agent",
    model=config.DEFAULT_LLM_MODEL,
    description=(
        "Performs a live Google web search and returns a concise, sourced "
        "answer for the given query."
    ),
    instruction=_SEARCH_AGENT_INSTRUCTION,
    tools=[google_search],
)

# Expose the search agent as a function-call tool the Summarizer can invoke
# alongside its other function-calling tools.
google_search_tool = AgentTool(agent=google_search_agent)
