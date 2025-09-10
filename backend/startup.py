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
    
    # Check if we're using a volume (persistent storage)
    volume_mounted = os.path.exists("/app/backend/database")
    if volume_mounted:
        print("✓ Volume detected - Database will persist between deployments")
    
    if not db_path.exists():
        print("No database found. Attempting to download full database...")
        
        # Try to download full database first
        try:
            if not download_full_database():
                # If download fails, create sample database
                print("Download failed. Creating sample database as fallback...")
                create_sample_database()
        except Exception as e:
            print(f"ERROR during download: {e}")
            print("Creating sample database as fallback...")
            create_sample_database()
    else:
        file_size = os.path.getsize(db_path)
        print(f"✓ Database exists: {file_size / 1024 / 1024:.2f} MB")
        
        # Only re-download if it's a sample database and we have a URL
        if file_size < 10 * 1024 * 1024 and os.environ.get('DATABASE_URL'):
            print("Small database detected. Attempting to download full database...")
            if download_full_database():
                print("✓ Full database downloaded successfully!")
                print("✓ Database is now persistent in Railway volume")
            else:
                print("Continuing with existing database")
        elif file_size > 100 * 1024 * 1024:
            print("✓ Full database loaded from persistent volume!")
            print(f"✓ Contains all 1.4M+ records ({file_size / 1024 / 1024:.2f} MB)")
    
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