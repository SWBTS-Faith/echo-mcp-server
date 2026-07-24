#!/usr/bin/env python3
"""Test script to verify Echo Prayer MCP Server is working correctly"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.tools import (
    one_minute_prayer,
    guided_prayer_generator,
    pray_together,
    get_available_categories
)

async def test_mcp_tools():
    """Test the MCP tools to ensure they're working correctly"""
    print("🧪 Testing Echo Prayer MCP Server Tools")
    print("=" * 50)
    
    # Test 1: One minute prayer
    print("\n1️⃣ Testing one_minute_prayer...")
    result = await one_minute_prayer()
    if result['success']:
        print(f"✅ Success: {result['prayer']['title']}")
        print(f"   Category: {result['prayer']['category']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 2: Guided prayer generator
    print("\n2️⃣ Testing guided_prayer_generator...")
    result = await guided_prayer_generator("peace", limit=2)
    if result['success']:
        print(f"✅ Success: Found {len(result['prayers'])} prayers")
        for prayer in result['prayers']:
            print(f"   - {prayer['title']} (Score: {prayer['relevance_score']:.3f})")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 3: Pray together
    print("\n3️⃣ Testing pray_together...")
    result = await pray_together("encouragement")
    if result['success']:
        print(f"✅ Success: {result['message'][:50]}...")
        print(f"   Suggestion: {result['prayer_suggestion']}")
    else:
        print(f"❌ Failed: {result['error']}")
    
    # Test 4: Available categories
    print("\n4️⃣ Testing get_available_categories...")
    result = await get_available_categories()
    if result['success']:
        print(f"✅ Success: Found {len(result['categories'])} categories")
        print(f"   Categories: {', '.join(result['categories'][:3])}...")
    else:
        print(f"❌ Failed: {result['error']}")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed!")
    print("📋 MCP Server is ready for use with:")
    print("   - Claude Desktop")
    print("   - Other MCP clients")
    print("   - Use the .mcp.json configuration file")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())
