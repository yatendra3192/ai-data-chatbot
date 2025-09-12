"""
Import CSV files to SQLite Database with ALL columns
This version imports all 199 columns from the salesorder CSV
"""
import pandas as pd
import sqlite3
import os
import time
from pathlib import Path

class FullCSVToSQLiteImporter:
    def __init__(self):
        self.db_path = "crm_analytics_full.db"  # New database with all columns
        self.chunk_size = 100  # Much smaller chunks for 199 columns
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
    
    def import_csv_with_all_columns(self, csv_path: str, table_name: str):
        """Import CSV file with ALL columns to SQLite table"""
        if not os.path.exists(csv_path):
            print(f"[ERROR] CSV file not found: {csv_path}")
            return 0
            
        print(f"\nImporting {csv_path} to {table_name}...")
        print("Reading first chunk to get all columns...")
        
        try:
            # Read first chunk to get column names and types
            first_chunk = pd.read_csv(csv_path, nrows=1000, low_memory=False, encoding='utf-8-sig')
            columns = first_chunk.columns.tolist()
            print(f"Found {len(columns)} columns in CSV")
            
            # Clean column names (remove special characters, spaces)
            clean_columns = {}
            for col in columns:
                # Remove BOM and clean column name
                clean_col = col.replace('\ufeff', '').strip()
                # Replace spaces and special chars with underscore
                clean_col = ''.join(c if c.isalnum() or c == '_' else '_' for c in clean_col)
                # Ensure column doesn't start with number
                if clean_col[0].isdigit():
                    clean_col = 'col_' + clean_col
                clean_columns[col] = clean_col
            
            print(f"Creating table {table_name} with all columns...")
            
            # Drop existing table
            cursor = self.conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            # Create table with all columns (using TEXT type for flexibility)
            create_sql = f"CREATE TABLE {table_name} (\n"
            column_defs = []
            for orig_col, clean_col in clean_columns.items():
                # Make Id the primary key if it exists
                if clean_col.lower() == 'id':
                    column_defs.append(f"    {clean_col} TEXT PRIMARY KEY")
                else:
                    column_defs.append(f"    {clean_col} TEXT")
            create_sql += ",\n".join(column_defs) + "\n)"
            
            cursor.execute(create_sql)
            self.conn.commit()
            print(f"Table created with {len(clean_columns)} columns")
            
            # Now import all data in chunks
            total_rows = 0
            start_time = time.time()
            
            for chunk_num, chunk in enumerate(pd.read_csv(csv_path, chunksize=self.chunk_size, 
                                                         low_memory=False, encoding='utf-8-sig')):
                # Rename columns to clean names
                chunk = chunk.rename(columns=clean_columns)
                
                # Clean data (replace NaN with None)
                chunk = chunk.where(pd.notnull(chunk), None)
                
                # Insert to SQLite (without method='multi' to avoid too many variables error)
                chunk.to_sql(
                    table_name,
                    self.conn,
                    if_exists='append',
                    index=False
                )
                
                total_rows += len(chunk)
                
                # Progress update
                if chunk_num % 5 == 0:
                    print(f"  Imported {total_rows:,} rows...", end='\r')
            
            elapsed = time.time() - start_time
            print(f"\n[SUCCESS] Imported {total_rows:,} rows to {table_name} in {elapsed:.2f} seconds")
            
            # Create indexes on important columns
            print("Creating indexes...")
            important_cols = ['customeridname', 'totalamount', 'statuscode', 'modifiedon', 
                            'shippingmethodcode', 'prioritycode', 'statecode']
            
            for col in important_cols:
                if col in clean_columns.values():
                    try:
                        index_name = f"idx_{table_name}_{col}"
                        cursor.execute(f"CREATE INDEX {index_name} ON {table_name}({col})")
                        print(f"  Created index on {col}")
                    except:
                        pass
            
            self.conn.commit()
            return total_rows
            
        except Exception as e:
            print(f"[ERROR] Error importing {csv_path}: {e}")
            import traceback
            traceback.print_exc()
            return 0
    
    def import_all_csvs(self):
        """Import all CSV files with all columns"""
        print("="*60)
        print("Starting FULL CSV import to SQLite database...")
        print("This will import ALL columns from the CSV files")
        print("="*60)
        
        # Create connection
        self.create_connection()
        
        # Import salesorder with ALL columns
        csv_path = r"C:\Users\User\Documents\DVwithCC\salesorder.csv"
        rows = self.import_csv_with_all_columns(csv_path, 'salesorder')
        
        # Also import quote and quotedetail with their existing columns
        print("\nImporting quote table...")
        quote_df = pd.read_csv(r"C:\Users\User\Documents\DVwithCC\Quote.csv", low_memory=False)
        quote_df.to_sql('quote', self.conn, if_exists='replace', index=False)
        print(f"Imported {len(quote_df):,} rows to quote table")
        
        print("\nImporting quotedetail table...")
        quotedetail_df = pd.read_csv(r"C:\Users\User\Documents\DVwithCC\quotedetail.csv", low_memory=False)
        quotedetail_df.to_sql('quotedetail', self.conn, if_exists='replace', index=False)
        print(f"Imported {len(quotedetail_df):,} rows to quotedetail table")
        
        print(f"\n{'='*60}")
        print(f"[COMPLETE] Import complete!")
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
        
        # Check salesorder columns
        cursor.execute("PRAGMA table_info(salesorder)")
        columns = cursor.fetchall()
        print(f"  salesorder table: {len(columns)} columns")
        
        # Check for specific columns
        col_names = [col[1] for col in columns]
        important_cols = ['shippingmethodcode', 'prioritycode', 'statecode', 'eht_projectname']
        for col in important_cols:
            if col in col_names:
                print(f"    [OK] Found column: {col}")
            else:
                print(f"    [MISSING] Column: {col}")
        
        # Check row counts
        tables = ['salesorder', 'quote', 'quotedetail']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  {table}: {count:,} rows")
            except:
                pass

if __name__ == "__main__":
    importer = FullCSVToSQLiteImporter()
    importer.import_all_csvs()