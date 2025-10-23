# Android App Crash Fix Guide

## Issues Identified

Your Android app was crashing due to several critical issues:

### 1. **GPS Service Error (Critical)**
- **Problem**: `gps_service.py` had a typo: `Logger.ciritcal` instead of `Logger.critical`
- **Problem**: The service was running an infinite loop without proper implementation
- **Impact**: This caused immediate crashes when the GPS service started
- **Fix**: Corrected typo and implemented proper Android service with sleep intervals

### 2. **Missing Android Permissions**
- **Problem**: Missing critical permissions for GPS background tracking
- **Missing**: `ACCESS_BACKGROUND_LOCATION`, `WAKE_LOCK`, `FOREGROUND_SERVICE`
- **Impact**: App crashes when trying to access location in background
- **Fix**: Added all required permissions to `buildozer.spec`

### 3. **Outdated Android API Configuration**
- **Problem**: Using Android API 32 without minapi specification
- **Impact**: Compatibility issues with newer Android devices
- **Fix**: 
  - Updated to Android API 33
  - Set minapi to 21 for broader device support
  - Updated NDK to 25b

### 4. **Missing Gradle Dependencies**
- **Problem**: No Google Play Services for location tracking
- **Impact**: GPS functionality may not work properly on modern Android
- **Fix**: Added `com.google.android.gms:play-services-location:21.0.1`

## Files Modified

1. **gps_service.py**
   - Fixed typo: `Logger.ciritcal` → `Logger.critical`
   - Implemented proper Android service with PythonService
   - Added 60-second sleep intervals to keep service alive

2. **buildozer.spec**
   - Added missing permissions: `ACCESS_BACKGROUND_LOCATION`, `WAKE_LOCK`, `FOREGROUND_SERVICE`
   - Updated Android API from 32 to 33
   - Set minapi to 21
   - Updated NDK to 25b
   - Added Google Play Services location dependency
   - Explicitly set android.entrypoint

## How to Rebuild the App

### Prerequisites
- Ensure you have Buildozer installed
- Ensure you have a Linux environment (or WSL on Windows)
- Make sure you have adequate disk space (10+ GB)

### Step 1: Clean Previous Build
```bash
buildozer android clean
```

### Step 2: Rebuild the APK
```bash
buildozer android debug
```

This will take 30-60 minutes for the first build as it downloads and compiles all dependencies.

### Step 3: Deploy to Your Phone

#### Option A: Direct USB Install
1. Enable Developer Options on your Android phone
2. Enable USB Debugging
3. Connect phone via USB
4. Run:
```bash
buildozer android deploy run
```

#### Option B: Manual Install
1. After build completes, find the APK in:
   ```
   bin/gct-0.1-arm64-v8a-debug.apk
   ```
2. Transfer to your phone
3. Install the APK
4. Grant all requested permissions when prompted

## Testing on Your Phone

### Step 1: Grant Permissions
When you first open the app, it will request permissions:
- **Location** - Select "Allow all the time" (required for GPS tracking)
- **Internet** - Required for database sync
- Allow any other permissions requested

### Step 2: Test GPS Functionality
1. Log in or register
2. Start a trip
3. Move around (outdoors works best for GPS)
4. Complete the trip
5. Check if statistics are recorded

### Step 3: Check for Crashes
If the app still crashes:
1. Connect phone via USB
2. Enable USB debugging
3. Run to see crash logs:
```bash
adb logcat | grep python
```

## Troubleshooting

### App Still Crashes Immediately
1. **Check permissions**: Go to Settings > Apps > GCT > Permissions
2. **Clear app data**: Settings > Apps > GCT > Storage > Clear Data
3. **Reinstall completely**: Uninstall, then reinstall

### GPS Not Working
1. Ensure Location Services are enabled on phone
2. Test outdoors (GPS doesn't work well indoors)
3. Check if "Location" permission is set to "Allow all the time"

### Cannot Connect to Database
- The app requires MySQL connection for some features
- If MySQL is not available, it will run in SQLite-only mode
- This is expected and won't cause crashes

### Build Fails
1. **Clear buildozer cache**:
   ```bash
   rm -rf .buildozer
   buildozer android clean
   ```

2. **Update buildozer**:
   ```bash
   pip install --upgrade buildozer
   pip install --upgrade cython
   ```

3. **Check Java/SDK installation**: Ensure you have Java 11 or higher

## Additional Recommendations

### For Production Release
1. **Remove test login** in `main.py` line 656:
   ```python
   # DELETE THIS LINE for production:
   localDBLogin('testUser', 'testPassword', 'Test User', '1234567890', 'Company1', '1', 'Company2', '2')
   ```

2. **Update MySQL credentials** if you plan to use remote database:
   - Update host, user, password in `DBConnect()` function

3. **Add app icon**:
   - Create a 512x512 PNG icon
   - Update buildozer.spec:
   ```
   icon.filename = %(source.dir)s/icon.png
   ```

4. **Add splash screen**:
   - Create a splash screen image
   - Update buildozer.spec:
   ```
   presplash.filename = %(source.dir)s/splash.png
   ```

### For Better GPS Tracking
Consider these improvements in future versions:
1. Add GPS accuracy checking
2. Implement GPS signal strength indicator
3. Add option to adjust GPS update frequency
4. Show GPS status on the tracking screen

## Version Information
- App Version: 0.1
- Python: 3.x
- Kivy: Latest
- KivyMD: Latest
- Android API: 33
- Min API: 21
- NDK: 25b

## Support
If you continue to experience crashes after following this guide:
1. Check crash logs with `adb logcat`
2. Verify all permissions are granted
3. Test on a different Android device if possible
4. Ensure your phone has Android 5.0 (API 21) or higher
