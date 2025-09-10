#!/usr/bin/env python
"""
Startup script for Railway deployment
Initializes database and starts the server
"""
import os
import sys
import uvicorn
from pathlib import Path
from init_sample_database import create_sample_database
from download_database import download_full_database

if __name__ == "__main__":
    print("=" * 60)
    print("Starting AI Data Chatbot")
    print("=" * 60)
    
    # Check if database exists
    db_path = Path(__file__).parent / "database" / "crm_analytics.db"
    
    if not db_path.exists():
        print("No database found. Attempting to download full database...")
        
        # Try to download full database first
        if not download_full_database():
            # If download fails, create sample database
            print("Creating sample database as fallback...")
            create_sample_database()
    else:
        file_size = os.path.getsize(db_path)
        print(f"Database exists: {file_size / 1024 / 1024:.2f} MB")
        
        if file_size < 10 * 1024 * 1024:  # If less than 10MB
            print("Small database detected. Attempting to download full database...")
            if download_full_database():
                print("Full database downloaded successfully!")
            else:
                print("Continuing with existing database")
    
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