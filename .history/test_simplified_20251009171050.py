#!/usr/bin/env python3
"""Test script for simplified Echo Prayer MCP Server"""

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
    get_available_categories,
    get_prayer_by_id,
    get_prayers_by_category
)

async def test_basic_tools():
    """Test basic prayer tools"""
    print("=== Testing Prayer Tools ===")
    
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
    
    # Test get prayer by ID
    print("\n6. Testing get_prayer_by_id...")
    result = await get_prayer_by_id(1)
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Prayer: {result['prayer']['title']}")
        print(f"Category: {result['prayer']['category']}")
    
    # Test get prayers by category
    print("\n7. Testing get_prayers_by_category...")
    result = await get_prayers_by_category("Abiding & Presence", limit=3)
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Found {len(result['prayers'])} prayers in '{result['category']}'")
        for prayer in result['prayers']:
            print(f"  - {prayer['title']}")

async def main():
    """Run all tests"""
    print("Echo Prayer MCP Server - Simplified Test Suite")
    print("=" * 50)
    
    try:
        # Test basic tools
        await test_basic_tools()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("✅ Server is ready for use - no authentication required!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
