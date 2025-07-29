#!/usr/bin/env python3
"""
Check Products Table Structure
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

def check_products_table():
    """Check products table structure and data"""
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    load_dotenv(env_path)
    
    # Get Supabase configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Try to query products table
        print("📊 Checking products table...")
        try:
            products_response = supabase.table('products').select('*').limit(5).execute()
            
            if products_response.data:
                print(f"✅ Found {len(products_response.data)} products:")
                for product in products_response.data:
                    print(f"   - Product: {product}")
            else:
                print("ℹ️  Products table exists but is empty")
                
        except Exception as e:
            print(f"❌ Error querying products table: {e}")
            
            # Try to get table info
            print("\n🔍 Trying to get table structure...")
            try:
                # This might fail, but let's see what tables exist
                tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_type = 'BASE TABLE'
                """
                
                # Can't run raw SQL through Supabase client easily, so let's check what we can access
                print("Available operations on products table:")
                
            except Exception as e2:
                print(f"❌ Error getting table structure: {e2}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_products_table()
    sys.exit(0 if success else 1)