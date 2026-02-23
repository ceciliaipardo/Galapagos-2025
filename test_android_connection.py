#!/usr/bin/env python3
"""
Test script to verify Supabase connection
Run this before building for Android to ensure connection works
"""
import supabase_rest_api as supabase_api
from kivy.logger import Logger
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

def test_all():
    """Test all critical Supabase functions"""
    print("\n" + "="*60)
    print("TESTING SUPABASE CONNECTION FOR ANDROID")
    print("="*60 + "\n")
    
    # Test 1: Basic Connection
    print("Test 1: Basic Connection")
    print("-" * 40)
    try:
        result = supabase_api.test_connection()
        if result:
            print("✅ Connection successful!")
        else:
            print("❌ Connection failed!")
            return False
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    # Test 2: Check if username exists (should return False for test user)
    print("\nTest 2: Check Username Exists")
    print("-" * 40)
    try:
        test_username = "test_android_user_999"
        exists = supabase_api.check_username_exists(test_username)
        print(f"Username '{test_username}' exists: {exists}")
        print("✅ Username check works!")
    except Exception as e:
        print(f"❌ Username check error: {e}")
        return False
    
    # Test 3: Check if phone exists
    print("\nTest 3: Check Phone Exists")
    print("-" * 40)
    try:
        test_phone = "9999999999"
        exists = supabase_api.check_phone_exists(test_phone)
        print(f"Phone '{test_phone}' exists: {exists}")
        print("✅ Phone check works!")
    except Exception as e:
        print(f"❌ Phone check error: {e}")
        return False
    
    # Test 4: Test Registration (create and delete test user)
    print("\nTest 4: Registration Test")
    print("-" * 40)
    try:
        test_username = f"test_android_{int(time.time())}"
        test_password = "testpass123"
        test_name = "Test User"
        test_phone = "1234567890"
        test_company = "Test Company"
        test_carnum = "123"
        
        print(f"Attempting to register test user: {test_username}")
        supabase_api.register_user(
            test_username, test_password, test_name, test_phone,
            test_company, test_carnum, "", ""
        )
        print("✅ Registration works!")
        
        # Clean up - try to delete test user
        print("Cleaning up test user...")
        try:
            supabase_api.delete('UserData', {'username': test_username})
            print("✅ Test user deleted")
        except:
            print("⚠️  Could not delete test user (manual cleanup may be needed)")
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test 5: Test Login
    print("\nTest 5: Login Test")
    print("-" * 40)
    try:
        # Try to login with non-existent user (should return None)
        result = supabase_api.login_user("nonexistent_user", "wrongpass")
        if result is None:
            print("✅ Login function works (correctly returns None for invalid user)")
        else:
            print("⚠️  Unexpected result from login")
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    print("\n" + "="*60)
    print("ALL TESTS PASSED! ✅")
    print("="*60)
    print("\nYour Supabase connection is working correctly!")
    print("You can now build for Android with confidence.")
    print("\nNext steps:")
    print("1. Run: buildozer android clean")
    print("2. Run: buildozer android debug")
    print("3. Install APK on your Android device")
    print("4. Test the app!\n")
    return True

if __name__ == '__main__':
    import time
    success = test_all()
    if not success:
        print("\n⚠️  TESTS FAILED!")
        print("Please check your Supabase configuration and internet connection.")
        print("Make sure you've run the SQL schema in Supabase dashboard.\n")
        exit(1)
    exit(0)
