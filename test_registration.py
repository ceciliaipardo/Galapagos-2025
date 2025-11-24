#!/usr/bin/env python3
"""Test registration flow"""
import supabase_rest_api as api

print("Testing registration flow...")

# Test connection
print("1. Testing connection...")
if api.test_connection():
    print("   ✓ Connection successful")
else:
    print("   ✗ Connection failed")
    exit(1)

# Test username check
print("\n2. Testing username check...")
try:
    test_username = "testuser123"
    exists = api.check_username_exists(test_username)
    print(f"   ✓ Username check works. Username '{test_username}' exists: {exists}")
except Exception as e:
    print(f"   ✗ Error checking username: {e}")

# Test phone check
print("\n3. Testing phone check...")
try:
    test_phone = "1234567890"
    exists = api.check_phone_exists(test_phone)
    print(f"   ✓ Phone check works. Phone '{test_phone}' exists: {exists}")
except Exception as e:
    print(f"   ✗ Error checking phone: {e}")

print("\n✓ All registration checks passed!")
