FROM python:3.11.12-slim

# Install tools
RUN apt-get update -y && apt-get install -y libpq-dev gcc && \
    python -m pip install --upgrade pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Copy source code (restricted by .dockerignore )
COPY . .

# Install Python dependencies
RUN uv sync --frozen --no-cache

ENV PATH="/app/.venv/bin:$PATH"

ENV PYTHONPATH=/app/src

EXPOSE 8080

# Use uvicorn to launch FastAPI app from src/main.py
# ENTRYPOINT ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080"]
ENTRYPOINT ["uvicorn"]
CMD ["src.main:app", "--host", "0.0.0.0", "--port", "8080"]
