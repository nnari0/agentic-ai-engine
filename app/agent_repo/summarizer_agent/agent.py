"""Summarizer agent – reads uploaded text documents and produces structured summaries."""

from google.adk.agents import LlmAgent

from app import config
from app.agent_repo.summarizer_agent.prompt import SUMMARIZER_AGENT_INSTRUCTION


summarizer_agent = LlmAgent(
    name="summarizer_agent",
    model=config.DEFAULT_LLM_MODEL,
    description="Summarizes uploaded text documents into structured key points and a concise summary.",
    instruction=SUMMARIZER_AGENT_INSTRUCTION,
)
