"""Unit tests for artifact tool helpers (no GCS calls)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from google.genai import types

from app.context.artifacts.artifact_tools import _user_scoped, list_artifacts, load_artifact


def test_user_scoped_adds_prefix():
    assert _user_scoped("report.md") == "user:report.md"


def test_user_scoped_does_not_double_prefix():
    assert _user_scoped("user:report.md") == "user:report.md"


@pytest.mark.asyncio
async def test_list_artifacts_strips_prefix():
    ctx = AsyncMock()
    ctx.list_artifacts = AsyncMock(return_value=["user:summary.md", "user:report.md"])

    result = await list_artifacts(tool_context=ctx)

    assert "summary.md" in result
    assert "report.md" in result
    assert "user:" not in result


@pytest.mark.asyncio
async def test_list_artifacts_empty():
    ctx = AsyncMock()
    ctx.list_artifacts = AsyncMock(return_value=[])

    result = await list_artifacts(tool_context=ctx)
    assert "No artifacts" in result or result.strip() == "Saved artifacts:"


@pytest.mark.asyncio
async def test_load_artifact_not_found():
    ctx = AsyncMock()
    ctx.load_artifact = AsyncMock(return_value=None)

    result = await load_artifact(filename="missing.md", tool_context=ctx)
    assert "not found" in result.lower()


@pytest.mark.asyncio
async def test_load_artifact_returns_content():
    ctx = AsyncMock()
    part = types.Part(text="# My Summary")
    ctx.load_artifact = AsyncMock(return_value=part)

    result = await load_artifact(filename="summary.md", tool_context=ctx)
    assert "# My Summary" in result
