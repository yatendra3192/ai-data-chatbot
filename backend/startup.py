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

def main():
    print("=" * 60)
    print("Starting AI Data Chatbot")
    print("=" * 60)
    
    # Handle volume mount - Railway mounts at /app/backend/database
    volume_path = Path("/app/backend/database")
    local_db_path = Path("/railway/backend/database")
    
    # If volume exists and local doesn't, create symlink
    if volume_path.exists() and not local_db_path.exists():
        print(f"Creating symlink from {local_db_path} to {volume_path}")
        os.makedirs(local_db_path.parent, exist_ok=True)
        if local_db_path.exists():
            os.rmdir(local_db_path)
        os.symlink(volume_path, local_db_path)
        print("✓ Volume linked successfully")
    
    # Check if database exists
    db_path = Path("database/crm_analytics.db")
    download_marker = Path("database/.full_db_downloaded")
    
    # Check if we're using a volume (persistent storage)
    volume_mounted = volume_path.exists()
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
        
        # Check if we have a marker indicating full database was downloaded
        if download_marker.exists():
            print("✓ Full database marker found - skipping re-download")
            print(f"✓ Using existing database ({file_size / 1024 / 1024:.2f} MB)")
        # Check if this is the full database (>400MB)
        elif file_size > 400 * 1024 * 1024:  # 400MB threshold for full database
            print("✓ Full database already loaded from persistent volume!")
            print(f"✓ Contains all 1.4M+ records ({file_size / 1024 / 1024:.2f} MB)")
            print("✓ Skipping re-download - database is complete")
            # Create marker file to prevent future re-downloads
            download_marker.touch()
        # Only re-download if it's a small/sample database and we have a URL
        elif file_size < 10 * 1024 * 1024 and os.environ.get('DATABASE_URL'):
            print("Small database detected. Attempting to download full database...")
            if download_full_database():
                print("✓ Full database downloaded successfully!")
                print("✓ Database is now persistent in Railway volume")
                # Create marker file to prevent future re-downloads
                download_marker.touch()
            else:
                print("Continuing with existing database")
        else:
            print(f"✓ Using existing database ({file_size / 1024 / 1024:.2f} MB)")
            print("✓ Database will persist in Railway volume")
    
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

if __name__ == "__main__":
    main()