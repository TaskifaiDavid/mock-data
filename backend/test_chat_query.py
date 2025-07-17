#!/usr/bin/env python3
"""Test the current chat query functionality"""

import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.chat_service import ChatService

async def test_chat_functionality():
    """Test the current chat service with real queries"""
    try:
        print("🤖 Testing current chat functionality...")
        
        chat_service = ChatService()
        
        # Use a dummy user ID for testing
        test_user_id = "550e8400-e29b-41d4-a716-446655440000"  # Standard test UUID
        
        print(f"\n📝 Testing with user_id: {test_user_id}")
        
        # Test simple questions
        test_queries = [
            "Hi",
            "What can you do?", 
            "What are my total sales?",
            "What are my sales for September 2024?",
            "Show me my top resellers"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing query: '{query}'")
            print("-" * 50)
            
            try:
                result = await chat_service.process_query(
                    user_id=test_user_id,
                    message=query,
                    session_id=None
                )
                
                print(f"✅ Query processed successfully")
                print(f"Success: {result.get('success')}")
                print(f"Intent: {result.get('intent')}")
                print(f"Message: {result.get('message')[:200]}...")
                
                if result.get('sql_query'):
                    print(f"SQL: {result.get('sql_query')}")
                    print(f"Results count: {result.get('results_count')}")
                
                if result.get('error'):
                    print(f"Error: {result.get('error')}")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n🎯 Chat functionality test completed!")
        
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chat_functionality())