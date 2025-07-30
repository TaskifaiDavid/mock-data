#!/usr/bin/env python3
"""
Setup SQLite database with sample data for LangChain SQL agent
"""
import sqlite3
import os
from datetime import datetime, timedelta
import random

def create_database():
    db_path = '/home/david/mockDataRepo/mockDataRepo/backend/dev_database.db'
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create products table
    cursor.execute('''
    CREATE TABLE products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        ean_code TEXT,
        description TEXT
    )
    ''')
    
    # Create resellers table
    cursor.execute('''
    CREATE TABLE resellers (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        contact_email TEXT
    )
    ''')
    
    # Create sales table
    cursor.execute('''
    CREATE TABLE sales (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        reseller_id INTEGER,
        quantity INTEGER NOT NULL,
        sales_amount_eur DECIMAL(10,2) NOT NULL,
        sale_date DATE NOT NULL,
        month INTEGER NOT NULL,
        year INTEGER NOT NULL,
        FOREIGN KEY (product_id) REFERENCES products (id),
        FOREIGN KEY (reseller_id) REFERENCES resellers (id)
    )
    ''')
    
    # Create uploads table for tracking
    cursor.execute('''
    CREATE TABLE uploads (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        filename TEXT NOT NULL,
        status TEXT NOT NULL,
        uploaded_at DATETIME NOT NULL,
        rows_processed INTEGER,
        rows_cleaned INTEGER
    )
    ''')
    
    # Insert sample products
    products_data = [
        (1, 'PRSP100 Premium Headphones', 'Electronics', 299.99, '1234567890123', 'High-quality wireless headphones'),
        (2, 'TECH200 Smart Watch', 'Electronics', 199.99, '1234567890124', 'Fitness tracking smartwatch'),
        (3, 'HOME300 Coffee Maker', 'Appliances', 149.99, '1234567890125', 'Automatic drip coffee maker'),
        (4, 'BOOK400 Programming Guide', 'Books', 49.99, '1234567890126', 'Complete programming reference'),
        (5, 'CLOTH500 Designer Jacket', 'Clothing', 89.99, '1234567890127', 'Waterproof outdoor jacket'),
        (6, 'GAME600 Console Controller', 'Electronics', 59.99, '1234567890128', 'Wireless gaming controller'),
        (7, 'KITCHEN700 Blender', 'Appliances', 79.99, '1234567890129', 'High-speed kitchen blender'),
        (8, 'SPORT800 Running Shoes', 'Clothing', 119.99, '1234567890130', 'Professional running shoes')
    ]
    
    cursor.executemany('INSERT INTO products VALUES (?, ?, ?, ?, ?, ?)', products_data)
    
    # Insert sample resellers
    resellers_data = [
        (1, 'Galilu Electronics', 'Germany', 'orders@galilu.de'),
        (2, 'TechMart USA', 'United States', 'sales@techmart.com'),
        (3, 'Nordic Supplies', 'Sweden', 'info@nordicsupplies.se'),
        (4, 'EuroTech Solutions', 'France', 'contact@eurotech.fr'),
        (5, 'Asian Electronics Hub', 'Japan', 'sales@asianhub.jp'),
        (6, 'UK Premium Store', 'United Kingdom', 'orders@ukpremium.co.uk')
    ]
    
    cursor.executemany('INSERT INTO resellers VALUES (?, ?, ?, ?)', resellers_data)
    
    # Generate sample sales data
    sales_data = []
    base_date = datetime(2024, 1, 1)
    
    for i in range(200):  # Generate 200 sales records
        product_id = random.randint(1, 8)
        reseller_id = random.randint(1, 6)
        quantity = random.randint(1, 50)
        
        # Get product price
        cursor.execute('SELECT price FROM products WHERE id = ?', (product_id,))
        product_price = cursor.fetchone()[0]
        
        sales_amount = quantity * product_price * random.uniform(0.8, 1.2)  # Add some price variation
        
        # Random date in 2024
        random_days = random.randint(0, 350)
        sale_date = base_date + timedelta(days=random_days)
        
        sales_data.append((
            i + 1,
            product_id,
            reseller_id,
            quantity,
            round(sales_amount, 2),
            sale_date.strftime('%Y-%m-%d'),
            sale_date.month,
            sale_date.year
        ))
    
    cursor.executemany('INSERT INTO sales VALUES (?, ?, ?, ?, ?, ?, ?, ?)', sales_data)
    
    # Add some sample uploads
    uploads_data = [
        ('sample-upload-1', 'dev_user_123', 'sales_data_q1.xlsx', 'completed', '2024-01-15 10:30:00', 150, 145),
        ('sample-upload-2', 'dev_user_123', 'product_catalog.xlsx', 'completed', '2024-02-20 14:45:00', 8, 8),
        ('sample-upload-3', 'dev_user_123', 'reseller_info.xlsx', 'completed', '2024-03-10 09:15:00', 6, 6)
    ]
    
    cursor.executemany('INSERT INTO uploads VALUES (?, ?, ?, ?, ?, ?, ?)', uploads_data)
    
    conn.commit()
    
    # Verify data was inserted
    cursor.execute('SELECT COUNT(*) FROM products')
    products_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM resellers')
    resellers_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM sales')
    sales_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM uploads')
    uploads_count = cursor.fetchone()[0]
    
    print(f"Database created successfully!")
    print(f"Products: {products_count}")
    print(f"Resellers: {resellers_count}")
    print(f"Sales: {sales_count}")
    print(f"Uploads: {uploads_count}")
    
    # Show sample data
    print("\nSample products:")
    cursor.execute('SELECT name, category, price FROM products LIMIT 3')
    for row in cursor.fetchall():
        print(f"  - {row[0]} ({row[1]}): €{row[2]}")
    
    print("\nSample sales:")
    cursor.execute('''
        SELECT p.name, r.name, s.quantity, s.sales_amount_eur, s.sale_date
        FROM sales s
        JOIN products p ON s.product_id = p.id
        JOIN resellers r ON s.reseller_id = r.id
        LIMIT 3
    ''')
    for row in cursor.fetchall():
        print(f"  - {row[0]} sold to {row[1]}: {row[2]} units, €{row[3]}, {row[4]}")
    
    conn.close()
    return db_path

if __name__ == '__main__':
    create_database()