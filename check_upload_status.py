#!/usr/bin/env python3
"""
Check Upload Status
Checks the status of uploads in the database
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

def check_upload_status():
    """Check upload status and details"""
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    load_dotenv(env_path)
    
    # Get Supabase configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        # Check uploads table
        print("📊 Upload Status Check...")
        uploads_response = supabase.table('uploads').select('*').execute()
        
        if uploads_response.data:
            print(f"✅ Found {len(uploads_response.data)} uploads:")
            for upload in uploads_response.data:
                print(f"\n   📁 Upload: {upload.get('filename', 'N/A')}")
                print(f"      ID: {upload.get('id', 'N/A')}")
                print(f"      Status: {upload.get('status', 'N/A')}")
                print(f"      Error: {upload.get('error_message', 'None')}")
                print(f"      Rows Processed: {upload.get('rows_processed', 'N/A')}")
                print(f"      Processing Time: {upload.get('processing_time_ms', 'N/A')}ms")
                print(f"      Uploaded: {upload.get('uploaded_at', 'N/A')}")
        else:
            print("ℹ️  No uploads found in the database")
        
        # Check how many records are in mock_data
        print("\n📊 Mock Data Count...")
        count_response = supabase.table('mock_data').select('*', count='exact').execute()
        print(f"✅ Total records in mock_data: {count_response.count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking upload status: {str(e)}")
        return False

if __name__ == "__main__":
    success = check_upload_status()
    sys.exit(0 if success else 1)