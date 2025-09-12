"""
Import ALL CSV files to SQLite Database with ALL columns
Imports salesorder (199 cols), Quote (256 cols), and quotedetail (195 cols)
"""
import pandas as pd
import sqlite3
import os
import time
from pathlib import Path

class CompleteCSVToSQLiteImporter:
    def __init__(self):
        self.db_path = "crm_complete.db"  # Complete database with all columns
        self.chunk_size = 100  # Small chunks due to many columns
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
    
    def clean_column_name(self, col):
        """Clean column name for SQLite compatibility"""
        # Remove BOM and clean column name
        clean_col = col.replace('\ufeff', '').strip()
        # Replace spaces and special chars with underscore
        clean_col = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_col)
        # Ensure column doesn't start with number
        if clean_col and clean_col[0].isdigit():
            clean_col = 'col_' + clean_col
        return clean_col
    
    def import_table_with_all_columns(self, csv_path: str, table_name: str):
        """Import CSV file with ALL columns to SQLite table"""
        if not os.path.exists(csv_path):
            print(f"[ERROR] CSV file not found: {csv_path}")
            return 0
            
        print(f"\n{'='*60}")
        print(f"Importing {table_name} from {os.path.basename(csv_path)}")
        print(f"{'='*60}")
        
        try:
            # Read first chunk to get column names
            print("Reading column structure...")
            first_chunk = pd.read_csv(csv_path, nrows=100, low_memory=False, encoding='utf-8-sig')
            columns = first_chunk.columns.tolist()
            print(f"Found {len(columns)} columns")
            
            # Clean column names
            clean_columns = {}
            for col in columns:
                clean_columns[col] = self.clean_column_name(col)
            
            # Drop existing table
            cursor = self.conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # Create table with all columns
            print(f"Creating {table_name} table with {len(columns)} columns...")
            create_sql = f"CREATE TABLE {table_name} (\n"
            column_defs = []
            
            for orig_col, clean_col in clean_columns.items():
                if clean_col.lower() == 'id':
                    column_defs.append(f"    {clean_col} TEXT PRIMARY KEY")
                else:
                    column_defs.append(f"    {clean_col} TEXT")
            
            create_sql += ",\n".join(column_defs) + "\n)"
            cursor.execute(create_sql)
            self.conn.commit()
            
            # Import data in chunks
            print(f"Importing data (chunk size: {self.chunk_size} rows)...")
            total_rows = 0
            start_time = time.time()
            chunk_count = 0
            
            for chunk in pd.read_csv(csv_path, chunksize=self.chunk_size, 
                                    low_memory=False, encoding='utf-8-sig'):
                # Rename columns to clean names
                chunk = chunk.rename(columns=clean_columns)
                
                # Clean data (replace NaN with None)
                chunk = chunk.where(pd.notnull(chunk), None)
                
                # Insert to SQLite
                chunk.to_sql(
                    table_name,
                    self.conn,
                    if_exists='append',
                    index=False
                )
                
                total_rows += len(chunk)
                chunk_count += 1
                
                # Progress update every 10 chunks
                if chunk_count % 10 == 0:
                    elapsed = time.time() - start_time
                    rate = total_rows / elapsed if elapsed > 0 else 0
                    print(f"  Progress: {total_rows:,} rows imported ({rate:.0f} rows/sec)")
            
            elapsed = time.time() - start_time
            print(f"\n[SUCCESS] Imported {total_rows:,} rows in {elapsed:.1f} seconds")
            print(f"  Average: {total_rows/elapsed:.0f} rows/second")
            
            # Create indexes on important columns
            self.create_indexes(table_name, clean_columns.values())
            
            return total_rows
            
        except Exception as e:
            print(f"[ERROR] Error importing {csv_path}: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def create_indexes(self, table_name, column_names):
        """Create indexes on important columns"""
        print(f"Creating indexes for {table_name}...")
        cursor = self.conn.cursor()
        
        # Define important columns for each table
        important_columns = {
            'salesorder': ['customeridname', 'totalamount', 'statuscode', 'modifiedon', 
                          'shippingmethodcode', 'prioritycode', 'statecode', 'ordernumber'],
            'quote': ['customeridname', 'totalamount', 'statuscode', 'modifiedon', 
                     'quotenumber', 'name', 'shippingmethodcode'],
            'quotedetail': ['quoteid', 'productidname', 'extendedamount', 'quantity',
                           'priceperunit', 'producttypecode']
        }
        
        # Create indexes for important columns that exist
        if table_name in important_columns:
            for col in important_columns[table_name]:
                # Find the cleaned column name
                matching_cols = [c for c in column_names if col in c.lower()]
                if matching_cols:
                    clean_col = matching_cols[0]
                    try:
                        index_name = f"idx_{table_name}_{clean_col[:20]}"
                        cursor.execute(f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name}({clean_col})")
                        print(f"  Created index on {clean_col}")
                    except Exception as e:
                        print(f"  Could not create index on {clean_col}: {e}")
        
        self.conn.commit()
    
    def import_all_tables(self):
        """Import all three CSV files with all columns"""
        print("\n" + "="*60)
        print("COMPLETE DATABASE IMPORT")
        print("Importing all columns from all three tables")
        print("="*60)
        
        # Create connection
        self.create_connection()
        
        # Define tables to import
        tables = [
            (r"C:\Users\User\Documents\DVwithCC\salesorder.csv", 'salesorder'),
            (r"C:\Users\User\Documents\DVwithCC\Quote.csv", 'quote'),
            (r"C:\Users\User\Documents\DVwithCC\quotedetail.csv", 'quotedetail')
        ]
        
        total_rows = 0
        start_time = time.time()
        
        for csv_path, table_name in tables:
            rows = self.import_table_with_all_columns(csv_path, table_name)
            total_rows += rows
        
        total_time = time.time() - start_time
        
        # Final summary
        print("\n" + "="*60)
        print("IMPORT COMPLETE!")
        print("="*60)
        print(f"Total rows imported: {total_rows:,}")
        print(f"Total time: {total_time:.1f} seconds")
        print(f"Database size: {os.path.getsize(self.db_path) / (1024**3):.2f} GB")
        
        # Verify the import
        self.verify_import()
        
        # Close connection
        self.conn.close()
        
        print("\n[INFO] Database ready at:", self.db_path)
    
    def verify_import(self):
        """Verify the imported data"""
        print("\nVerifying imported data...")
        cursor = self.conn.cursor()
        
        tables = ['salesorder', 'quote', 'quotedetail']
        for table in tables:
            # Get column count
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            
            print(f"  {table}: {row_count:,} rows, {len(columns)} columns")
            
            # Check for specific important columns
            col_names = [col[1] for col in columns]
            if table == 'salesorder':
                important = ['shippingmethodcode', 'prioritycode', 'statecode']
                for col in important:
                    found = any(col in c.lower() for c in col_names)
                    status = "[OK]" if found else "[MISSING]"
                    print(f"    {status} {col}")

if __name__ == "__main__":
    importer = CompleteCSVToSQLiteImporter()
    importer.import_all_tables()