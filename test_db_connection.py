#!/usr/bin/env python3
"""
Database Connection Test Script
Tests Supabase database connectivity and retrieves sample data
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

def test_database_connection():
    """Test Supabase database connection and retrieve sample data"""
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    load_dotenv(env_path)
    
    # Get Supabase configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    if not supabase_url or not supabase_service_key:
        print("❌ Error: Missing Supabase configuration in .env file")
        return False
    
    print(f"🔗 Connecting to Supabase at: {supabase_url}")
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        print("✅ Supabase client created successfully")
        
        # Test 1: Check users table
        print("\n📊 Testing users table...")
        users_response = supabase.table('users').select('id, email, created_at').limit(5).execute()
        
        if users_response.data:
            print(f"✅ Found {len(users_response.data)} users:")
            for user in users_response.data:
                print(f"   - ID: {user['id']}, Email: {user.get('email', 'N/A')}")
        else:
            print("ℹ️  No users found in the database")
        
        # Test 2: Check mock_data table
        print("\n📊 Testing mock_data table...")
        mock_data_response = supabase.table('mock_data').select('*').limit(5).execute()
        
        if mock_data_response.data:
            print(f"✅ Found {len(mock_data_response.data)} records in mock_data:")
            for i, record in enumerate(mock_data_response.data, 1):
                print(f"   {i}. {record}")
        else:
            print("ℹ️  No data found in mock_data table")
        
        # Test 3: Check uploads table
        print("\n📁 Testing uploads table...")
        uploads_response = supabase.table('uploads').select('id, filename, uploaded_at').limit(5).execute()
        
        if uploads_response.data:
            print(f"✅ Found {len(uploads_response.data)} uploads:")
            for upload in uploads_response.data:
                print(f"   - {upload.get('filename', 'N/A')} (Uploaded: {upload.get('uploaded_at', 'N/A')})")
        else:
            print("ℹ️  No uploads found in the database")
        
        print("\n🎉 Database connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database_connection()
    sys.exit(0 if success else 1)