#!/usr/bin/env python3
"""
Create user record for the hash-based ID that auth service generates
"""

import hashlib
from app.services.db_service import DatabaseService

def get_hash_user_id(email):
    """Get the hash-based user ID that auth service generates"""
    hash_obj = hashlib.sha256(email.encode())
    hex_string = hash_obj.hexdigest()[:32]
    # Format as UUID: 8-4-4-4-12
    return f"{hex_string[:8]}-{hex_string[8:12]}-{hex_string[12:16]}-{hex_string[16:20]}-{hex_string[20:32]}"

def main():
    email = "test2@example.com"
    hash_user_id = get_hash_user_id(email)
    
    print(f"🔧 Creating user record for hash-based ID")
    print(f"Email: {email}")
    print(f"Hash-based ID: {hash_user_id}")
    
    # Create user record with the hash-based ID
    db_service = DatabaseService()
    
    try:
        # Check what users exist for this email
        existing_email = db_service.service_supabase.table("users").select("*").eq("email", email).execute()
        existing_id = db_service.service_supabase.table("users").select("*").eq("id", hash_user_id).execute()
        
        print(f"Existing by email: {existing_email.data}")
        print(f"Existing by ID: {existing_id.data}")
        
        if existing_id.data:
            print("✅ Hash-based ID already exists:", existing_id.data[0])
        elif existing_email.data:
            print("✅ User exists but with different ID:", existing_email.data[0])
        else:
            print("🔍 Creating new Auth user and users table record...")
            
            # Create user in Supabase Auth first
            auth_result = db_service.service_supabase.auth.admin.create_user({
                "email": email,
                "password": "testpassword123",
                "user_metadata": {"name": "Test User 2"},
                "email_confirm": True
            })
            
            real_auth_id = auth_result.user.id
            print(f"✅ Auth user created with ID: {real_auth_id}")
            
            # Create corresponding users table record
            result = db_service.service_supabase.table("users").insert({
                "id": real_auth_id,
                "email": email
            }).execute()
            print("✅ Users table record created")
            print("   Record:", result.data[0])
            print(f"\n🎯 FOR TESTING: The real user ID is {real_auth_id}, not {hash_user_id}")
            print("   The auth system will use hash-based ID in dev mode, but data will be stored under real ID")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main()