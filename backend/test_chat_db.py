#!/usr/bin/env python3
"""Test script to verify chat database functionality"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.db_service import DatabaseService
from app.utils.config import get_settings

async def test_chat_tables():
    """Test if chat tables exist and basic operations work"""
    try:
        settings = get_settings()
        db = DatabaseService()
        
        print("🔍 Testing chat database functionality...")
        
        # Test 1: Test direct Supabase table access
        print("\n1. Testing direct table access...")
        try:
            # Test direct access to chat_sessions
            result = db.supabase.table("chat_sessions").select("count", count="exact").execute()
            print(f"✅ chat_sessions table exists, found {result.count} sessions")
        except Exception as e:
            print(f"❌ chat_sessions table issue: {e}")
        
        try:
            # Test direct access to chat_messages  
            result = db.supabase.table("chat_messages").select("count", count="exact").execute()
            print(f"✅ chat_messages table exists, found {result.count} messages")
        except Exception as e:
            print(f"❌ chat_messages table issue: {e}")
        
        try:
            # Test direct access to sellout_entries2
            result = db.supabase.table("sellout_entries2").select("count", count="exact").execute()
            print(f"✅ sellout_entries2 table exists, found {result.count} entries")
        except Exception as e:
            print(f"❌ sellout_entries2 table issue: {e}")
        
        # Test 2: Test using raw SQL via RPC function
        print("\n2. Testing raw SQL via RPC...")
        try:
            # Try using the execute_sql_query function from database/schema.sql
            result = db.supabase.rpc('execute_sql_query', {
                'query_text': 'SELECT COUNT(*) as total_count FROM chat_sessions'
            }).execute()
            print(f"✅ Raw SQL works: {result.data}")
        except Exception as e:
            print(f"❌ Raw SQL issue: {e}")
        
        # Test 3: Test the fetch_all function with proper parameters
        print("\n3. Testing fetch_all with dummy user_id...")
        try:
            # Create a dummy user_id for testing
            test_user_id = "00000000-0000-0000-0000-000000000000"
            result = await db.fetch_all("SELECT * FROM chat_sessions WHERE user_id = %s", (test_user_id,))
            print(f"✅ fetch_all works (found {len(result)} sessions for test user)")
        except Exception as e:
            print(f"❌ fetch_all issue: {e}")
        
        # Test 4: Test database schema function
        print("\n4. Testing database schema discovery...")
        try:
            schema = await db.get_database_schema()
            print(f"✅ Schema discovery works, found {len(schema.get('tables', {}))} tables")
            for table_name in schema.get('tables', {}):
                print(f"   - {table_name}")
        except Exception as e:
            print(f"❌ Schema discovery issue: {e}")
        
        print("\n🎯 Chat database test completed!")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_tables())