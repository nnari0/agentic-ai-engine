"""Critic agent executor – evaluates AI-generated summaries using Gemini."""

import os

from google import genai

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.server.tasks.task_updater import TaskUpdater
from a2a.types import Part, TextPart

CRITIQUE_PROMPT = """\
You are a senior editor evaluating an AI-generated document summary.

Score the summary on each dimension from 1 (poor) to 10 (excellent):

- **Accuracy**: Does it faithfully represent the source content without hallucinating?
- **Completeness**: Does it capture all key points?
- **Clarity**: Is it easy to understand?
- **Conciseness**: Is it appropriately brief without losing meaning?

Then provide:
- **Overall Score** (1–10): Weighted average
- **Strengths**: What the summary does well (2–3 bullet points)
- **Improvements**: Specific, actionable suggestions (2–3 bullet points)

Return your evaluation in clean Markdown.

---

Summary to evaluate:

{summary}
"""

_MODEL = os.getenv("CRITIC_LLM_MODEL", "gemini-2.5-flash")

# Uses Application Default Credentials (GOOGLE_APPLICATION_CREDENTIALS).
# Set GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION in the environment.
_client = genai.Client(
    vertexai=True,
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "europe-north1"),
)


class CriticAgentExecutor(AgentExecutor):
    """Evaluates summaries using Gemini via Vertex AI and publishes the critique as a task artifact."""

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.start_work()

        summary = context.get_user_input()
        if not summary.strip():
            await updater.failed(
                message=updater.new_agent_message(
                    parts=[Part(root=TextPart(text="No summary text received."))]
                )
            )
            return

        try:
            response = await _client.aio.models.generate_content(
                model=_MODEL,
                contents=CRITIQUE_PROMPT.format(summary=summary),
            )
            critique_text = response.text or "No critique generated."
        except Exception as exc:
            await updater.failed(
                message=updater.new_agent_message(
                    parts=[Part(root=TextPart(text=f"Critique failed: {exc}"))]
                )
            )
            return

        await updater.add_artifact(
            parts=[Part(root=TextPart(text=critique_text))],
            name="critique",
        )
        await updater.complete()

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        await updater.cancel()
