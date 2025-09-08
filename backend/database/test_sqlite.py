"""Test SQLite database"""
import sqlite3

conn = sqlite3.connect('crm_analytics.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables found:", tables)

# Check row counts
for table in tables:
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"{table[0]}: {count:,} rows")

conn.close()