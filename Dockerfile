FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

ARG AZURE_API_ENDPOINT
ARG AZURE_API_KEY
ARG OPENAI_API_VERSION
ARG LANGSMITH_API_KEY

ENV AZURE_API_ENDPOINT=${AZURE_API_ENDPOINT} \
    AZURE_API_KEY=${AZURE_API_KEY} \
    OPENAI_API_VERSION=${OPENAI_API_VERSION} \
    LANGSMITH_API_KEY=${LANGSMITH_API_KEY}

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./ 
COPY uv.lock* ./
COPY src ./src
COPY README.md ./README.md

RUN pip install --no-cache-dir uv
RUN uv sync --frozen --no-dev || uv sync --no-dev


EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
