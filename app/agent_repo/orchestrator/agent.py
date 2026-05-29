"""Research Orchestrator – top-level orchestrator agent.

The orchestrator is the single entry point exposed in the UI.
It delegates to two specialist sub-agents via AgentTool:

  researcher_agent – fetches and extracts information from web pages
  writer_agent     – compiles findings into a structured Markdown report
"""

from google.adk.agents import LlmAgent
from google.adk.tools import AgentTool

from app import config
from app.agent_repo.orchestrator.prompt import COORDINATOR_INSTRUCTION
from app.agent_repo.orchestrator.sub_agents import researcher_agent, writer_agent
from app.context.metrics import on_after_agent, on_before_model, on_after_model

research_orchestrator = LlmAgent(
    name="research_orchestrator",
    model=config.DEFAULT_LLM_MODEL,
    description=(
        "Orchestrates a research pipeline: delegates web fetching to a "
        "researcher sub-agent and report writing to a writer sub-agent."
    ),
    instruction=COORDINATOR_INSTRUCTION,
    tools=[
        AgentTool(agent=researcher_agent),
        AgentTool(agent=writer_agent),
    ],
    after_agent_callback=on_after_agent,
    before_model_callback=on_before_model,
    after_model_callback=on_after_model,
)
