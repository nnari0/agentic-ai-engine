# AI Agents and Orchestration Patterns

## What is an AI Agent?

An AI agent is an autonomous software system that perceives its environment,
makes decisions, and takes actions to achieve a goal. Unlike a single-turn LLM
call, an agent operates in a loop: it receives observations (user messages, tool
results, memory), reasons about them, and produces actions (tool calls, text
responses) until the task is complete.

Key properties of an agent:
- **Autonomy** – acts without step-by-step human instruction
- **Goal-directedness** – pursues a specific objective
- **Tool use** – calls external functions (APIs, search, code execution)
- **Memory** – maintains context across multiple turns

## The ReAct Pattern

ReAct (Reason + Act) is the most common agent execution pattern:

1. **Thought** – the model reasons about the current state and what to do next
2. **Action** – the model selects and calls a tool
3. **Observation** – the tool result is fed back to the model
4. Steps 1–3 repeat until the model produces a final answer

This loop allows agents to decompose complex problems into small steps, verify
intermediate results, and recover from errors.

## Orchestrator / Sub-Agent Pattern

For complex tasks a single agent often falls short. The orchestrator pattern
addresses this by splitting responsibilities:

- **Orchestrator** – the top-level agent that understands the user's goal,
  decomposes it into sub-tasks, and delegates each to a specialist.
- **Sub-agents** – focused agents with narrow skills (e.g., web search,
  code execution, report writing). They receive a specific instruction from
  the orchestrator, execute it, and return the result.

Benefits:
- Each sub-agent's system prompt can be tightly tuned to its skill
- Sub-agents can run in parallel to reduce latency
- The orchestrator maintains a clean separation of concerns

In Google ADK the orchestrator calls sub-agents via `AgentTool`, which wraps
an `LlmAgent` as a callable tool. The orchestrator sees the sub-agent exactly
like any other tool.

## Multi-Agent Communication (A2A)

When agents need to span team or organisation boundaries, the A2A
(Agent-to-Agent) protocol provides a standardised HTTP interface. Each agent
exposes an `AgentCard` (JSON metadata) and a `/run` endpoint. Callers discover
capabilities through the card and interact without knowing the agent's internal
implementation.

A2A enables:
- **Reusability** – an agent deployed by one team can be consumed by another
- **Language independence** – agents can be implemented in any runtime
- **Observability** – each hop produces structured events

## Google ADK Overview

The Google Agent Development Kit (ADK) provides:

| Component | Purpose |
|-----------|---------|
| `LlmAgent` | Wraps a Gemini model with instructions and tools |
| `Runner` | Executes agents, manages sessions and events |
| `ToolContext` | Provides tools access to session state and services |
| `AgentTool` | Embeds one agent as a tool inside another |
| `McpToolset` | Connects to an MCP server for external tools |
| `VertexAiRagRetrieval` | Native RAG retrieval via Vertex AI corpus |
| `GcsArtifactService` | Stores and retrieves binary/text artifacts in GCS |
| `VertexAiMemoryBankService` | Long-term memory across sessions |
