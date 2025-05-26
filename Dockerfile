# Use Python 3.12 slim image (2025 modernization)
FROM python:3.12-slim as builder

# Install UV for faster dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_CACHE_DIR=/tmp/uv-cache

# Copy dependency files
WORKDIR /app
COPY pyproject.toml uv.lock* ./

# Install dependencies with UV
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.12-slim

# Copy virtual environment from builder
COPY --from=builder /app/.venv /app/.venv

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PATH="/app/.venv/bin:$PATH"

# Create non-root user for security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Copy application code
WORKDIR /app
COPY . .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app
USER appuser

# Create required directories
RUN mkdir -p input output

# Default command
CMD ["python", "china_data_processor.py"]
