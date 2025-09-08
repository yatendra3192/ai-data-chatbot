"""
Import CSV files to SQL Server Database
This script creates tables and imports data with proper indexing
"""
import pandas as pd
import pyodbc
from sqlalchemy import create_engine, text
import os
import time
from sql_config import db_config

class CSVToSQLImporter:
    def __init__(self):
        self.config = db_config
        self.chunk_size = 10000  # Import in chunks for large files
        
    def create_tables(self):
        """Create tables with proper data types and indexes"""
        conn = self.config.get_connection()
        cursor = conn.cursor()
        
        try:
            # Drop existing tables if they exist
            tables = ['salesorder', 'quote', 'quotedetail']
            for table in tables:
                cursor.execute(f"DROP TABLE IF EXISTS {table}")
            
            # Create salesorder table
            print("Creating salesorder table...")
            cursor.execute("""
                CREATE TABLE salesorder (
                    Id NVARCHAR(50) PRIMARY KEY,
                    customeridname NVARCHAR(500),
                    totalamount DECIMAL(18,2),
                    statuscode INT,
                    modifiedon DATETIME,
                    billto_city NVARCHAR(100),
                    billto_country NVARCHAR(100),
                    ordernumber NVARCHAR(50)
                )
            """)
            
            # Create quote table
            print("Creating quote table...")
            cursor.execute("""
                CREATE TABLE quote (
                    Id NVARCHAR(50) PRIMARY KEY,
                    name NVARCHAR(500),
                    totalamount DECIMAL(18,2),
                    statuscode INT,
                    customeridname NVARCHAR(500),
                    modifiedon DATETIME,
                    quotenumber NVARCHAR(50)
                )
            """)
            
            # Create quotedetail table
            print("Creating quotedetail table...")
            cursor.execute("""
                CREATE TABLE quotedetail (
                    Id NVARCHAR(50) PRIMARY KEY,
                    quoteid NVARCHAR(50),
                    productidname NVARCHAR(500),
                    quantity DECIMAL(18,2),
                    priceperunit DECIMAL(18,2),
                    extendedamount DECIMAL(18,2),
                    producttypecode INT
                )
            """)
            
            conn.commit()
            print("Tables created successfully!")
            
            # Create indexes for better performance
            print("Creating indexes...")
            
            # Indexes for salesorder
            cursor.execute("CREATE INDEX IX_salesorder_customer ON salesorder(customeridname)")
            cursor.execute("CREATE INDEX IX_salesorder_amount ON salesorder(totalamount)")
            cursor.execute("CREATE INDEX IX_salesorder_date ON salesorder(modifiedon)")
            
            # Indexes for quote
            cursor.execute("CREATE INDEX IX_quote_customer ON quote(customeridname)")
            cursor.execute("CREATE INDEX IX_quote_amount ON quote(totalamount)")
            cursor.execute("CREATE INDEX IX_quote_date ON quote(modifiedon)")
            
            # Indexes for quotedetail
            cursor.execute("CREATE INDEX IX_quotedetail_quote ON quotedetail(quoteid)")
            cursor.execute("CREATE INDEX IX_quotedetail_product ON quotedetail(productidname)")
            
            conn.commit()
            print("Indexes created successfully!")
            
        except Exception as e:
            print(f"Error creating tables: {e}")
            conn.rollback()
        finally:
            conn.close()
    
    def import_csv_to_table(self, csv_path: str, table_name: str, columns_map: dict):
        """Import CSV file to SQL Server table"""
        print(f"\nImporting {csv_path} to {table_name} table...")
        
        try:
            # Create SQLAlchemy engine for bulk insert
            engine = self.config.create_engine()
            
            # Read CSV in chunks
            total_rows = 0
            start_time = time.time()
            
            for chunk in pd.read_csv(csv_path, chunksize=self.chunk_size):
                # Select and rename columns based on mapping
                chunk_filtered = chunk[list(columns_map.keys())].copy()
                chunk_filtered.columns = list(columns_map.values())
                
                # Clean data
                chunk_filtered = chunk_filtered.where(pd.notnull(chunk_filtered), None)
                
                # Insert to SQL Server
                chunk_filtered.to_sql(
                    table_name, 
                    engine, 
                    if_exists='append', 
                    index=False,
                    method='multi'
                )
                
                total_rows += len(chunk_filtered)
                print(f"  Imported {total_rows:,} rows...", end='\r')
            
            elapsed = time.time() - start_time
            print(f"\n✓ Imported {total_rows:,} rows to {table_name} in {elapsed:.2f} seconds")
            
            return total_rows
            
        except Exception as e:
            print(f"Error importing {csv_path}: {e}")
            return 0
    
    def import_all_csvs(self):
        """Import all CSV files to SQL Server"""
        print("Starting CSV import to SQL Server...")
        
        # Create database and tables
        if not self.config.create_database_if_not_exists():
            print("Failed to create database")
            return
        
        self.create_tables()
        
        # Define column mappings for each table
        # Map CSV columns to SQL table columns (selecting most important columns)
        
        salesorder_columns = {
            'Id': 'Id',
            'customeridname': 'customeridname',
            'totalamount': 'totalamount',
            'statuscode': 'statuscode',
            'modifiedon': 'modifiedon',
            'billto_city': 'billto_city',
            'billto_country': 'billto_country',
            'ordernumber': 'ordernumber'
        }
        
        quote_columns = {
            'Id': 'Id',
            'name': 'name',
            'totalamount': 'totalamount',
            'statuscode': 'statuscode',
            'customeridname': 'customeridname',
            'modifiedon': 'modifiedon',
            'quotenumber': 'quotenumber'
        }
        
        quotedetail_columns = {
            'Id': 'Id',
            'quoteid': 'quoteid',
            'productidname': 'productidname',
            'quantity': 'quantity',
            'priceperunit': 'priceperunit',
            'extendedamount': 'extendedamount',
            'producttypecode': 'producttypecode'
        }
        
        # Import each CSV
        datasets = [
            (r"C:\Users\User\Documents\DVwithCC\salesorder.csv", 'salesorder', salesorder_columns),
            (r"C:\Users\User\Documents\DVwithCC\Quote.csv", 'quote', quote_columns),
            (r"C:\Users\User\Documents\DVwithCC\quotedetail.csv", 'quotedetail', quotedetail_columns)
        ]
        
        total_imported = 0
        for csv_path, table_name, columns in datasets:
            if os.path.exists(csv_path):
                rows = self.import_csv_to_table(csv_path, table_name, columns)
                total_imported += rows
            else:
                print(f"CSV file not found: {csv_path}")
        
        print(f"\n✅ Import complete! Total rows imported: {total_imported:,}")
        
        # Verify data
        self.verify_import()
    
    def verify_import(self):
        """Verify the imported data"""
        print("\nVerifying imported data...")
        
        conn = self.config.get_connection()
        cursor = conn.cursor()
        
        tables = ['salesorder', 'quote', 'quotedetail']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} rows")
        
        conn.close()

if __name__ == "__main__":
    importer = CSVToSQLImporter()
    
    # Test connection first
    if db_config.test_connection():
        importer.import_all_csvs()
    else:
        print("Failed to connect to SQL Server. Please check your connection settings in sql_config.py")