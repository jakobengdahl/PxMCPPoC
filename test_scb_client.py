#!/usr/bin/env python3
"""
Test script for SCB MCP Server
Tests basic functionality with SCB API
"""

import asyncio
import json
from pyscbwrapper import SCB


async def test_scb_basic():
    """Test basic SCB functionality"""
    print("=" * 60)
    print("Testing SCB API Connection")
    print("=" * 60)

    # Test Swedish client
    print("\n1. Testing Swedish (sv) client...")
    try:
        scb_sv = SCB("sv")
        root_sv = scb_sv.info()
        print(f"✓ Successfully connected to SCB API (Swedish)")
        print(f"  Found {len(root_sv)} top-level categories")
        if root_sv:
            print(f"  First category: {root_sv[0].get('text', 'N/A')}")
    except Exception as e:
        print(f"✗ Error with Swedish client: {e}")

    # Test English client
    print("\n2. Testing English (en) client...")
    try:
        scb_en = SCB("en")
        root_en = scb_en.info()
        print(f"✓ Successfully connected to SCB API (English)")
        print(f"  Found {len(root_en)} top-level categories")
        if root_en:
            print(f"  First category: {root_en[0].get('text', 'N/A')}")
    except Exception as e:
        print(f"✗ Error with English client: {e}")

    # Test browsing metadata
    print("\n3. Testing metadata browsing...")
    try:
        scb = SCB("sv")
        categories = scb.info()

        # Try to navigate to a common category (e.g., Befolkning/Population)
        for cat in categories:
            if cat.get("type") == "l":  # folder
                cat_id = cat.get("id")
                print(f"  Exploring category: {cat.get('text')} (ID: {cat_id})")

                try:
                    subcats = scb.go_down(cat_id)
                    print(f"    ✓ Found {len(subcats)} subcategories")
                    if subcats and len(subcats) > 0:
                        print(f"      Example: {subcats[0].get('text', 'N/A')}")
                    break
                except Exception as e:
                    print(f"    ✗ Could not access subcategories: {e}")

    except Exception as e:
        print(f"✗ Error browsing metadata: {e}")

    # Test finding a table
    print("\n4. Testing table access...")
    try:
        scb = SCB("sv")

        # Try a well-known table (Population statistics)
        # Note: Table IDs may change, this is just an example
        test_tables = [
            "BE0101N1",  # Befolkning efter ålder och kön
            "TAB638",    # Another common table
        ]

        for table_id in test_tables:
            try:
                print(f"  Trying table: {table_id}")
                scb.set_table(table_id)
                url = scb.get_url()
                print(f"    ✓ Table found: {url}")

                # Get variables
                variables = scb.get_variables()
                print(f"    ✓ Variables available: {list(variables.keys())}")
                break

            except Exception as e:
                print(f"    ✗ Table {table_id} not accessible: {e}")

    except Exception as e:
        print(f"✗ Error accessing table: {e}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)


async def test_mcp_tools():
    """Test MCP tool functions"""
    print("\n" + "=" * 60)
    print("Testing MCP Tool Functions")
    print("=" * 60)

    # Import the server module
    try:
        import sys
        sys.path.insert(0, '/home/user/PxMCPPoC')
        from scb_mcp_server import browse_metadata, search_tables, get_table_metadata

        # Test browse_metadata
        print("\n1. Testing browse_metadata...")
        result = await browse_metadata(path="", language="sv")
        print(f"  Result keys: {list(result.keys())}")
        if "items" in result:
            print(f"  Found {len(result['items'])} items")
            if result['items']:
                print(f"  First item: {result['items'][0].get('text', 'N/A')}")

        # Test search_tables
        print("\n2. Testing search_tables...")
        result = await search_tables(query="befolkning", language="sv")
        print(f"  Result keys: {list(result.keys())}")
        if "matches" in result:
            print(f"  Found {len(result['matches'])} matches")

        print("\n✓ MCP tool functions working correctly")

    except Exception as e:
        print(f"✗ Error testing MCP tools: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("SCB MCP Server - Test Suite")
    print()

    asyncio.run(test_scb_basic())
    asyncio.run(test_mcp_tools())
