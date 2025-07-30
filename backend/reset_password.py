#!/usr/bin/env python3
"""
Admin script to reset user password.
Usage: python reset_password.py <email> <new_password>
"""

import sys
import asyncio
from app.services.auth_service import AuthService
from app.utils.config import get_settings

async def reset_password(email: str, new_password: str):
    """Reset password for an existing user."""
    try:
        settings = get_settings()
        auth_service = AuthService()
        
        if auth_service.dev_mode:
            print("❌ Cannot reset password in development mode")
            return
        
        # Use admin client to update user password
        try:
            # Get user by email first
            users_response = auth_service.admin_supabase.auth.admin.list_users()
            target_user = None
            
            # Handle different response formats
            users_list = users_response.users if hasattr(users_response, 'users') else users_response
            
            for user in users_list:
                if user.email == email:
                    target_user = user
                    break
            
            if not target_user:
                print(f"❌ User {email} not found")
                return
            
            # Update password
            update_response = auth_service.admin_supabase.auth.admin.update_user_by_id(
                target_user.id,
                {
                    "password": new_password,
                    "email_confirm": True
                }
            )
            
            if update_response.user:
                print(f"✅ Password reset successfully for {email}")
                print(f"   User ID: {update_response.user.id}")
                print(f"   Email confirmed: {update_response.user.email_confirmed_at is not None}")
            else:
                print(f"❌ Failed to reset password for {email}")
                
        except Exception as supabase_error:
            print(f"❌ Supabase error: {str(supabase_error)}")
            
    except Exception as e:
        print(f"❌ Failed to reset password: {str(e)}")
        sys.exit(1)

def main():
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        print("Example: python reset_password.py user@example.com newpassword123")
        sys.exit(1)
    
    email = sys.argv[1]
    new_password = sys.argv[2]
    
    print(f"Resetting password for: {email}")
    asyncio.run(reset_password(email, new_password))

if __name__ == "__main__":
    main()