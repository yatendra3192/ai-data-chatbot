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

# Create a different working directory to avoid conflicts
WORKDIR /railway

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code to /railway/backend
COPY backend/*.py ./backend/
COPY backend/database/*.py ./backend/database/

# Copy frontend build from builder stage
COPY --from=frontend-builder /app/frontend/out ./frontend/out
COPY --from=frontend-builder /app/frontend/public ./frontend/public
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next

# Create database directory structure
RUN mkdir -p /railway/backend/database

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production
ENV PYTHONPATH=/railway

# Expose port
EXPOSE 8000

# Run from /railway/backend directory
WORKDIR /railway/backend

# Start the application
CMD ["python", "startup.py"]