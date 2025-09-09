#!/bin/bash

# Start script for Railway deployment
echo "Starting AI Data Chatbot Application..."

# Set environment variables
export NODE_ENV=production
export PYTHONUNBUFFERED=1

# Check if database exists, if not create it
if [ ! -f "./backend/database/crm_analytics.db" ]; then
    echo "Database not found. Initializing..."
    cd backend/database
    python import_csv_to_sqlite.py
    cd ../..
fi

# Start the backend server
echo "Starting backend server on port ${PORT:-8000}..."
cd backend
python -m uvicorn main_sqlite:app --host 0.0.0.0 --port ${PORT:-8000} &
BACKEND_PID=$!

# Start the frontend server
echo "Starting frontend server..."
cd ../frontend
npm start &
FRONTEND_PID=$!

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID