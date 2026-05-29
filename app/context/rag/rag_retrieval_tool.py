"""RAG retrieval tool – plain async function wrapping rag.retrieval_query().

Design note
-----------
The ADK's ``VertexAiRagRetrieval`` injects a native ``types.Tool(retrieval=…)``
into the Gemini API request for Gemini 2+ models.  The Gemini API does **not**
allow mixing a retrieval tool with function-calling tools in the same request,
so any agent that also has tools like ``save_artifact`` or ``critique_summary``
will receive a 400 INVALID_ARGUMENT error.

Using a plain ``async def`` instead keeps everything as function declarations
and avoids the mixing constraint entirely.  The retrieval still hits the same
Vertex AI RAG corpus — the only difference is that it goes through a function
call rather than a server-side grounding pass.
"""

from __future__ import annotations

import asyncio

import structlog

from app.context.rag.rag_engine_handler import rag_engine_handler

logger = structlog.get_logger(__name__)


async def retrieve_from_corpus(query: str) -> str:
    """Search the internal knowledge-base corpus and return the most relevant chunks.

    Query the Vertex AI RAG corpus for text chunks semantically similar to
    *query*.  Use this before fetching external web pages — if sufficient
    information already exists in the corpus an extra web request can be
    avoided.

    Args:
        query: Natural-language search query describing the information needed.

    Returns:
        Numbered list of the most relevant text chunks, or a message stating
        that no relevant content was found.
    """
    corpus_name = rag_engine_handler.corpus_name
    if not corpus_name:
        return "RAG corpus is not available – skipping corpus search."

    try:
        from vertexai.preview import rag

        response = await asyncio.to_thread(
            rag.retrieval_query,
            text=query,
            rag_corpora=[corpus_name],
            similarity_top_k=5,
            vector_distance_threshold=0.5,
        )

        contexts = response.contexts.contexts
        if not contexts:
            return f"No relevant content found in the corpus for query: '{query}'"

        chunks = [f"{i + 1}. {ctx.text.strip()}" for i, ctx in enumerate(contexts)]
        logger.info("RAG retrieval complete", query=query, chunks=len(chunks))
        return "\n\n".join(chunks)

    except Exception as e:
        logger.warning("RAG retrieval failed", query=query, error=str(e))
        return f"Corpus search failed: {e}"
