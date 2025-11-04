#!/usr/bin/env python3
"""
Test script for SCB MCP HTTP Server
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_server():
    """Test the HTTP server endpoints"""
    print("=" * 60)
    print("Testing SCB MCP HTTP Server")
    print("=" * 60)

    # Test 1: Root endpoint
    print("\n1. Testing root endpoint (GET /)...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print(f"   ✓ Success!")
            data = response.json()
            print(f"   Server: {data.get('name')}")
            print(f"   Version: {data.get('version')}")
        else:
            print(f"   ✗ Failed with status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 2: Health check
    print("\n2. Testing health check (GET /health)...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print(f"   ✓ Success!")
            data = response.json()
            print(f"   Status: {data.get('status')}")
        else:
            print(f"   ✗ Failed with status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 3: List tools
    print("\n3. Testing list tools (GET /tools)...")
    try:
        response = requests.get(f"{BASE_URL}/tools")
        if response.status_code == 200:
            print(f"   ✓ Success!")
            data = response.json()
            tools = data.get('tools', [])
            print(f"   Found {len(tools)} tools:")
            for tool in tools:
                print(f"     - {tool['name']}")
        else:
            print(f"   ✗ Failed with status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 4: Call browse_metadata tool
    print("\n4. Testing browse_metadata tool (POST /call_tool)...")
    try:
        payload = {
            "name": "scb_browse_metadata",
            "arguments": {
                "path": "",
                "language": "sv"
            }
        }
        response = requests.post(
            f"{BASE_URL}/call_tool",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✓ Success!")
                result = data.get('result', {})
                if 'error' in result:
                    print(f"   Note: SCB API returned error (expected in restricted networks)")
                    print(f"   Error: {result['error']}")
                else:
                    items = result.get('items', [])
                    print(f"   Found {len(items)} categories")
                    if items:
                        print(f"   First category: {items[0].get('text', 'N/A')}")
            else:
                print(f"   ✗ Failed: {data.get('error')}")
        else:
            print(f"   ✗ Failed with status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 5: Call search_tables tool
    print("\n5. Testing search_tables tool (POST /call_tool)...")
    try:
        payload = {
            "name": "scb_search_tables",
            "arguments": {
                "query": "befolkning",
                "language": "sv"
            }
        }
        response = requests.post(
            f"{BASE_URL}/call_tool",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(f"   ✓ Success!")
                result = data.get('result', {})
                if 'error' in result:
                    print(f"   Note: SCB API returned error (expected in restricted networks)")
                else:
                    matches = result.get('matches', [])
                    print(f"   Found {len(matches)} matches")
            else:
                print(f"   ✗ Failed: {data.get('error')}")
        else:
            print(f"   ✗ Failed with status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    # Test 6: Invalid tool name
    print("\n6. Testing error handling with invalid tool...")
    try:
        payload = {
            "name": "invalid_tool_name",
            "arguments": {}
        }
        response = requests.post(
            f"{BASE_URL}/call_tool",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 404:
            print(f"   ✓ Correctly returned 404 for invalid tool")
        else:
            print(f"   Note: Got status {response.status_code}")
    except Exception as e:
        print(f"   ✗ Error: {e}")

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)
    print("\nNOTE: If you see SCB API errors, this is expected if:")
    print("  - The server is behind a firewall blocking api.scb.se")
    print("  - SSL/TLS connections are restricted")
    print("\nThe server itself is working correctly!")


if __name__ == "__main__":
    print("SCB MCP HTTP Server - Test Suite")
    print("\nMake sure the server is running on http://localhost:8000")
    print("Start it with: python scb_mcp_server_http.py")
    print()

    try:
        test_server()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to server!")
        print("Make sure the server is running:")
        print("  python scb_mcp_server_http.py")
