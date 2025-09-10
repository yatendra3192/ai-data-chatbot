# Multi-stage build for unified frontend + backend deployment
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build the frontend (static export)
RUN npm run build

# Final stage - Python backend with frontend
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

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/out ./frontend/out
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next

# Create database directory
RUN mkdir -p /app/backend/database

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Expose port (Railway will set PORT env var)
EXPOSE 8000

# Initialize database on first run (if needed) and start the application
CMD ["sh", "-c", "cd backend && python init_sample_database.py && cd .. && python -m uvicorn backend.main_unified:app --host 0.0.0.0 --port ${PORT:-8000}"]