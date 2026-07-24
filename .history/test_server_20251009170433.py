#!/usr/bin/env python3
"""Test script for Echo Prayer MCP Server"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools import (
    one_minute_prayer,
    guided_prayer_generator,
    pray_together,
    generate_prayer_request,
    authenticate_user,
    create_user_account,
    get_available_categories
)

async def test_basic_tools():
    """Test basic prayer tools that don't require authentication"""
    print("=== Testing Basic Prayer Tools ===")
    
    # Test one minute prayer
    print("\n1. Testing one_minute_prayer...")
    result = await one_minute_prayer()
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Prayer: {result['prayer']['title']}")
        print(f"Category: {result['prayer']['category']}")
    
    # Test guided prayer generator
    print("\n2. Testing guided_prayer_generator...")
    result = await guided_prayer_generator("anxiety", limit=2)
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Found {len(result['prayers'])} prayers")
        for prayer in result['prayers']:
            print(f"  - {prayer['title']} (Score: {prayer['relevance_score']:.3f})")
    
    # Test pray together
    print("\n3. Testing pray_together...")
    result = await pray_together("encouragement")
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Message: {result['message']}")
        print(f"Suggestion: {result['prayer_suggestion']}")
    
    # Test generate prayer request
    print("\n4. Testing generate_prayer_request...")
    result = await generate_prayer_request("healing", "recovering from surgery")
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Topic: {result['prayer_request']['topic']}")
        print(f"Prayer points: {len(result['prayer_request']['prayer_points'])}")
    
    # Test get available categories
    print("\n5. Testing get_available_categories...")
    result = await get_available_categories()
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Categories: {result['categories'][:5]}...")  # Show first 5

async def test_authentication():
    """Test authentication features"""
    print("\n=== Testing Authentication ===")
    
    # Test create user account
    print("\n1. Testing create_user_account...")
    result = await create_user_account("testuser", "testpass123", "test@example.com")
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"User created: {result['username']}")
    else:
        print(f"Error: {result['error']}")
    
    # Test authenticate user
    print("\n2. Testing authenticate_user...")
    result = await authenticate_user("testuser", "testpass123")
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Token: {result['access_token'][:20]}...")
        return result['access_token']
    else:
        print(f"Error: {result['error']}")
        return None

async def test_authenticated_tools(token):
    """Test tools that require authentication"""
    if not token:
        print("\n=== Skipping Authenticated Tools (No Token) ===")
        return
    
    print("\n=== Testing Authenticated Tools ===")
    
    from src.tools import (
        share_prayer,
        get_group_prayers,
        list_user_shared_prayers,
        list_prayers_shared_with_user
    )
    
    # Test share prayer
    print("\n1. Testing share_prayer...")
    result = await share_prayer(token, 1, "public", shared_with_group="test_group")
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Message: {result['message']}")
    
    # Test get group prayers
    print("\n2. Testing get_group_prayers...")
    result = await get_group_prayers(token, "test_group")
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Found {len(result['prayers'])} prayers")
    
    # Test list user shared prayers
    print("\n3. Testing list_user_shared_prayers...")
    result = await list_user_shared_prayers(token)
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Message: {result['message']}")
    
    # Test list prayers shared with user
    print("\n4. Testing list_prayers_shared_with_user...")
    result = await list_prayers_shared_with_user(token)
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Message: {result['message']}")

async def main():
    """Run all tests"""
    print("Echo Prayer MCP Server - Test Suite")
    print("=" * 50)
    
    try:
        # Test basic tools
        await test_basic_tools()
        
        # Test authentication
        token = await test_authentication()
        
        # Test authenticated tools
        await test_authenticated_tools(token)
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
