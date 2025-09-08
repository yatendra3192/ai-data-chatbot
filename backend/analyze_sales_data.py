import pandas as pd
import numpy as np
from pathlib import Path

# Load and analyze the sales order data
csv_path = Path("./data/uploads/salesorder.csv")
print("Analyzing salesorder.csv...")

# Load data
df = pd.read_csv(csv_path, nrows=10000)
print(f"Loaded {len(df)} rows")
print(f"Columns: {df.columns.tolist()[:20]}...")

# Find key columns for analysis
print("\n=== Key Columns Analysis ===")

# Look for customer columns
customer_cols = [col for col in df.columns if 'customer' in col.lower() or 'account' in col.lower()]
print(f"Customer columns: {customer_cols[:5]}")

# Look for amount/revenue columns
amount_cols = [col for col in df.columns if 'amount' in col.lower() or 'total' in col.lower() or 'revenue' in col.lower()]
print(f"Amount columns: {amount_cols[:10]}")

# Look for product columns
product_cols = [col for col in df.columns if 'product' in col.lower() or 'item' in col.lower()]
print(f"Product columns: {product_cols[:5]}")

# Analyze totalamount column if it exists
if 'totalamount' in df.columns:
    print("\n=== Total Amount Analysis ===")
    print(f"Total amount sum: {df['totalamount'].sum():,.2f}")
    print(f"Average amount: {df['totalamount'].mean():,.2f}")
    print(f"Max amount: {df['totalamount'].max():,.2f}")
    
    # Top customers by total amount
    if 'customeridname' in df.columns:
        top_customers = df.groupby('customeridname')['totalamount'].sum().nlargest(5)
        print("\nTop 5 Customers by Total Amount:")
        for customer, amount in top_customers.items():
            print(f"  {customer}: ${amount:,.2f}")

# Check for status columns
status_cols = [col for col in df.columns if 'status' in col.lower() or 'state' in col.lower()]
print(f"\nStatus columns: {status_cols[:5]}")

# Show data types of numeric columns
numeric_cols = df.select_dtypes(include=[np.number]).columns
print(f"\nNumeric columns ({len(numeric_cols)}): {numeric_cols.tolist()[:10]}...")

# Show sample data
print("\n=== Sample Data ===")
print(df[['ordernumber', 'customeridname', 'totalamount']].head() if 'ordernumber' in df.columns else df.head())