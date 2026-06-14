from app.agent_repo.summarizer_agent import agent
from app.agent_repo.summarizer_agent.agent import root_agent, summarizer_agent

# ``agent`` and ``root_agent`` are re-exported so ADK's agent loader can resolve
# the entry-point agent both as ``<pkg>.agent.root_agent`` (CLI eval) and as
# ``<pkg>.root_agent`` (web).
__all__ = ["agent", "root_agent", "summarizer_agent"]
