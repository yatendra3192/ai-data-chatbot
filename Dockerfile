# Simple Dockerfile for Railway - Backend API only
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Create database directory
RUN mkdir -p /app/backend/database

# Set working directory
WORKDIR /app/backend

# Create a simple startup script inline
RUN echo '#!/bin/bash\n\
echo "Starting Backend API Server..."\n\
python -m uvicorn main_sqlite:app --host 0.0.0.0 --port ${PORT:-8000}' > /app/start.sh && \
    chmod +x /app/start.sh

# Expose port
EXPOSE 8000

# Run the application
CMD ["/app/start.sh"]