import pandas as pd
from pathlib import Path

# Test loading the CSV
csv_path = Path("./data/uploads/salesorder.csv")
print(f"CSV exists: {csv_path.exists()}")
print(f"CSV path: {csv_path.absolute()}")

if csv_path.exists():
    print("\nLoading CSV...")
    df = pd.read_csv(csv_path, nrows=10)
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    print("\nFirst few rows:")
    print(df.head())
    
    # Show data types
    print("\nData types:")
    print(df.dtypes)
else:
    print("CSV file not found!")