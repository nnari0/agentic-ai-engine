"""Greeting agent – welcomes students and helps them get started."""

from google.adk.agents import LlmAgent

from app import config
from app.agent_repo.greeting_agent.prompt import GREETING_AGENT_INSTRUCTION
from app.context.metrics import on_after_agent, on_before_model, on_after_model

greeting_agent = LlmAgent(
    name="greeting_agent",
    model=config.DEFAULT_LLM_MODEL,
    description="Agent that greets users and answers basic questions about itself.",
    instruction=GREETING_AGENT_INSTRUCTION,
    after_agent_callback=on_after_agent,
    before_model_callback=on_before_model,
    after_model_callback=on_after_model,
)

# Exposed under ``root_agent`` so ADK's CLI/web loader can discover it.
root_agent = greeting_agent
