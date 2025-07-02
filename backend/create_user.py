#!/usr/bin/env python3
"""
Admin script to create users manually.
Usage: python create_user.py <email> <password>
"""

import sys
import asyncio
from app.services.auth_service import AuthService
from app.models.auth import UserRegister


async def create_user(email: str, password: str):
    """Create a new user with the given email and password."""
    try:
        auth_service = AuthService()
        user_data = UserRegister(email=email, password=password)
        
        result = await auth_service.register(user_data)
        print(f"✅ User created successfully!")
        print(f"   ID: {result.user.id}")
        print(f"   Email: {result.user.email}")
        print(f"   Created: {result.user.created_at}")
        
    except Exception as e:
        print(f"❌ Failed to create user: {str(e)}")
        sys.exit(1)


def main():
    if len(sys.argv) != 3:
        print("Usage: python create_user.py <email> <password>")
        print("Example: python create_user.py user@example.com mypassword123")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    
    print(f"Creating user with email: {email}")
    asyncio.run(create_user(email, password))


if __name__ == "__main__":
    main()