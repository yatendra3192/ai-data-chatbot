"""
Import CSV files to SQLite Database
Provides similar performance benefits without SQL Server installation
"""
import pandas as pd
import sqlite3
import os
import time
from pathlib import Path

class CSVToSQLiteImporter:
    def __init__(self):
        self.db_path = "crm_analytics.db"
        self.chunk_size = 5000  # Smaller chunks to avoid SQLite limit
        self.conn = None
        
    def create_connection(self):
        """Create SQLite connection with optimizations"""
        self.conn = sqlite3.connect(self.db_path)
        # Enable performance optimizations
        self.conn.execute("PRAGMA journal_mode = WAL")
        self.conn.execute("PRAGMA synchronous = NORMAL")
        self.conn.execute("PRAGMA cache_size = 10000")
        self.conn.execute("PRAGMA temp_store = MEMORY")
        return self.conn
    
    def create_tables(self):
        """Create optimized tables"""
        print("Creating database tables...")
        
        cursor = self.conn.cursor()
        
        # Drop existing tables
        cursor.execute("DROP TABLE IF EXISTS salesorder")
        cursor.execute("DROP TABLE IF EXISTS quote")
        cursor.execute("DROP TABLE IF EXISTS quotedetail")
        
        # Create salesorder table with tax columns
        cursor.execute("""
            CREATE TABLE salesorder (
                Id TEXT PRIMARY KEY,
                customeridname TEXT,
                totalamount REAL,
                totaltax REAL,
                statuscode INTEGER,
                modifiedon TEXT,
                createdon TEXT,
                billto_city TEXT,
                billto_country TEXT,
                ordernumber TEXT
            )
        """)
        
        # Create quote table
        cursor.execute("""
            CREATE TABLE quote (
                Id TEXT PRIMARY KEY,
                name TEXT,
                totalamount REAL,
                statuscode INTEGER,
                customeridname TEXT,
                modifiedon TEXT,
                quotenumber TEXT
            )
        """)
        
        # Create quotedetail table
        cursor.execute("""
            CREATE TABLE quotedetail (
                Id TEXT PRIMARY KEY,
                quoteid TEXT,
                productidname TEXT,
                quantity REAL,
                priceperunit REAL,
                extendedamount REAL,
                producttypecode INTEGER
            )
        """)
        
        self.conn.commit()
        print("Tables created successfully!")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        print("Creating indexes...")
        cursor = self.conn.cursor()
        
        # Indexes for salesorder
        cursor.execute("CREATE INDEX idx_so_customer ON salesorder(customeridname)")
        cursor.execute("CREATE INDEX idx_so_amount ON salesorder(totalamount)")
        cursor.execute("CREATE INDEX idx_so_date ON salesorder(modifiedon)")
        cursor.execute("CREATE INDEX idx_so_status ON salesorder(statuscode)")
        
        # Indexes for quote
        cursor.execute("CREATE INDEX idx_q_customer ON quote(customeridname)")
        cursor.execute("CREATE INDEX idx_q_amount ON quote(totalamount)")
        cursor.execute("CREATE INDEX idx_q_date ON quote(modifiedon)")
        cursor.execute("CREATE INDEX idx_q_status ON quote(statuscode)")
        
        # Indexes for quotedetail
        cursor.execute("CREATE INDEX idx_qd_quote ON quotedetail(quoteid)")
        cursor.execute("CREATE INDEX idx_qd_product ON quotedetail(productidname)")
        cursor.execute("CREATE INDEX idx_qd_amount ON quotedetail(extendedamount)")
        
        self.conn.commit()
        print("Indexes created successfully!")
    
    def import_csv_to_table(self, csv_path: str, table_name: str, columns_map: dict):
        """Import CSV file to SQLite table"""
        if not os.path.exists(csv_path):
            print(f"[WARNING] CSV file not found: {csv_path}")
            return 0
            
        print(f"\nImporting {csv_path} to {table_name}...")
        
        try:
            total_rows = 0
            start_time = time.time()
            
            # Read CSV in chunks
            for chunk_num, chunk in enumerate(pd.read_csv(csv_path, chunksize=self.chunk_size, low_memory=False)):
                # Check if required columns exist
                available_cols = [col for col in columns_map.keys() if col in chunk.columns]
                if not available_cols:
                    print(f"  [WARNING] No matching columns found in {csv_path}")
                    continue
                    
                # Select available columns
                chunk_filtered = chunk[available_cols].copy()
                
                # Rename columns to match table schema
                rename_map = {old: columns_map[old] for old in available_cols}
                chunk_filtered = chunk_filtered.rename(columns=rename_map)
                
                # Clean data
                chunk_filtered = chunk_filtered.where(pd.notnull(chunk_filtered), None)
                
                # Insert to SQLite (use simpler method for compatibility)
                chunk_filtered.to_sql(
                    table_name,
                    self.conn,
                    if_exists='append',
                    index=False
                )
                
                total_rows += len(chunk_filtered)
                
                # Progress update
                if chunk_num % 5 == 0:
                    print(f"  Imported {total_rows:,} rows...", end='\r')
            
            elapsed = time.time() - start_time
            print(f"\n[SUCCESS] Imported {total_rows:,} rows to {table_name} in {elapsed:.2f} seconds")
            return total_rows
            
        except Exception as e:
            print(f"[ERROR] Error importing {csv_path}: {e}")
            return 0
    
    def import_all_csvs(self):
        """Import all CSV files to SQLite"""
        print("="*60)
        print("Starting CSV import to SQLite database...")
        print("="*60)
        
        # Create connection and tables
        self.create_connection()
        self.create_tables()
        
        # Define column mappings (map CSV columns to DB columns)
        salesorder_columns = {
            'Id': 'Id',
            'customeridname': 'customeridname',
            'totalamount': 'totalamount',
            'totaltax': 'totaltax',
            'statuscode': 'statuscode',
            'modifiedon': 'modifiedon',
            'createdon': 'createdon',
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
            rows = self.import_csv_to_table(csv_path, table_name, columns)
            total_imported += rows
        
        # Create indexes after import
        if total_imported > 0:
            self.create_indexes()
        
        print(f"\n{'='*60}")
        print(f"[COMPLETE] Import complete! Total rows imported: {total_imported:,}")
        print(f"Database size: {os.path.getsize(self.db_path) / 1024**2:.2f} MB")
        print(f"{'='*60}")
        
        # Verify data
        self.verify_import()
        
        # Close connection
        self.conn.close()
    
    def verify_import(self):
        """Verify the imported data"""
        print("\nVerifying imported data...")
        cursor = self.conn.cursor()
        
        tables = ['salesorder', 'quote', 'quotedetail']
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table}: {count:,} rows")
    
    def test_performance(self):
        """Test query performance"""
        print("\nTesting query performance...")
        self.create_connection()
        cursor = self.conn.cursor()
        
        # Test query 1: Top customers
        start = time.time()
        cursor.execute("""
            SELECT customeridname, SUM(totalamount) as total
            FROM salesorder
            WHERE customeridname IS NOT NULL
            GROUP BY customeridname
            ORDER BY total DESC
            LIMIT 5
        """)
        results = cursor.fetchall()
        elapsed = time.time() - start
        print(f"  Top 5 customers query: {elapsed:.3f} seconds")
        
        # Test query 2: Count by status
        start = time.time()
        cursor.execute("""
            SELECT statuscode, COUNT(*) as count
            FROM salesorder
            GROUP BY statuscode
        """)
        results = cursor.fetchall()
        elapsed = time.time() - start
        print(f"  Status distribution query: {elapsed:.3f} seconds")
        
        self.conn.close()

if __name__ == "__main__":
    importer = CSVToSQLiteImporter()
    importer.import_all_csvs()
    importer.test_performance()