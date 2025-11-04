#!/usr/bin/env python3
"""
Test direct SCB API access with proper headers
"""

import requests
import json

print("Testing SCB API with different approaches...")
print("=" * 60)

# Test 1: Basic request (will likely fail)
print("\n1. Basic request (no headers)...")
try:
    response = requests.get("https://api.scb.se/OV0104/v1/doris/sv/ssd/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: With User-Agent
print("\n2. Request with User-Agent...")
try:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json'
    }
    response = requests.get("https://api.scb.se/OV0104/v1/doris/sv/ssd/", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success! Got {len(data)} items")
        if data:
            print(f"   First item: {json.dumps(data[0], indent=2, ensure_ascii=False)[:300]}")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Check if pyscbwrapper version needs update
print("\n3. Checking pyscbwrapper version...")
try:
    import pyscbwrapper
    print(f"   Version: {pyscbwrapper.__version__ if hasattr(pyscbwrapper, '__version__') else 'Unknown'}")
    print(f"   Location: {pyscbwrapper.__file__}")
except Exception as e:
    print(f"   Error: {e}")

# Test 4: Alternative API endpoint
print("\n4. Testing alternative endpoint...")
try:
    headers = {
        'User-Agent': 'Python SCB MCP Client/1.0',
        'Accept': 'application/json'
    }
    # Try the PXWEB API endpoint
    response = requests.get("https://api.scb.se/OV0104/v1/doris/sv/ssd/START", headers=headers)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Success! Got response")
        print(f"   Data type: {type(data)}")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")
