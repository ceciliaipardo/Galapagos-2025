# Quick Setup Guide - Galapagos Car Tracking React Native

## Prerequisites Check

Before starting, verify you have:
- ✅ Windows 10 or 11
- ✅ At least 15GB free disk space
- ✅ Good internet connection (will download ~3GB)

## Step 1: Install Node.js

1. Go to https://nodejs.org/
2. Download the **LTS version** (currently v18 or v20)
3. Run the installer
4. Keep all default options
5. Click "Install"
6. **Restart your computer** after installation

### Verify Node.js Installation

Open Command Prompt and run:
```cmd
node --version
npm --version
```

You should see version numbers like `v18.x.x` and `9.x.x`

## Step 2: Install Android Studio

### Download and Install

1. Go to https://developer.android.com/studio
2. Download Android Studio
3. Run the installer
4. In the setup wizard:
   - Select "Standard" installation
   - Accept all licenses
   - Let it download Android SDK (this takes 15-30 minutes)

### Configure Android SDK

1. Open Android Studio
2. Click "More Actions" > "SDK Manager"
3. In "SDK Platforms" tab, check:
   - ✅ Android 13.0 (Tiramisu) - API Level 33
   - ✅ Android 12.0 (S) - API Level 31
4. In "SDK Tools" tab, check:
   - ✅ Android SDK Build-Tools
   - ✅ Android Emulator
   - ✅ Android SDK Platform-Tools
5. Click "Apply" and let it download (10-20 minutes)

### Set Environment Variables

1. Press `Windows + R`, type `sysdm.cpl`, press Enter
2. Click "Advanced" tab > "Environment Variables"
3. Under "User variables", click "New":
   - Variable name: `ANDROID_HOME`
   - Variable value: `C:\Users\YOUR_USERNAME\AppData\Local\Android\Sdk`
   - Replace `YOUR_USERNAME` with your actual username
4. Find "Path" in User variables, select it, click "Edit"
5. Click "New" and add these one by one:
   - `%ANDROID_HOME%\platform-tools`
   - `%ANDROID_HOME%\emulator`
   - `%ANDROID_HOME%\tools`
   - `%ANDROID_HOME%\tools\bin`
6. Click OK on all dialogs
7. **Restart your computer**

### Verify Android Setup

Open a NEW Command Prompt and run:
```cmd
adb version
```

You should see ADB version information.

## Step 3: Create Android Emulator (Virtual Phone)

1. Open Android Studio
2. Click "More Actions" > "Virtual Device Manager"
3. Click "Create Device"
4. Select "Pixel 5" (or any phone) > Click "Next"
5. Select "Tiramisu" (API Level 33) > Click "Next"
   - If not downloaded, click "Download" and wait
6. Name it "Pixel_5_API_33" > Click "Finish"
7. Click the ▶️ play button to start the emulator
8. Wait for the phone to fully boot up (2-3 minutes)

## Step 4: Initialize React Native Project

Open Command Prompt in your project directory:

```cmd
cd C:\Users\xegui\OneDrive\Documentos\Galapagos-2025
npx react-native init GalapagosCarTracking
```

This will take 5-10 minutes to download and set up.

## Step 5: Copy Your App Files

After the project is created, copy files:

```cmd
cd GalapagosCarTracking

:: Delete the default App.js
del App.js

:: Copy your files (you'll need to do this manually or with File Explorer)
:: Copy from: Galapagos-2025\react-native-app\
:: To: Galapagos-2025\GalapagosCarTracking\
```

**Manual Copy Steps:**
1. Open File Explorer
2. Navigate to `Galapagos-2025\react-native-app\`
3. Copy these files/folders to `Galapagos-2025\GalapagosCarTracking\`:
   - `App.js` (replace existing)
   - `package.json` (replace existing)
   - `src\` folder (entire folder)

## Step 6: Install Dependencies

```cmd
cd C:\Users\xegui\OneDrive\Documentos\Galapagos-2025\GalapagosCarTracking
npm install
```

This will take 3-5 minutes.

## Step 7: Configure Android Permissions

Edit the Android manifest file:

**File:** `android\app\src\main\AndroidManifest.xml`

Add these lines after `<manifest>` and before `<application>`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

## Step 8: Link Native Dependencies

```cmd
cd C:\Users\xegui\OneDrive\Documentos\Galapagos-2025\GalapagosCarTracking
npx react-native link react-native-geolocation-service
npx react-native link react-native-sqlite-storage
```

## Step 9: Start Metro Bundler

Open a Command Prompt:

```cmd
cd C:\Users\xegui\OneDrive\Documentos\Galapagos-2025\GalapagosCarTracking
npm start
```

**Keep this window open!** You'll see:
```
Welcome to Metro!
Fast - Scalable - Integrated
```

## Step 10: Run on Emulator

Open a SECOND Command Prompt:

```cmd
cd C:\Users\xegui\OneDrive\Documentos\Galapagos-2025\GalapagosCarTracking
npm run android
```

**First run takes 10-15 minutes!** You'll see lots of output. This is normal.

The app should launch on your emulator!

## Troubleshooting Common Issues

### Issue: "SDK location not found"

**Solution:** Make sure you set ANDROID_HOME correctly and restarted your computer.

### Issue: "Emulator is not running"

**Solution:**
1. Open Android Studio
2. Go to Virtual Device Manager
3. Click ▶️ on your emulator
4. Wait for it to fully boot
5. Try `npm run android` again

### Issue: "Unable to load script"

**Solution:**
```cmd
cd android
gradlew clean
cd ..
npx react-native start --reset-cache
```

Then in another window:
```cmd
npm run android
```

### Issue: Build fails with "Execution failed"

**Solution:**
```cmd
cd android
gradlew clean
cd ..
npm run android
```

### Issue: Metro bundler shows errors

**Solution:**
```cmd
npm install
npx react-native start --reset-cache
```

## Running on Physical Android Phone

### Enable Developer Mode
1. Go to Settings > About Phone
2. Tap "Build Number" 7 times
3. Go back to Settings > System > Developer Options
4. Enable "USB Debugging"

### Connect and Run
1. Connect phone via USB
2. On phone, allow USB debugging when prompted
3. Verify connection:
   ```cmd
   adb devices
   ```
   Should show your device
4. Run:
   ```cmd
   npm run android
   ```

## Quick Reference Commands

### Start Development
```cmd
# Terminal 1: Start Metro
cd C:\Users\xegui\OneDrive\Documentos\Galapagos-2025\GalapagosCarTracking
npm start

# Terminal 2: Run Android
cd C:\Users\xegui\OneDrive\Documentos\Galapagos-2025\GalapagosCarTracking
npm run android
```

### Reload App
- Press `r` in Metro terminal
- Or shake device/emulator and select "Reload"

### Open Developer Menu
- Emulator: `Ctrl + M`
- Physical device: Shake the phone

### Clean Build
```cmd
cd android
gradlew clean
cd ..
npm run android
```

## Next Steps After Setup

1. ✅ App is running on emulator
2. Test login screen (try typing)
3. Test language toggle (EN/ES button)
4. Implement remaining screens from ScreenPlaceholders.js
5. Add your image assets to assets/images/ folder
6. Build APK for your phone

## Getting Help

If you're stuck:
1. Check the error message in the terminal
2. Google the specific error
3. Check react-native-app/README.md for more troubleshooting
4. Make sure all steps were completed in order

## Success! 🎉

When you see the blue "Welcome!" screen on your emulator, you're ready to go!
