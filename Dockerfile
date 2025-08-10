FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY mini_chat_all_in_one.py .
COPY test_mini_chat.py .

# Create directory for model cache
RUN mkdir -p /root/.cache/huggingface

# Expose port
EXPOSE 8000

# Set environment variables
ENV TRANSFORMERS_CACHE=/root/.cache/huggingface
ENV HF_HOME=/root/.cache/huggingface

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/')" || exit 1

# Default command (web mode)
CMD ["python", "mini_chat_all_in_one.py", "--web", "--host", "0.0.0.0", "--port", "8000"]

# Alternative: CLI mode
# CMD ["python", "mini_chat_all_in_one.py", "--cli"]