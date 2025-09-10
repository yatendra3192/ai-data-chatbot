"""
Initialize SQLite database for Railway deployment
Creates empty tables if database doesn't exist
"""
import sqlite3
import os

def init_database():
    """Create database with empty tables if it doesn't exist"""
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'crm_analytics.db')
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create salesorder table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS salesorder (
            OrderID TEXT,
            CustomerID TEXT,
            OrderDate TEXT,
            ShipDate TEXT,
            Status TEXT,
            TotalAmount REAL,
            City TEXT,
            State TEXT,
            Country TEXT,
            Region TEXT,
            ProductCategory TEXT
        )
    ''')
    
    # Create quote table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quote (
            QuoteID TEXT,
            CustomerID TEXT,
            QuoteDate TEXT,
            ExpirationDate TEXT,
            Status TEXT,
            TotalAmount REAL,
            Discount REAL,
            Tax REAL,
            CustomerName TEXT,
            CustomerEmail TEXT,
            CustomerPhone TEXT,
            BillingAddress TEXT,
            ShippingAddress TEXT,
            PaymentTerms TEXT,
            DeliveryTerms TEXT,
            SalesRep TEXT
        )
    ''')
    
    # Create quotedetail table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quotedetail (
            QuoteDetailID TEXT,
            QuoteID TEXT,
            ProductID TEXT,
            ProductName TEXT,
            Quantity INTEGER,
            UnitPrice REAL,
            Discount REAL,
            Tax REAL,
            TotalPrice REAL
        )
    ''')
    
    # Insert sample data for demo purposes
    cursor.execute('''
        INSERT OR IGNORE INTO salesorder (OrderID, CustomerID, OrderDate, TotalAmount, Status, City, Country)
        VALUES 
        ('ORD-001', 'CUST-001', '2024-01-15', 5000.00, 'Completed', 'New York', 'USA'),
        ('ORD-002', 'CUST-002', '2024-01-16', 7500.00, 'Pending', 'Los Angeles', 'USA'),
        ('ORD-003', 'CUST-003', '2024-01-17', 3200.00, 'Completed', 'Chicago', 'USA'),
        ('ORD-004', 'CUST-001', '2024-01-18', 9800.00, 'Shipped', 'New York', 'USA'),
        ('ORD-005', 'CUST-004', '2024-01-19', 4500.00, 'Completed', 'Houston', 'USA')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO quote (QuoteID, CustomerID, QuoteDate, TotalAmount, Status, CustomerName)
        VALUES 
        ('QT-001', 'CUST-001', '2024-01-10', 5500.00, 'Accepted', 'Acme Corp'),
        ('QT-002', 'CUST-002', '2024-01-11', 8000.00, 'Pending', 'TechStart Inc'),
        ('QT-003', 'CUST-003', '2024-01-12', 3500.00, 'Accepted', 'Global Trade LLC'),
        ('QT-004', 'CUST-004', '2024-01-13', 4800.00, 'Rejected', 'Swift Logistics'),
        ('QT-005', 'CUST-001', '2024-01-14', 10200.00, 'Pending', 'Acme Corp')
    ''')
    
    cursor.execute('''
        INSERT OR IGNORE INTO quotedetail (QuoteDetailID, QuoteID, ProductName, Quantity, UnitPrice, TotalPrice)
        VALUES 
        ('QD-001', 'QT-001', 'Widget Pro', 10, 250.00, 2500.00),
        ('QD-002', 'QT-001', 'Widget Standard', 20, 150.00, 3000.00),
        ('QD-003', 'QT-002', 'Service Package A', 1, 8000.00, 8000.00),
        ('QD-004', 'QT-003', 'Widget Mini', 50, 70.00, 3500.00),
        ('QD-005', 'QT-004', 'Widget Pro', 15, 320.00, 4800.00)
    ''')
    
    conn.commit()
    
    # Get row counts
    tables = ['salesorder', 'quote', 'quotedetail']
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"Table {table}: {count} rows")
    
    conn.close()
    print(f"Database initialized at: {db_path}")
    return db_path

if __name__ == "__main__":
    init_database()