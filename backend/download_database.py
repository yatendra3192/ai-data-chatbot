"""
Download full database from external source
This script downloads the complete CRM database for Railway deployment
"""
import os
import urllib.request
import shutil
from pathlib import Path

def download_full_database():
    """Download the full database from a URL"""
    db_path = Path(__file__).parent / "database" / "crm_analytics.db"
    
    # Check if full database already exists
    if db_path.exists():
        file_size = os.path.getsize(db_path)
        if file_size > 100 * 1024 * 1024:  # If > 100MB, assume it's the full database
            print(f"Full database already exists ({file_size / 1024 / 1024:.2f} MB)")
            return True
    
    # Get database URL from environment variable
    db_url = os.environ.get('DATABASE_URL')
    
    if not db_url:
        print("DATABASE_URL environment variable not set")
        print("Using sample database instead")
        return False
    
    print(f"Downloading full database from: {db_url}")
    
    try:
        # Create database directory if it doesn't exist
        os.makedirs(db_path.parent, exist_ok=True)
        
        # Download with progress
        def download_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            percent = min(downloaded * 100.0 / total_size, 100)
            print(f"Download progress: {percent:.1f}%", end='\r')
        
        # Download the file
        temp_path = str(db_path) + ".download"
        urllib.request.urlretrieve(db_url, temp_path, download_progress)
        
        # Move to final location
        shutil.move(temp_path, db_path)
        
        print(f"\nDatabase downloaded successfully!")
        file_size = os.path.getsize(db_path)
        print(f"Database size: {file_size / 1024 / 1024:.2f} MB")
        return True
        
    except Exception as e:
        print(f"Error downloading database: {e}")
        return False

if __name__ == "__main__":
    download_full_database()