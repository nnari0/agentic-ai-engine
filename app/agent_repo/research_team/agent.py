"""Research Report Team – coordinator agent.

The coordinator is the single entry point exposed in the UI.
It delegates to two specialist sub-agents via AgentTool:

  web_researcher  – fetches and extracts information from web pages
  report_writer   – compiles findings into a structured Markdown report
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

from app import config
from app.agent_repo.research_team.prompt import COORDINATOR_INSTRUCTION
from app.agent_repo.research_team.sub_agents import report_writer, web_researcher

research_coordinator = LlmAgent(
    name="research_coordinator",
    model=config.DEFAULT_LLM_MODEL,
    description=(
        "Orchestrates a research team: fetches web sources and compiles "
        "the findings into a structured report."
    ),
    instruction=COORDINATOR_INSTRUCTION,
    tools=[
        AgentTool(agent=web_researcher),
        AgentTool(agent=report_writer),
    ],
)
