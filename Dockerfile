FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY rag_scripts/ ./rag_scripts/
COPY data/ ./data/

# Set working directory to rag_scripts
WORKDIR /app/rag_scripts

# Expose port
EXPOSE 5000

# Default command (can be overridden)
CMD ["python", "app.py", "--provider", "bedrock"]