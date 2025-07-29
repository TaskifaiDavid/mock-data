#!/usr/bin/env python3
"""
Create Excel File from CSV
Converts the CSV file to a proper Excel format
"""

import pandas as pd

def create_excel_file():
    """Convert CSV to Excel format"""
    
    try:
        # Read the CSV file
        df = pd.read_csv('mock_data_100_rows.csv')
        print(f"📊 Read CSV with {len(df)} rows and {len(df.columns)} columns")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Write to Excel format
        excel_filename = 'mock_data_100_rows.xlsx'
        df.to_excel(excel_filename, index=False, engine='openpyxl')
        
        print(f"✅ Created Excel file: {excel_filename}")
        print(f"📁 File saved successfully")
        
        # Verify the Excel file
        excel_df = pd.read_excel(excel_filename, engine='openpyxl')
        print(f"✅ Verification: Excel file has {len(excel_df)} rows")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_excel_file()
    exit(0 if success else 1)