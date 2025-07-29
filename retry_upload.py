#!/usr/bin/env python3
"""
Retry Upload Processing
Resets a failed upload back to pending status to retry processing
"""

import os
import sys
from supabase import create_client, Client
from dotenv import load_dotenv

def retry_upload_processing():
    """Reset failed upload to pending for retry"""
    
    # Load environment variables
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    load_dotenv(env_path)
    
    # Get Supabase configuration
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY')
    
    try:
        # Create Supabase client
        supabase: Client = create_client(supabase_url, supabase_service_key)
        
        upload_id = '8affd23c-38da-4b5c-bc4a-7a07fce8b9fd'
        
        # Reset upload status to pending
        print(f"🔄 Resetting upload {upload_id} to pending status...")
        
        update_response = supabase.table('uploads').update({
            'status': 'pending',
            'error_message': None,
            'rows_processed': None,
            'processing_time_ms': None
        }).eq('id', upload_id).execute()
        
        if update_response.data:
            print(f"✅ Upload status reset successfully!")
            print(f"   Upload ID: {upload_id}")
            print(f"   New Status: pending")
            print(f"   The background task should now pick up and process this upload.")
        else:
            print(f"❌ Failed to reset upload status")
        
        return True
        
    except Exception as e:
        print(f"❌ Error resetting upload: {str(e)}")
        return False

if __name__ == "__main__":
    success = retry_upload_processing()
    sys.exit(0 if success else 1)