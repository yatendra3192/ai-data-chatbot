"""
Initialize a sample SQLite database for Railway deployment
Creates a smaller sample database with representative data
"""
import sqlite3
import random
from datetime import datetime, timedelta
import os

def create_sample_database():
    """Create a sample database with representative data"""
    db_path = os.path.join(os.path.dirname(__file__), "database", "crm_analytics.db")
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Check if database already exists
    if os.path.exists(db_path):
        print(f"Database already exists at {db_path}")
        return
    
    print("Creating sample database...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS salesorder (
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quote (
            Id TEXT PRIMARY KEY,
            quotenumber TEXT,
            name TEXT,
            customeridname TEXT,
            totalamount REAL,
            totaltax REAL,
            statuscode INTEGER,
            createdon TEXT,
            modifiedon TEXT,
            effectivefrom TEXT,
            effectiveto TEXT,
            billto_city TEXT,
            billto_stateorprovince TEXT,
            billto_country TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quotedetail (
            Id TEXT PRIMARY KEY,
            quoteid TEXT,
            productidname TEXT,
            productdescription TEXT,
            quantity REAL,
            priceperunit REAL,
            extendedamount REAL,
            tax REAL,
            createdon TEXT,
            modifiedon TEXT,
            FOREIGN KEY (quoteid) REFERENCES quote(Id)
        )
    """)
    
    # Generate sample data
    print("Generating sample data...")
    
    # Sample data generators
    cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 
              'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
              'Fort Worth', 'Columbus', 'Charlotte', 'San Francisco', 'Indianapolis', 'Seattle']
    
    countries = ['United States', 'Canada', 'Mexico', 'United Kingdom', 'Germany', 'France']
    
    customers = [f"Customer {i}" for i in range(1, 101)]
    
    products = [
        ('Product A', 'High-quality widget', 99.99),
        ('Product B', 'Premium gadget', 149.99),
        ('Product C', 'Professional tool', 299.99),
        ('Product D', 'Enterprise solution', 999.99),
        ('Product E', 'Basic item', 19.99),
        ('Product F', 'Standard package', 49.99),
        ('Product G', 'Deluxe edition', 199.99),
        ('Product H', 'Ultimate bundle', 499.99)
    ]
    
    # Generate sales orders (1000 records)
    print("Creating sales orders...")
    sales_orders = []
    start_date = datetime.now() - timedelta(days=365)
    
    for i in range(1, 1001):
        order_date = start_date + timedelta(days=random.randint(0, 365))
        sales_orders.append((
            f"SO-{i:06d}",
            random.choice(customers),
            round(random.uniform(100, 10000), 2),
            round(random.uniform(10, 1000), 2),
            random.choice([1, 2, 3]),  # Status codes
            order_date.isoformat(),
            order_date.isoformat(),
            random.choice(cities),
            random.choice(countries),
            f"ORD-{i:06d}"
        ))
    
    cursor.executemany("""
        INSERT INTO salesorder VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, sales_orders)
    
    # Generate quotes (2000 records)
    print("Creating quotes...")
    quotes = []
    quote_ids = []
    
    for i in range(1, 2001):
        quote_date = start_date + timedelta(days=random.randint(0, 365))
        quote_id = f"Q-{i:06d}"
        quote_ids.append(quote_id)
        
        quotes.append((
            quote_id,
            f"QUOTE-{i:06d}",
            f"Quote for {random.choice(customers)}",
            random.choice(customers),
            round(random.uniform(100, 15000), 2),
            round(random.uniform(10, 1500), 2),
            random.choice([1, 2, 3, 4]),
            quote_date.isoformat(),
            quote_date.isoformat(),
            quote_date.isoformat(),
            (quote_date + timedelta(days=30)).isoformat(),
            random.choice(cities),
            random.choice(['CA', 'NY', 'TX', 'FL', 'IL', 'PA']),
            random.choice(countries)
        ))
    
    cursor.executemany("""
        INSERT INTO quote VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, quotes)
    
    # Generate quote details (10000 records)
    print("Creating quote details...")
    quote_details = []
    
    for i in range(1, 10001):
        quote_id = random.choice(quote_ids)
        product = random.choice(products)
        quantity = random.randint(1, 20)
        detail_date = start_date + timedelta(days=random.randint(0, 365))
        
        quote_details.append((
            f"QD-{i:06d}",
            quote_id,
            product[0],
            product[1],
            quantity,
            product[2],
            round(quantity * product[2], 2),
            round(quantity * product[2] * 0.1, 2),  # 10% tax
            detail_date.isoformat(),
            detail_date.isoformat()
        ))
    
    cursor.executemany("""
        INSERT INTO quotedetail VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, quote_details)
    
    # Create indexes for better performance
    print("Creating indexes...")
    cursor.execute("CREATE INDEX idx_salesorder_customer ON salesorder(customeridname)")
    cursor.execute("CREATE INDEX idx_salesorder_date ON salesorder(createdon)")
    cursor.execute("CREATE INDEX idx_quote_customer ON quote(customeridname)")
    cursor.execute("CREATE INDEX idx_quote_date ON quote(createdon)")
    cursor.execute("CREATE INDEX idx_quotedetail_quote ON quotedetail(quoteid)")
    cursor.execute("CREATE INDEX idx_quotedetail_product ON quotedetail(productidname)")
    
    # Commit and close
    conn.commit()
    conn.close()
    
    print(f"Sample database created successfully at {db_path}")
    print("Database contains:")
    print("  - 1,000 sales orders")
    print("  - 2,000 quotes")
    print("  - 10,000 quote details")
    print("Total: 13,000 records")

if __name__ == "__main__":
    create_sample_database()