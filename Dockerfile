FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    libpq-dev \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml uv.lock* ./

# Install Python dependencies (non-editable, just dependencies)
# Install base dependencies first
RUN uv pip install --system \
    a2a-sdk>=0.3.0 \
    "google-adk[extensions]>=1.7.0" \
    sqlalchemy>=2.0.0 \
    alembic>=1.13.0 \
    psycopg2-binary>=2.9.9 \
    uvicorn>=0.27.0 \
    gunicorn>=21.0.0 \
    fastapi>=0.109.0 \
    mesop>=0.1.0 \
    httpx>=0.27.0 \
    python-dotenv>=1.0.0 \
    click>=8.2.0 \
    mem0ai>=0.1.0
    langfuse>=3.0.0

# Install RAG dependencies
RUN uv pip install --system \
    langchain>=0.3.0 \
    langchain-google-genai>=2.1.5 \
    langgraph>=0.4.5 \
    chromadb>=0.5.0 \
    sentence-transformers>=3.0.0 \
    pydantic-settings>=2.0.0 \
    pypdf2>=3.0.0 \
    python-docx>=1.1.0 \
    python-pptx>=1.0.0 \
    pillow>=10.0.0 \
    pytesseract>=0.3.10 \
    openai

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/test_documents data/vector_db

# Set Python path
ENV PYTHONPATH=/app

# Expose ports
EXPOSE 8083 10001 10002 10003 10004 10005 10006 10007 10008 12000

# Default command (can be overridden in docker-compose)
CMD ["python", "scripts/init_db.py", "--seed"]
