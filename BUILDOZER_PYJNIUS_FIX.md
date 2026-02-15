# The pyjnius Problem - Manual Fix Required

## The Issue

pyjnius 1.6.1 (which p4a downloads) has Python 2 code: `isinstance(arg, long)`  
Python 3 doesn't have `long` type → Build fails

## Solution: Manually Patch pyjnius

After buildozer downloads pyjnius but before it fails, we need to patch the file.

### **Quick Fix - Run These Commands:**

```bash
cd /mnt/c/Users/xegui/Galapagos2025

# Let buildozer download everything first
buildozer android debug

# When it fails with the pyjnius error, run this fix:
sed -i 's/isinstance(arg, long)/isinstance(arg, int)/g' \
  .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/armeabi-v7a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi

sed -i 's/isinstance(arg, long)/isinstance(arg, int)/g' \
  .buildozer/android/platform/build-arm64-v8a_armeabi-v7a/build/other_builds/pyjnius-sdl2/arm64-v8a__ndk_target_21/pyjnius/jnius/jnius_utils.pxi

# Now rebuild (it will use the patched files)
buildozer android debug
```

### **What This Does:**

Changes this line in pyjnius source:
```python
isinstance(arg, long)  # Python 2 - BREAKS
```

To:
```python
isinstance(arg, int)   # Python 3 - WORKS
```

## Alternative: Remove GPS Service Temporarily

If the patch doesn't work, we can build WITHOUT the GPS service first, then add it later.

### **Edit buildozer.spec:**

```ini
# Comment out the service temporarily
# services = GPS:gps_service.py
```

This will build without the service, then we can add it back once pyjnius issue is resolved.

## Expected Result

After the patch, buildozer should complete successfully and create your APK.
