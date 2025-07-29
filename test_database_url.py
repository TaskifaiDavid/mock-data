#!/usr/bin/env python3
"""
Test DATABASE_URL Environment Variable
Check if the backend can access DATABASE_URL
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables first
load_dotenv('/home/david/mockDataRepo/mockDataRepo/backend/.env')

sys.path.append('/home/david/mockDataRepo/mockDataRepo/backend')

from app.utils.config import get_settings

def test_database_url():
    """Test if DATABASE_URL is accessible"""
    
    try:
        print("🔍 Testing DATABASE_URL access...")
        
        # Test direct environment variable access
        direct_url = os.getenv('DATABASE_URL')
        print(f"📋 Direct os.getenv('DATABASE_URL'): {'✅ Found' if direct_url else '❌ Not found'}")
        if direct_url:
            print(f"   Value starts with: {direct_url[:30]}...")
        
        # Test through settings configuration
        settings = get_settings()
        print(f"📋 Settings object created: ✅")
        
        try:
            langchain_url = settings.langchain_database_url
            print(f"📋 settings.langchain_database_url: ✅ Found")
            print(f"   Value starts with: {langchain_url[:30]}...")
        except Exception as e:
            print(f"📋 settings.langchain_database_url: ❌ Error - {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing DATABASE_URL: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_database_url()
    sys.exit(0 if success else 1)