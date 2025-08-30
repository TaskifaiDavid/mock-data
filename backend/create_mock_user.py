#!/usr/bin/env python3
"""
Create mock user for development mode dashboard testing
"""
import logging
from app.utils.config import get_settings
from supabase import create_client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_mock_user():
    """Create the mock user in Supabase users table"""
    settings = get_settings()
    
    # Use service key to bypass RLS
    service_supabase = create_client(
        settings.supabase_url,
        settings.supabase_service_key
    )
    
    # Mock user data from auth service (minimal fields)
    user_data = {
        "id": "0925f997-eb0d-7426-78f6-6d2da134d15d",
        "email": "user@email.com"
    }
    
    try:
        # Check if user already exists by ID
        existing_user_by_id = service_supabase.table("users").select("*").eq("id", user_data["id"]).execute()
        
        if existing_user_by_id.data:
            logger.info(f"Mock user {user_data['email']} already exists with correct ID")
            return True
            
        # Check if user exists by email with different ID
        existing_user_by_email = service_supabase.table("users").select("*").eq("email", user_data["email"]).execute()
        
        if existing_user_by_email.data:
            existing_user = existing_user_by_email.data[0]
            logger.info(f"User with email {user_data['email']} already exists with ID: {existing_user['id']}")
            logger.info(f"Expected ID: {user_data['id']}")
            logger.info(f"Need to update auth service to use existing user ID: {existing_user['id']}")
            return True
            
        # Insert mock user
        result = service_supabase.table("users").insert(user_data).execute()
        
        if result.data:
            logger.info(f"Successfully created mock user: {user_data['email']} (ID: {user_data['id']})")
            return True
        else:
            logger.error(f"Failed to create mock user: {result}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating mock user: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_mock_user()
    if success:
        print("✅ Mock user created successfully")
    else:
        print("❌ Failed to create mock user")