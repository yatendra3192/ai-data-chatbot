"""
Download full database from external source
This script downloads the complete CRM database for Railway deployment
"""
import os
import urllib.request
import shutil
from pathlib import Path
import requests

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
        
        # For Google Drive, we need to handle large file warning
        if 'drive.google.com' in db_url:
            print("Detected Google Drive URL, using special download method...")
            
            # Extract file ID from URL
            if 'id=' in db_url:
                file_id = db_url.split('id=')[1].split('&')[0]
            else:
                file_id = db_url.split('/d/')[1].split('/')[0]
            
            # Try direct download with confirm parameter
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm=t"
            
            # Use requests for better handling
            temp_path = str(db_path) + ".download"
            
            print("Starting download...")
            response = requests.get(download_url, stream=True, timeout=300)  # 5 minute timeout
            
            # Check if we got HTML instead of the file
            content_type = response.headers.get('content-type', '')
            if 'text/html' in content_type:
                print("Google Drive requires confirmation for large files")
                # Try alternative method
                session = requests.Session()
                response = session.get(f"https://drive.google.com/uc?export=download&id={file_id}", stream=True)
                
                # Look for confirmation token in response
                for key, value in response.cookies.items():
                    if key.startswith('download_warning'):
                        params = {'id': file_id, 'confirm': value}
                        response = session.get("https://drive.google.com/uc?export=download", 
                                              params=params, stream=True)
                        break
            
            # Download the file
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=block_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            percent = (downloaded * 100.0 / total_size)
                            print(f"Download progress: {percent:.1f}%", end='\r')
            
            # Verify the download
            file_size = os.path.getsize(temp_path)
            print(f"\nDownloaded file size: {file_size / 1024 / 1024:.2f} MB")
            
            if file_size < 1024 * 1024:  # Less than 1MB, probably got HTML
                print("ERROR: Downloaded file too small, likely got HTML page instead")
                os.remove(temp_path)
                return False
            
            # Move to final location
            shutil.move(temp_path, db_path)
            
        else:
            # For non-Google Drive URLs, use requests for better control
            print("Using direct download method...")
            temp_path = str(db_path) + ".download"
            
            try:
                response = requests.get(db_url, stream=True, timeout=300)  # 5 minute timeout
                response.raise_for_status()  # Raise error for bad status codes
                
                total_size = int(response.headers.get('content-length', 0))
                block_size = 8192
                downloaded = 0
                
                print(f"Downloading {total_size / 1024 / 1024:.2f} MB...")
                
                with open(temp_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=block_size):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                percent = (downloaded * 100.0 / total_size)
                                if downloaded % (block_size * 100) == 0:  # Print every 100 blocks
                                    print(f"Download progress: {percent:.1f}%")
                
                shutil.move(temp_path, db_path)
                
            except requests.exceptions.Timeout:
                print("ERROR: Download timed out after 5 minutes")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False
            except requests.exceptions.RequestException as e:
                print(f"ERROR: Download failed: {e}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                return False
        
        print(f"Database downloaded successfully!")
        file_size = os.path.getsize(db_path)
        print(f"Database size: {file_size / 1024 / 1024:.2f} MB")
        
        # Verify it's a valid SQLite database
        import sqlite3
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("SELECT 1")
            conn.close()
            print("✓ Database validation successful")
            return True
        except Exception as e:
            print(f"ERROR: Downloaded file is not a valid SQLite database: {e}")
            os.remove(db_path)
            return False
        
    except Exception as e:
        print(f"Error downloading database: {e}")
        if os.path.exists(str(db_path) + ".download"):
            os.remove(str(db_path) + ".download")
        return False

if __name__ == "__main__":
    download_full_database()