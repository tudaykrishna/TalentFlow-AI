# ================================
# TalentFlow AI - Frontend Service
# Streamlit Application
# ================================

# Use Python 3.10 slim image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from root
COPY requirements.txt .

# Install Python dependencies (only frontend-related packages)
RUN pip install --no-cache-dir \
    streamlit==1.42.0 \
    requests==2.32.3 \
    pandas==2.2.3 \
    audio-recorder-streamlit==0.0.10 \
    Authlib==1.3.2

# Copy App application code
COPY App/ /app/App/

# Set working directory to App
WORKDIR /app/App

# Create necessary directories
RUN mkdir -p images

# Health check for Streamlit
HEALTHCHECK --interval=30s --timeout=30s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose Streamlit port
EXPOSE 8501

# Configure Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Start Streamlit application
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]