# ── Build stage ───────────────────────────────────────────────────────────────
# Uses the official uv image which ships Python 3.14 + uv pre-installed.
FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim AS builder

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

# Copy dependency specs first so Docker caches the install layer separately
# from the application source — rebuilds only re-run uv sync when lock files change.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# Copy application source and finalize install (adds the project package itself).
COPY agentic_ai_main.py ./
COPY app/ ./app/
RUN uv sync --frozen --no-dev


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
