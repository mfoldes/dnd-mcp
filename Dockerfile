# syntax=docker/dockerfile:1

# 1: Build Dependencies Stage
# ============================
ARG PYTHON_VERSION=3.13
FROM python:${PYTHON_VERSION} AS builder

# Do not write .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Do not buffer stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependencies file
COPY pyproject.toml requirements.txt ./

# Create a virtual environment and install dependencies
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install -r requirements.txt

# 2: Runtime Image Stage
# ============================
FROM python:${PYTHON_VERSION}-slim AS runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/venv/bin:$PATH"

WORKDIR /app

# Create non-privileged user to run service
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid ${UID} \
    dnduser

# Copy virtual environment from builder stage
COPY --from=builder /app/venv /app/venv

# Copy application code
COPY --chown=dnduser:dnduser . .

# Create logs and cache directory
RUN mkdir -p /app/logs /app/cache && \
    chown -R dnduser:dnduser /app/logs /app/cache

# Change to non-privileged user
USER dnduser

# Expose MCP server port
EXPOSE 8000

# Set entrypoint
ENTRYPOINT ["python", "dnd_mcp_server.py"]