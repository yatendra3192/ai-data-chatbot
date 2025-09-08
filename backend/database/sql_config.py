"""
SQL Server Database Configuration
"""
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import pyodbc
from typing import Optional

class SQLServerConfig:
    def __init__(self):
        # SQL Server connection parameters
        # Update these with your SQL Server details
        self.server = os.getenv('SQL_SERVER', 'localhost')
        self.database = os.getenv('SQL_DATABASE', 'CRM_Analytics')
        self.username = os.getenv('SQL_USERNAME', 'sa')
        self.password = os.getenv('SQL_PASSWORD', 'YourPassword123!')
        self.driver = '{ODBC Driver 17 for SQL Server}'
        
        # Connection string for pyodbc
        self.connection_string = (
            f'DRIVER={self.driver};'
            f'SERVER={self.server};'
            f'DATABASE={self.database};'
            f'UID={self.username};'
            f'PWD={self.password};'
            f'TrustServerCertificate=yes;'
        )
        
        # SQLAlchemy connection URL
        self.sqlalchemy_url = (
            f'mssql+pyodbc://{self.username}:{self.password}@{self.server}/{self.database}'
            f'?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes'
        )
        
        self.engine = None
        self.session = None
    
    def create_engine(self):
        """Create SQLAlchemy engine"""
        try:
            self.engine = create_engine(
                self.sqlalchemy_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False  # Set to True for debugging
            )
            return self.engine
        except Exception as e:
            print(f"Error creating engine: {e}")
            return None
    
    def get_connection(self):
        """Get direct pyodbc connection"""
        try:
            return pyodbc.connect(self.connection_string)
        except Exception as e:
            print(f"Error connecting to SQL Server: {e}")
            return None
    
    def test_connection(self):
        """Test the database connection"""
        try:
            conn = self.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT @@VERSION")
                version = cursor.fetchone()[0]
                print(f"Connected to SQL Server: {version[:50]}...")
                conn.close()
                return True
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False
    
    def create_database_if_not_exists(self):
        """Create the database if it doesn't exist"""
        try:
            # Connect to master database first
            master_conn_string = self.connection_string.replace(
                f'DATABASE={self.database}',
                'DATABASE=master'
            )
            conn = pyodbc.connect(master_conn_string)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute(f"""
                SELECT name FROM sys.databases WHERE name = '{self.database}'
            """)
            
            if not cursor.fetchone():
                # Create database
                cursor.execute(f"CREATE DATABASE [{self.database}]")
                print(f"Database '{self.database}' created successfully")
            else:
                print(f"Database '{self.database}' already exists")
            
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating database: {e}")
            return False

# Global instance
db_config = SQLServerConfig()