# ── Build stage ───────────────────────────────────────────────────────────────
# Uses the official uv image which ships Python 3.14 + uv pre-installed.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Install dependencies before copying source code to maximise Docker layer cache.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

# Copy application source and perform the final install (adds the project itself).
COPY . .
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev


# ── Runtime stage ─────────────────────────────────────────────────────────────
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Non-root user for security.
RUN useradd --create-home --uid 1000 appuser

COPY --from=builder --chown=appuser:appuser /app /app

USER appuser

EXPOSE 8080

# Cloud Run injects PORT=8080. Run without --reload (production mode).
CMD ["sh", "-c", "uvicorn agentic_ai_main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1"]
