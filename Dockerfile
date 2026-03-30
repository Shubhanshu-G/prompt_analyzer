FROM python:3.11-slim

LABEL maintainer="AI Prompt Evaluator Team"
LABEL description="A local, privacy-focused tool for analyzing and scoring AI prompts and decisions points using Ollama."
LABEL version="1.0"
LABEL project="AI Prompt & Decision Evaluator"

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create uploads directory
RUN mkdir -p uploads

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the Evaluator app
CMD ["streamlit", "run", "evaluate.py", "--server.address=0.0.0.0", "--server.port=8501"]
