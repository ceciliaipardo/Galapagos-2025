# 🚀 BUILD YOUR APK NOW - STEP BY STEP

WSL is already installed! Follow these exact steps to build your Android APK.

---

## Step 1: Open WSL Terminal

In PowerShell, type:
```powershell
wsl
```

You should see a Linux terminal prompt like: `username@hostname:~$`

---

## Step 2: Navigate to Your Project

```bash
cd /mnt/c/Users/xegui/Galapagos2025
```

Verify you're in the right place:
```bash
ls -la buildozer.spec
```
You should see: `-rw-r--r-- 1 ... buildozer.spec`

---

## Step 3: Install Buildozer (First Time Only)

Run these commands one at a time:

```bash
# Update package list
sudo apt update

# Install dependencies (this takes 5-10 minutes)
# Note: Removed libtinfo5 - not needed in modern Ubuntu
sudo apt install -y git zip unzip openjdk-11-jdk python3-pip autoconf libtool pkg-config zlib1g-dev libncurses-dev cmake libffi-dev libssl-dev

# Install buildozer and dependencies
pip3 install --user --upgrade pip
pip3 install --user buildozer cython

# Add to PATH
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

Verify installation:
```bash
buildozer --version
```

If you get a version number, you're ready!

---

## Step 4: Build Your APK

```bash
buildozer android debug
```

**What to expect:**
- **First time:** 10-30 minutes (downloads Android SDK/NDK ~2-4 GB)
- **Subsequent builds:** 2-5 minutes
- You'll see lots of output - this is normal
- Be patient!

**Common messages you'll see:**
- "Downloading Android SDK..."
- "Building for arm64-v8a, armeabi-v7a..."
- "Compiling..."

---

## Step 5: When Build Completes

Success looks like:
```
# Android packaging done!
# APK GCT-0.1-arm64-v8a_armeabi-v7a-debug.apk available in the bin directory
```

Your APK location:
```
/mnt/c/Users/xegui/Galapagos2025/bin/GCT-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

Or on Windows:
```
C:\Users\xegui\Galapagos2025\bin\GCT-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

---

## Step 6: Install on Android Phone

### Method A: Via USB Cable

1. Enable USB debugging on phone:
   - Settings > About Phone > Tap "Build Number" 7 times
   - Settings > Developer Options > Enable USB Debugging

2. Connect phone to computer

3. In WSL, run:
```bash
adb devices
# You should see your device listed

adb install bin/GCT-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

### Method B: Via File Transfer

1. Copy APK from Windows:
   - Open: `C:\Users\xegui\Galapagos2025\bin`
   - Copy `GCT-0.1-arm64-v8a_armeabi-v7a-debug.apk` to phone

2. On phone:
   - Open file manager
   - Find the APK file
   - Tap to install
   - Allow "Install from unknown sources" if prompted

---

## Step 7: Test the App

1. Open "GCT" app on phone
2. Login:
   - Username: `123`
   - Password: `123`
3. Grant location permissions when prompted
4. Select car and start a test trip
5. Drive around for 2-3 minutes
6. Complete trip
7. View statistics

---

## 🔧 TROUBLESHOOTING

### If "buildozer: command not found"

```bash
export PATH=$PATH:~/.local/bin
buildozer --version
```

### If build fails with "No SDK found"

```bash
buildozer android clean
buildozer android debug
```

### If you see "Permission denied"

```bash
chmod +x ~/.local/bin/buildozer
```

### To see detailed error messages

```bash
buildozer -v android debug
```

### To clean and rebuild from scratch

```bash
buildozer android clean
rm -rf .buildozer
buildozer android debug
```

---

## 📱 QUICK COMMANDS REFERENCE

```bash
# Enter WSL
wsl

# Go to project
cd /mnt/c/Users/xegui/Galapagos2025

# Build APK
buildozer android debug

# Install on phone (USB)
adb install bin/GCT-0.1-arm64-v8a_armeabi-v7a-debug.apk

# Check phone is connected
adb devices

# View app logs
adb logcat | grep python

# Clean build
buildozer android clean
```

---

## ⏱️ EXPECTED BUILD TIME

**First Build:**
- Downloading SDK/NDK: 5-10 minutes
- Compiling: 10-20 minutes
- **Total: 15-30 minutes**

**Subsequent Builds:**
- No downloads needed
- Compiling only: 2-5 minutes

---

## ✅ SUCCESS INDICATORS

You'll know it worked when you see:
1. ✅ "Android packaging done!"
2. ✅ APK file appears in `bin/` folder
3. ✅ No error messages at the end
4. ✅ App installs and opens on phone
5. ✅ You can login with credentials

---

## 🎉 NEXT STEPS AFTER SUCCESSFUL BUILD

1. **Test thoroughly** on multiple devices
2. **Create release build:**
   ```bash
   buildozer android release
   ```
3. **Sign the APK** for distribution
4. **Upload to Google Play Store** (optional)

---

## 📞 NEED HELP?

**Build Error?**
- Check WSL is updated: `wsl --update`
- Check disk space: `df -h`
- Check internet: `ping google.com`

**App Crashes?**
- Check logs: `adb logcat | grep python`
- Verify permissions granted
- Test internet connection

**Login Issues?**
- Verify internet connection on phone
- Check credentials: 123 / 123
- Test database: `python test_connection.py`

---

**Good luck with your build! The app is fully verified and ready. Just follow these steps!** 🚀
