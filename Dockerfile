# Minimal Dockerfile for Railway - Backend only
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy data files for database initialization (if they exist)
# These will be ignored if not present
COPY Data\ Dictionary\ Orders.txt* ./
COPY DD_Quote.txt* ./
COPY DD_quotedetail.txt* ./

# Set working directory to backend
WORKDIR /app/backend

# Initialize database on container start
RUN python init_database.py

# Expose port
EXPOSE 8000

# Run the application (Railway sets the PORT env variable)
CMD uvicorn main_sqlite:app --host 0.0.0.0 --port ${PORT:-8000}