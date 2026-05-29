"""Prometheus metrics and OpenTelemetry span enrichment for agent observability.

Counters exposed at GET /metrics
---------------------------------
  agent_turns_total         — completed agent turns, labelled by agent_name
  tool_calls_total          — tool invocations, labelled by agent_name + tool_name
  llm_requests_total        — LLM API calls, labelled by agent_name + model
  llm_input_tokens_total    — cumulative input tokens, labelled by agent_name + model
  llm_output_tokens_total   — cumulative output tokens, labelled by agent_name + model

OTel span attributes (added to the active span by on_before_model / on_after_model)
----------------------------------------------------------------------------------
  Before call:  llm.model, llm.message_count, llm.prompt_chars,
                llm.system_instruction_chars, llm.available_tools,
                llm.temperature, llm.max_output_tokens, llm.top_p
  After call:   llm.model_version, llm.finish_reason,
                llm.input_tokens, llm.output_tokens, llm.total_tokens,
                llm.thinking_tokens, llm.response_chars,
                llm.last_user_message_preview (first 200 chars)

Usage
-----
  from app.context.metrics import (
      compose, on_after_agent, on_after_tool, on_before_model, on_after_model
  )

  agent = LlmAgent(
      ...
      after_agent_callback=compose(_memorize_session, on_after_agent),
      after_tool_callback=on_after_tool,
      before_model_callback=on_before_model,
      after_model_callback=on_after_model,
  )
"""

from __future__ import annotations

import contextvars
from typing import Any

from opentelemetry import trace
from prometheus_client import Counter

from google.adk.agents.callback_context import CallbackContext

# ── Prometheus counters ────────────────────────────────────────────────────────

agent_turns_total = Counter(
    "agent_turns_total",
    "Total completed agent turns",
    ["agent_name"],
)

tool_calls_total = Counter(
    "tool_calls_total",
    "Total tool calls made by agents",
    ["agent_name", "tool_name"],
)

llm_requests_total = Counter(
    "llm_requests_total",
    "Total LLM API calls",
    ["agent_name", "model"],
)

llm_input_tokens_total = Counter(
    "llm_input_tokens_total",
    "Cumulative input tokens consumed",
    ["agent_name", "model"],
)

llm_output_tokens_total = Counter(
    "llm_output_tokens_total",
    "Cumulative output tokens generated",
    ["agent_name", "model"],
)

# ── Internal context var: passes model name from before→after model callback ──

_current_model: contextvars.ContextVar[str] = contextvars.ContextVar(
    "llm_current_model", default="unknown"
)


# ── Helper ─────────────────────────────────────────────────────────────────────

def _text_from_content(content: Any, max_chars: int = 200) -> str:
    """Extract plain text from a Content / str / list, truncated to max_chars."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content[:max_chars]
    parts = getattr(content, "parts", None)
    if parts:
        joined = " ".join(
            p.text for p in parts if getattr(p, "text", None)
        )
        return joined[:max_chars]
    return ""


# ── Agent-level callbacks ──────────────────────────────────────────────────────

async def on_after_agent(callback_context: CallbackContext) -> None:
    """Count completed agent turns."""
    agent_turns_total.labels(agent_name=callback_context.agent_name).inc()


async def on_after_tool(tool, args, tool_context, tool_response):
    """Count tool invocations by name and agent."""
    try:
        agent_name = tool_context.agent_name
    except AttributeError:
        agent_name = "unknown"
    tool_calls_total.labels(agent_name=agent_name, tool_name=tool.name).inc()
    return None


# ── Model-level callbacks ──────────────────────────────────────────────────────

async def on_before_model(callback_context: CallbackContext, llm_request) -> None:
    """Enrich the active OTel span with LLM request metadata before the API call."""
    model = getattr(llm_request, "model", None) or "unknown"
    _current_model.set(model)

    span = trace.get_current_span()
    if not span.is_recording():
        return None

    span.set_attribute("llm.agent_name", callback_context.agent_name)
    span.set_attribute("llm.model", model)

    # Generation config
    config = getattr(llm_request, "config", None)
    if config:
        temp = getattr(config, "temperature", None)
        if temp is not None:
            span.set_attribute("llm.temperature", float(temp))
        max_out = getattr(config, "max_output_tokens", None)
        if max_out is not None:
            span.set_attribute("llm.max_output_tokens", int(max_out))
        top_p = getattr(config, "top_p", None)
        if top_p is not None:
            span.set_attribute("llm.top_p", float(top_p))

        # System instruction character count + truncated preview
        sys_instr = getattr(config, "system_instruction", None)
        if sys_instr:
            instr_text = _text_from_content(sys_instr, max_chars=10_000)
            span.set_attribute("llm.system_instruction_chars", len(instr_text))
            span.set_attribute("llm.system_instruction_preview", instr_text[:200])

    # Conversation contents
    contents = getattr(llm_request, "contents", None) or []
    span.set_attribute("llm.message_count", len(contents))

    prompt_chars = sum(
        len(p.text)
        for msg in contents
        for p in (getattr(msg, "parts", None) or [])
        if getattr(p, "text", None)
    )
    span.set_attribute("llm.prompt_chars", prompt_chars)

    # Preview of the last user message
    for msg in reversed(contents):
        if getattr(msg, "role", None) == "user":
            preview = _text_from_content(msg, max_chars=200)
            if preview:
                span.set_attribute("llm.last_user_message_preview", preview)
            break

    # Available tools
    tools_dict = getattr(llm_request, "tools_dict", None) or {}
    if tools_dict:
        span.set_attribute("llm.available_tools", ", ".join(sorted(tools_dict.keys())))

    return None


async def on_after_model(callback_context: CallbackContext, llm_response) -> None:
    """Enrich the active OTel span with response metadata and update token counters."""
    agent_name = callback_context.agent_name
    model = _current_model.get()

    span = trace.get_current_span()
    recording = span.is_recording()

    # Model version (e.g. "gemini-2.5-flash-001")
    model_version = getattr(llm_response, "model_version", None)
    if model_version and recording:
        span.set_attribute("llm.model_version", model_version)

    # Finish reason
    finish_reason = getattr(llm_response, "finish_reason", None)
    if finish_reason is not None and recording:
        span.set_attribute("llm.finish_reason", str(finish_reason))

    # Response content character count
    content = getattr(llm_response, "content", None)
    if content and recording:
        response_chars = sum(
            len(p.text)
            for p in (getattr(content, "parts", None) or [])
            if getattr(p, "text", None)
        )
        span.set_attribute("llm.response_chars", response_chars)

    # Token usage — OTel attributes + Prometheus counters
    usage = getattr(llm_response, "usage_metadata", None)
    input_tokens = 0
    output_tokens = 0

    if usage:
        input_tokens = getattr(usage, "prompt_token_count", 0) or 0
        output_tokens = getattr(usage, "candidates_token_count", 0) or 0
        total_tokens = getattr(usage, "total_token_count", 0) or 0
        thinking_tokens = getattr(usage, "thoughts_token_count", 0) or 0

        if recording:
            span.set_attribute("llm.input_tokens", input_tokens)
            span.set_attribute("llm.output_tokens", output_tokens)
            span.set_attribute("llm.total_tokens", total_tokens)
            if thinking_tokens:
                span.set_attribute("llm.thinking_tokens", thinking_tokens)

    llm_requests_total.labels(agent_name=agent_name, model=model).inc()
    if input_tokens:
        llm_input_tokens_total.labels(agent_name=agent_name, model=model).inc(input_tokens)
    if output_tokens:
        llm_output_tokens_total.labels(agent_name=agent_name, model=model).inc(output_tokens)

    return None


# ── Callback composer ──────────────────────────────────────────────────────────

def compose(*callbacks):
    """Combine multiple after-agent callbacks into one callable.

    ADK's after_agent_callback accepts a single function.  Use this helper
    when an agent already has a callback and you need to add another:

        after_agent_callback=compose(_memorize_session, on_after_agent)
    """
    async def _combined(callback_context: CallbackContext):
        for cb in callbacks:
            await cb(callback_context)
    return _combined
