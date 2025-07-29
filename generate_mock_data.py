#!/usr/bin/env python3
"""
Mock Data Generator
Generates 100 rows of realistic mock data for the mock_data table
"""

import csv
import random
import uuid
from datetime import datetime, timedelta

def generate_mock_data():
    """Generate 100 rows of mock data matching the database structure"""
    
    # Sample data patterns from existing database
    resellers = ['reseller1', 'reseller2', 'reseller3', 'reseller4', 'reseller5']
    functional_names = ['PRSP100', 'PRRC30', 'PRNP50', 'PRWS25', 'PRBT75', 'PRGL40', 'PRMX60', 'PRDT35', 'PREX90']
    currencies = ['SEK', 'USD', 'GBP', 'EUR', 'NOK', 'DKK', 'CAD', 'AUD']
    
    # EAN prefix for BIBBI products (735015 is the existing pattern)
    ean_prefix = '735015'
    
    # Generate data
    mock_data = []
    
    for i in range(100):
        # Generate random EAN (keeping existing pattern)
        ean_suffix = str(random.randint(430000, 499999))
        product_ean = ean_prefix + ean_suffix
        
        # Random month and year
        month = random.randint(1, 12)
        year = random.choice([2024, 2025])
        
        # Random quantity (1-50 units)
        quantity = random.randint(1, 50)
        
        # Random currency
        currency = random.choice(currencies)
        
        # Generate sales values (local currency varies by currency)
        if currency == 'USD':
            sales_lc = round(random.uniform(50, 800), 2)
            sales_eur = round(sales_lc * 0.85, 2)  # USD to EUR approximation
        elif currency == 'GBP':
            sales_lc = round(random.uniform(40, 700), 2)
            sales_eur = round(sales_lc * 1.15, 2)  # GBP to EUR approximation
        elif currency == 'SEK':
            sales_lc = round(random.uniform(500, 8000), 2)
            sales_eur = round(sales_lc * 0.09, 2)  # SEK to EUR approximation
        elif currency == 'EUR':
            sales_lc = round(random.uniform(50, 700), 2)
            sales_eur = sales_lc  # Already in EUR
        else:  # NOK, DKK, CAD, AUD
            sales_lc = round(random.uniform(300, 5000), 2)
            sales_eur = round(sales_lc * 0.10, 2)  # Rough approximation
        
        # Random reseller and functional name
        reseller = random.choice(resellers)
        functional_name = random.choice(functional_names)
        
        # Create record
        record = {
            'product_ean': product_ean,
            'month': month,
            'year': year,
            'quantity': quantity,
            'sales_lc': sales_lc,
            'sales_eur': sales_eur,
            'currency': currency,
            'reseller': reseller,
            'functional_name': functional_name
        }
        
        mock_data.append(record)
    
    return mock_data

def write_csv(data, filename):
    """Write mock data to CSV file"""
    
    # Define CSV headers based on database structure
    headers = [
        'product_ean',
        'month', 
        'year',
        'quantity',
        'sales_lc',
        'sales_eur', 
        'currency',
        'reseller',
        'functional_name'
    ]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"✅ Generated {len(data)} rows of mock data in {filename}")

if __name__ == "__main__":
    # Generate mock data
    print("🔄 Generating 100 rows of mock data...")
    mock_data = generate_mock_data()
    
    # Write to CSV
    csv_filename = "mock_data_100_rows.csv"
    write_csv(mock_data, csv_filename)
    
    # Display sample of generated data
    print(f"\n📊 Sample of generated data (first 5 rows):")
    for i, record in enumerate(mock_data[:5], 1):
        print(f"   {i}. EAN: {record['product_ean']}, {record['functional_name']}, "
              f"{record['reseller']}, {record['month']}/{record['year']}, "
              f"{record['quantity']} units, {record['sales_eur']} EUR")
    
    print(f"\n🎉 Mock data generation completed!")
    print(f"📁 File saved as: {csv_filename}")