#!/bin/bash

# Start script for Railway deployment
echo "Starting AI Data Chatbot Application..."

# Set environment variables
export NODE_ENV=production
export PYTHONUNBUFFERED=1

# Use Railway's PORT or default to 8000
PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Start the backend server
echo "Starting backend server..."
cd /app/backend
python -m uvicorn main_sqlite:app --host 0.0.0.0 --port $PORT &
BACKEND_PID=$!

# Give backend time to start
sleep 5

# Start the frontend server on port 3000
echo "Starting frontend server..."
cd /app/frontend
PORT=3000 npm start &
FRONTEND_PID=$!

# Keep the container running
echo "Application started. Backend on port $PORT, Frontend on port 3000"
wait $BACKEND_PID $FRONTEND_PID