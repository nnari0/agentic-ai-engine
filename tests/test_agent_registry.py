"""Unit tests for the agent registry."""

import pytest
from app.agent_repo.agent_registry import list_agents, get_agent


def test_list_agents_returns_all():
    agents = list_agents()
    ids = [a["id"] for a in agents]
    assert "greeting_agent" in ids
    assert "summarizer_agent" in ids
    assert "research_orchestrator" in ids


def test_agent_capabilities_flags():
    agents = {a["id"]: a for a in list_agents()}

    assert agents["summarizer_agent"]["has_memory"] is True
    assert agents["summarizer_agent"]["has_artifacts"] is True
    assert agents["summarizer_agent"]["has_rag"] is True

    assert agents["greeting_agent"]["has_memory"] is False


def test_get_agent_returns_registered_agent():
    agent = get_agent("summarizer_agent")
    assert agent is not None
    assert agent.name == "summarizer_agent"


def test_get_agent_unknown_raises():
    with pytest.raises(KeyError):
        get_agent("nonexistent_agent")
