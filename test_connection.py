#!/usr/bin/env python3
"""Test Supabase connection"""
import supabase_rest_api as api

print("Testing Supabase connection...")
try:
    result = api.test_connection()
    if result:
        print("✓ Connection successful!")
        
        # Try to query UserData
        print("\nTrying to fetch UserData...")
        users = api.select('UserData', limit=1)
        print(f"✓ Successfully queried UserData. Found {len(users)} record(s)")
    else:
        print("✗ Connection failed")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
