"""Unit tests for the summarizer agent prompt structure."""

from app.agent_repo.summarizer_agent.prompt import SUMMARIZER_AGENT_INSTRUCTION


REQUIRED_SECTIONS = [
    "## 1. Role",
    "## 2. Policies",
    "## 3. Workflow",
    "## 4. Output Format",
    "## 5. Critique Loop",
    "## 6. Tools",
    "## 7. Example",
]

REQUIRED_TOOLS = [
    "critique_summary",
    "save_artifact",
    "load_artifact",
    "list_artifacts",
    "retrieve_from_corpus",
    "preload_memory",
    "load_memory",
]


def test_all_sections_present():
    for section in REQUIRED_SECTIONS:
        assert section in SUMMARIZER_AGENT_INSTRUCTION, f"Missing section: {section!r}"


def test_all_tools_documented():
    for tool in REQUIRED_TOOLS:
        assert tool in SUMMARIZER_AGENT_INSTRUCTION, f"Tool not documented: {tool!r}"


def test_output_format_has_four_sections():
    for heading in ["### Title / Topic", "### Key Points", "### Summary", "### Takeaway"]:
        assert heading in SUMMARIZER_AGENT_INSTRUCTION, f"Missing output heading: {heading!r}"


def test_critique_loop_mandatory():
    assert "Do not skip the critique" in SUMMARIZER_AGENT_INSTRUCTION
