# Stage 1: Build environment
FROM python:3.14-slim AS builder

# Install uv by copying it from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Optimizations for uv inside Docker
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./

COPY src/ ./src/

RUN uv sync --frozen --no-dev --no-editable

# Stage 2: Runtime enviornoment
FROM python:3.14-slim

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

# Run as the pipeline's actual entrypoint.
CMD ["ingest"]