#!/usr/bin/env python3
"""
Check pyscbwrapper API methods and test basic functionality
"""

from pyscbwrapper import SCB
import json

print("Checking pyscbwrapper API methods...")
print("=" * 60)

# Create SCB instance
scb = SCB("sv")

# List all available methods
print("\nAvailable methods on SCB object:")
methods = [method for method in dir(scb) if not method.startswith('_')]
for method in methods:
    print(f"  - {method}")

print("\n" + "=" * 60)
print("Testing basic API calls...")
print("=" * 60)

# Test 1: Get info
print("\n1. Testing scb.info()...")
try:
    result = scb.info()
    print(f"   Type: {type(result)}")
    print(f"   Length: {len(result) if isinstance(result, list) else 'N/A'}")
    if isinstance(result, list) and result:
        print(f"   First item keys: {result[0].keys() if isinstance(result[0], dict) else 'N/A'}")
        print(f"   First item: {json.dumps(result[0], indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check URL
print("\n2. Testing scb.get_url()...")
try:
    url = scb.get_url()
    print(f"   URL: {url}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Direct API call
print("\n3. Testing direct API access...")
try:
    import requests
    response = requests.get("https://api.scb.se/OV0104/v1/doris/sv/ssd/")
    print(f"   Status: {response.status_code}")
    print(f"   Response type: {response.headers.get('content-type')}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Data type: {type(data)}")
        if isinstance(data, list) and data:
            print(f"   First item: {json.dumps(data[0], indent=2, ensure_ascii=False)}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()
