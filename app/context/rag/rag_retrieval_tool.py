"""RAG retrieval tool – builds a VertexAiRagRetrieval from the configured corpus.

``VertexAiRagRetrieval`` integrates with Gemini 2+ as a native server-side
retrieval tool (injected via ``types.Tool(retrieval=...)``) so no extra
function-call round-trip is needed.  For older models it falls back to a
regular function declaration.

Call ``get_rag_retrieval_tool()`` once per agent definition.  It triggers
lazy corpus initialisation and returns ``None`` when RAG is unavailable so
callers can simply filter it out of the tools list.
"""

from __future__ import annotations

import structlog
from google.adk.tools.retrieval import VertexAiRagRetrieval

from app.context.rag.rag_engine_handler import rag_engine_handler

logger = structlog.get_logger(__name__)


def get_rag_retrieval_tool() -> VertexAiRagRetrieval | None:
    """Return a configured VertexAiRagRetrieval tool, or None if RAG is unavailable."""
    corpus_name = rag_engine_handler.corpus_name
    if not corpus_name:
        logger.warning("RAG corpus unavailable – skipping RAG retrieval tool")
        return None
    logger.info("RAG retrieval tool created", corpus=corpus_name)
    return VertexAiRagRetrieval(
        name="retrieve_from_corpus",
        description=(
            "Search the internal knowledge-base corpus for documents relevant "
            "to the query.  Use this first before fetching external web pages – "
            "if the answer already exists in the corpus you can avoid an extra "
            "web request.  Returns the most relevant text chunks."
        ),
        rag_corpora=[corpus_name],
        similarity_top_k=5,
        vector_distance_threshold=0.5,
    )
