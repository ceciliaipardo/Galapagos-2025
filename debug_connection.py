#!/usr/bin/env python3
"""Comprehensive connection debugging"""
import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print("\n" + "="*50)

# Test 1: Import the module
print("Test 1: Importing supabase_rest_api...")
try:
    import supabase_rest_api as api
    print("✓ Module imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check the make_request function signature
print("\nTest 2: Checking make_request function...")
import inspect
sig = inspect.signature(api.make_request)
print(f"make_request signature: {sig}")

# Test 3: Check select function
print("\nTest 3: Checking select function...")
sig = inspect.signature(api.select)
print(f"select signature: {sig}")

# Test 4: Try actual connection
print("\nTest 4: Testing actual connection...")
try:
    result = api.test_connection()
    if result:
        print("✓ Connection SUCCESSFUL")
    else:
        print("✗ Connection FAILED (returned False)")
except Exception as e:
    print(f"✗ Connection FAILED with exception: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Try to query UserData
print("\nTest 5: Attempting to query UserData...")
try:
    users = api.select('UserData', limit=1)
    print(f"✓ Query successful. Found {len(users)} record(s)")
except Exception as e:
    print(f"✗ Query failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*50)
print("Diagnostic complete!")
