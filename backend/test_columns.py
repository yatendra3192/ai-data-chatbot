import sqlite3
import pandas as pd

DB_PATH = "database/crm_analytics.db"

# Test query for top client
query = """
SELECT 
    customeridname,
    SUM(totalamount) as total_revenue
FROM salesorder
GROUP BY customeridname
ORDER BY total_revenue DESC
LIMIT 1
"""

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query(query, conn)
conn.close()

print("Query result columns:", df.columns.tolist())
print("\nFirst row as dict:")
row = df.iloc[0].to_dict() if len(df) > 0 else {}
for key, value in row.items():
    print(f"  {key}: {value}")