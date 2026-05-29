"""Artifact tools for ADK agents – save, load, and list GCS-backed artifacts.

ADK injects ``tool_context`` automatically when a tool function declares it
as a parameter typed as ``ToolContext``.  The artifact service wired into the
runner persists files in Google Cloud Storage; each file is versioned, and
load/list operations always return the most-recent version unless specified.

All artifacts are stored with the ``user:`` namespace prefix, which means they
are scoped to the user rather than the session.  A file saved in one session is
visible and loadable in every subsequent session for the same user.

GCS path layout:
  user-scoped  →  {app_name}/{user_id}/user/{filename}/{version}
  (session-scoped would be {app_name}/{user_id}/{session_id}/{filename}/{version})

Supported formats
-----------------
Markdown (.md, .txt)  – stored as UTF-8 text via ``types.Part.from_text``
PDF (.pdf)            – stored as binary via ``types.Part.from_bytes`` with
                        the content supplied as a base64-encoded string.
"""

import base64

import structlog
from google.adk.tools import ToolContext
from google.genai import types

logger = structlog.get_logger(__name__)

_USER_PREFIX = "user:"


def _user_scoped(filename: str) -> str:
    """Return filename with the user: namespace prefix (idempotent)."""
    return filename if filename.startswith(_USER_PREFIX) else f"{_USER_PREFIX}{filename}"


async def save_artifact(filename: str, content: str, tool_context: ToolContext) -> str:
    """Save text content as a user-scoped artifact in Google Cloud Storage.

    The artifact is stored under the ``user:`` namespace so it persists across
    session resets and is visible in the Artifacts panel in every session.

    Args:
        filename: File name including extension, e.g. ``"report.md"`` or
                  ``"summary.txt"``.  Use ``.md`` for Markdown.
        content:  Full text content to store.

    Returns:
        Confirmation message with the assigned version number.
    """
    scoped = _user_scoped(filename)
    part = types.Part.from_text(text=content)
    version = await tool_context.save_artifact(filename=scoped, artifact=part)
    logger.info("Artifact saved", filename=scoped, version=version)
    return f"Artifact '{filename}' saved (version {version})."


async def save_pdf_artifact(
    filename: str, content_base64: str, tool_context: ToolContext
) -> str:
    """Save a PDF document as a user-scoped artifact in Google Cloud Storage.

    The content must be supplied as a base64-encoded string of the raw PDF
    bytes.  The artifact persists across session resets.

    Args:
        filename:       File name, e.g. ``"report.pdf"``.
        content_base64: Base64-encoded PDF bytes.

    Returns:
        Confirmation message with the assigned version number.
    """
    scoped = _user_scoped(filename)
    data = base64.b64decode(content_base64)
    part = types.Part.from_bytes(data=data, mime_type="application/pdf")
    version = await tool_context.save_artifact(filename=scoped, artifact=part)
    logger.info("PDF artifact saved", filename=scoped, version=version)
    return f"PDF artifact '{filename}' saved (version {version})."


async def load_artifact(filename: str, tool_context: ToolContext) -> str:
    """Load a previously saved artifact and return its text content.

    Looks up the artifact under the ``user:`` namespace first (user-scoped),
    then falls back to a plain session-scoped lookup for backwards compatibility.
    For binary artifacts (e.g. PDFs) a short description is returned instead
    of the raw bytes.

    Args:
        filename: Base file name (with or without the ``user:`` prefix).

    Returns:
        Text content of the artifact, or a descriptive message for binary files.
    """
    scoped = _user_scoped(filename)
    part = await tool_context.load_artifact(filename=scoped)
    if part is None:
        part = await tool_context.load_artifact(filename=filename)
    if part is None:
        return f"Artifact '{filename}' not found."
    if part.text:
        return part.text
    if part.inline_data:
        mime = part.inline_data.mime_type or "application/octet-stream"
        size_kb = len(part.inline_data.data) / 1024
        return (
            f"[Binary artifact: '{filename}', type: {mime}, "
            f"size: {size_kb:.1f} KB – download from the Artifacts panel]"
        )
    return f"Artifact '{filename}' has no readable content."


async def list_artifacts(tool_context: ToolContext) -> str:
    """List all user-scoped artifact filenames (visible across all sessions).

    Returns:
        Bullet list of filenames, or a message if none have been saved yet.
    """
    names = await tool_context.list_artifacts()
    logger.info("Artifacts listed", count=len(names))
    if not names:
        return "No artifacts saved yet."
    display = [n[len(_USER_PREFIX):] if n.startswith(_USER_PREFIX) else n for n in names]
    return "Saved artifacts:\n" + "\n".join(f"- {n}" for n in display)
