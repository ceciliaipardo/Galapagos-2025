# Android App Crash Fix Guide - v2

## Critical Fixes Applied

I've identified and fixed several issues that were causing your Android app to crash immediately on startup:

### 1. **Removed Test Auto-Login (CRITICAL FIX)**
**Problem:** The app was attempting to automatically log in with test credentials on startup:
```python
localDBLogin('testUser', 'testPassword', 'Test User', '1234567890', 'Company1', '1', 'Company2', '2')
```
This was causing crashes because:
- It created database entries without proper error handling
- It bypassed the normal login flow
- It could conflict with the Welcome screen initialization

**Fix:** Removed the auto-login line entirely. Users must now log in normally.

### 2. **Added Permission Error Handling**
**Problem:** Permission requests were failing silently, causing GPS crashes.

**Fix:** Wrapped permission requests in try-catch blocks:
```python
try:
    request_permissions([
        Permission.INTERNET, 
        Permission.ACCESS_BACKGROUND_LOCATION, 
        Permission.ACCESS_FINE_LOCATION, 
        Permission.ACCESS_COARSE_LOCATION,
        Permission.WAKE_LOCK
    ])
except Exception as e:
    Logger.error(f"Permission request failed: {e}")
```

### 3. **Added Database Initialization Error Handling**
**Problem:** If local database creation failed, the app would crash.

**Fix:** Added error handling:
```python
try:
    localDBCreate()
except Exception as e:
    Logger.error(f"Local DB creation failed: {e}")
```

### 4. **Fixed GPS Initialization**
**Problem:** GPS initialization was using `MainApp()` which creates a new app instance instead of using the running instance.

**Fix:** Changed to use `App.get_running_app()`:
```python
try:
    app = App.get_running_app()
    if app:
        app.startGPS(checkFrequency)
except Exception as e:
    Logger.error(f"GPS initialization failed: {e}")
```

### 5. **Added Comprehensive Error Handling for Trip Operations**
**Problem:** Any error in trip start/end would crash the app.

**Fix:** Wrapped all trip operations in try-catch blocks with proper logging.

## How to Rebuild the App

### Prerequisites
You need a Linux environment. Since the app was packaged on a different computer, you'll need to:
1. Set up the same build environment, OR
2. Package it yourself using WSL

### Option 1: If You Have Access to the Original Build Computer

1. Copy the updated `main.py` to that computer
2. Navigate to the project directory
3. Clean previous build:
```bash
buildozer android clean
```

4. Rebuild:
```bash
buildozer -v android debug
```

5. The new APK will be in: `bin/gct-0.1-arm64-v8a-debug.apk`

### Option 2: Package on Your Windows Machine Using WSL

#### Step 1: Install WSL (if not already installed)
```powershell
wsl --install
```
Restart computer after installation.

#### Step 2: Install Build Dependencies in WSL
Open Ubuntu terminal and run:
```bash
# Update packages
sudo apt update && sudo apt upgrade -y

# Install Python and essentials
sudo apt install -y python3 python3-pip openjdk-11-jdk build-essential git zip unzip

# Install build tools
pip3 install --upgrade cython buildozer
```

#### Step 3: Copy Project to WSL
```bash
# Create projects directory
mkdir -p ~/projects
cd ~/projects

# Copy from Windows (adjust path as needed)
cp -r /mnt/c/Projects/Galapagos-2025 .

# Navigate to project
cd Galapagos-2025
```

#### Step 4: Build the APK
```bash
# Clean any previous builds
buildozer android clean

# Build (this takes 30-60 minutes first time)
buildozer -v android debug
```

#### Step 5: Copy APK to Windows
```bash
# Copy to Desktop
cp bin/gct-0.1-arm64-v8a-debug.apk /mnt/c/Users/xegui/Desktop/
```

## Installing on Android Device

### Method 1: Direct Transfer
1. Connect phone to computer via USB
2. Copy `gct-0.1-arm64-v8a-debug.apk` to phone
3. On phone, navigate to the APK and tap it
4. Allow installation from unknown sources if prompted
5. Click Install

### Method 2: ADB Install (if you have ADB)
```bash
adb install -r bin/gct-0.1-arm64-v8a-debug.apk
```

## Testing the Fixed App

### Step 1: First Launch
1. Open the app
2. You should see the Welcome screen (no auto-login)
3. Grant all permissions when prompted:
   - Location: Select "Allow all the time"
   - Internet access

### Step 2: Register or Login
Since auto-login is removed, you must:
1. Register a new account (if you have database connection), OR
2. Use an existing account

### Step 3: Test Trip Functionality
1. Start a trip
2. Select car
3. Select destination
4. Select passengers
5. Select cargo
6. Click Complete to finish

### Step 4: Check for Crashes
If the app crashes:
1. Enable USB Debugging on phone
2. Connect via USB
3. Run: `adb logcat | grep -i python`
4. Share the error logs

## Key Differences from Previous Build

### What Changed:
- ❌ **REMOVED:** Auto-login test code
- ✅ **ADDED:** Comprehensive error handling
- ✅ **ADDED:** Proper permission error handling
- ✅ **ADDED:** GPS initialization safety checks
- ✅ **ADDED:** Database operation error handling
- ✅ **FIXED:** GPS instance reference issues

### What Stayed the Same:
- All UI functionality
- All trip tracking features
- Database structure
- GPS service configuration
- Permissions in buildozer.spec

## Troubleshooting

### App Still Crashes Immediately

1. **Uninstall the old version completely:**
   ```bash
   adb uninstall org.galapagos.gct
   ```
   Then install the new APK.

2. **Check if you have old local database:**
   The app creates a local SQLite database. Old data might cause issues.
   Uninstalling should clear this.

3. **Verify permissions in buildozer.spec:**
   Make sure these lines are in `buildozer.spec`:
   ```ini
   android.permissions = INTERNET,ACCESS_COARSE_LOCATION,ACCESS_FINE_LOCATION,ACCESS_BACKGROUND_LOCATION,WAKE_LOCK,FOREGROUND_SERVICE
   android.api = 33
   android.minapi = 21
   android.ndk = 25b
   ```

4. **Get crash logs:**
   ```bash
   adb logcat *:E | grep python
   ```
   This shows only error logs related to Python.

### Build Fails

1. **Not enough disk space:**
   ```bash
   df -h
   # If low on space:
   buildozer android clean
   rm -rf ~/.buildozer
   ```

2. **Permission denied errors:**
   ```bash
   chmod +x -R .buildozer
   ```

3. **SDK/NDK download fails:**
   Check your internet connection. The first build downloads several GB.

### App Opens but GPS Doesn't Work

1. **Check Location Services:** Make sure they're enabled on the phone
2. **Check Permissions:** Go to Settings > Apps > GCT > Permissions
   - Location should be "Allow all the time"
3. **Test outdoors:** GPS doesn't work well indoors

### Database Connection Issues

The app has two modes:
- **With MySQL:** Requires network connection to MySQL server
- **Without MySQL:** Uses local SQLite only

If MySQL connection fails, it's expected. The app will still work locally.

## Next Steps

After successfully installing the fixed app:

1. **Test basic functionality:**
   - Can you open the app?
   - Can you register/login?
   - Can you navigate between screens?

2. **Test trip features:**
   - Start a trip
   - Does GPS update during trip?
   - Can you complete the trip?
   - Do statistics show correctly?

3. **Report any remaining issues:**
   - If crashes occur, get the logcat output
   - Note exactly what action causes the crash
   - Check if error messages appear on screen

## Summary of File Changes

- ✅ `main.py` - Removed auto-login, added error handling
- ⚠️ `buildozer.spec` - Should already have correct permissions (no changes needed)
- ⚠️ `gps_service.py` - Should already be fixed (no changes needed)

The main fix was removing the problematic auto-login code and adding comprehensive error handling throughout the app's startup and GPS initialization code.
