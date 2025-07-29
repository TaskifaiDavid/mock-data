#!/usr/bin/env python3
"""
Check Demo Data Quality
Verify the latest processed data has correct values
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

def check_demo_data():
    """Check the quality of demo data"""
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    load_dotenv(env_path)
    
    # Get Supabase configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Get the latest 5 records to check quality
        print("📊 Checking latest demo data quality...")
        latest_response = supabase.table('mock_data').select('*').order('created_at', desc=True).limit(5).execute()
        
        if latest_response.data:
            print(f"✅ Found {len(latest_response.data)} latest records:")
            for i, record in enumerate(latest_response.data, 1):
                print(f"\n   {i}. Record Analysis:")
                print(f"      📦 Product EAN: {record.get('product_ean', 'N/A')}")
                print(f"      📅 Date: {record.get('month', 'N/A')}/{record.get('year', 'N/A')}")
                print(f"      📊 Quantity: {record.get('quantity', 'N/A')}")
                print(f"      💰 Sales LC: {record.get('sales_lc', 'N/A')}")
                print(f"      💶 Sales EUR: {record.get('sales_eur', 'N/A')} ← Should NOT be null")
                print(f"      🏪 Reseller: {record.get('reseller', 'N/A')} ← Should be 'Demo'")
                print(f"      🏷️  Functional Name: {record.get('functional_name', 'N/A')} ← Should be UPPERCASE")
                print(f"      💱 Currency: {record.get('currency', 'N/A')}")
        else:
            print("ℹ️  No data found in mock_data table")
        
        # Check specific issues
        print(f"\n🔍 Quality Check Summary:")
        
        # Check sales_eur nulls
        null_sales_eur = supabase.table('mock_data').select('*', count='exact').is_('sales_eur', 'null').execute()
        print(f"   ❌ Records with NULL sales_eur: {null_sales_eur.count}")
        
        # Check Demo reseller count
        demo_reseller = supabase.table('mock_data').select('*', count='exact').eq('reseller', 'Demo').execute()
        print(f"   ✅ Records with 'Demo' reseller: {demo_reseller.count}")
        
        # Check uppercase functional names (sample check)
        if latest_response.data:
            uppercase_count = 0
            for record in latest_response.data:
                fn = record.get('functional_name', '')
                if fn and fn.isupper():
                    uppercase_count += 1
            print(f"   ✅ Uppercase functional_name in latest 5: {uppercase_count}/5")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking demo data: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_demo_data()
    sys.exit(0 if success else 1)