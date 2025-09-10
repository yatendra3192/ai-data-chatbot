#!/usr/bin/env python
"""
Startup script for Railway deployment
Initializes database and starts the server
"""
import os
import sys
import uvicorn
from init_sample_database import create_sample_database

if __name__ == "__main__":
    # Initialize database if needed
    print("Checking database...")
    create_sample_database()
    
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Starting server on port {port}...")
    
    # Start the server
    uvicorn.run(
        "main_unified:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )