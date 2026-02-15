# How to Package Your App for Android

**Complete step-by-step guide to build the APK**

---

## Prerequisites

You need:
1. ✅ WSL (Windows Subsystem for Linux) with Ubuntu
2. ✅ Buildozer (we'll install it)
3. ✅ Your project files (you have them)

---

## Step 1: Set Up WSL (If Not Already Done)

### Option A: If WSL is already installed
Open PowerShell and type:
```powershell
wsl -d Ubuntu
```

### Option B: If WSL is NOT installed
Open PowerShell as Administrator and run:
```powershell
wsl --install -d Ubuntu
```

Then restart your computer and set up Ubuntu username/password.

---

## Step 2: Install Buildozer in WSL

Open WSL Ubuntu terminal:
```bash
# Navigate to your project
cd /mnt/c/Users/xegui/Galapagos2025

# Update packages
sudo apt update

# Install all dependencies
sudo apt install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    zip \
    unzip \
    openjdk-17-jdk \
    wget \
    libffi-dev \
    libssl-dev \
    build-essential \
    libsqlite3-dev \
    zlib1g-dev \
    ccache \
    pkg-config

# Install Cython
pip3 install --upgrade cython

# Install Buildozer
pip3 install --upgrade buildozer

# Add pip binaries to PATH
export PATH=$PATH:~/.local/bin

# Make it permanent
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

**Time:** 5-10 minutes

---

## Step 3: Clean Build (Important!)

Remove any old build files:

```bash
cd /mnt/c/Users/xegui/Galapagos2025

# Clean everything
buildozer android clean

# Remove old buildozer directory (if exists)
rm -rf .buildozer
```

---

## Step 4: Build the APK

### For Testing (Debug Build):

```bash
buildozer android debug
```

**What happens:**
1. Downloads Android SDK (~500 MB) - first time only
2. Downloads Android NDK (~900 MB) - first time only
3. Compiles Python for Android
4. Packages your app with all dependencies
5. Creates APK file in `bin/` folder

**Time:** 
- First build: 30-60 minutes (downloading + compiling)
- Subsequent builds: 5-10 minutes

**Watch for errors:**
The terminal will show progress. If it stops with an error, scroll up to see what failed.

### For Production (Release Build):

```bash
buildozer android release
```

**Note:** Release builds need to be signed before installing.

---

## Step 5: Find Your APK

After successful build:

```bash
ls -lh bin/
```

You'll see something like:
```
gct-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

**Copy to Windows:**
```bash
cp bin/*.apk /mnt/c/Users/xegui/Desktop/
```

Now the APK is on your Windows Desktop!

---

## Step 6: Install on Android Device

### Option A: Using ADB (Recommended)

1. **Enable USB Debugging on your phone:**
   - Go to Settings → About Phone
   - Tap "Build Number" 7 times (becomes developer)
   - Go to Settings → Developer Options
   - Enable "USB Debugging"

2. **Connect phone to computer via USB**

3. **Install APK:**
```bash
# In WSL
adb devices  # Should show your device

adb install -r bin/gct-0.1-arm64-v8a_armeabi-v7a-debug.apk
```

### Option B: Manual Install

1. Copy APK to phone (email it, USB transfer, etc.)
2. On phone, open the APK file
3. Allow "Install from Unknown Sources" if asked
4. Tap "Install"

---

## Step 7: Monitor & Debug

While app is running on phone:

```bash
adb logcat | grep -E "python|GPS|Supabase"
```

This shows real-time logs from your app. Super useful for debugging!

---

## Common Issues & Fixes

### Issue: "buildozer: command not found"

**Fix:**
```bash
export PATH=$PATH:~/.local/bin
echo 'export PATH=$PATH:~/.local/bin' >> ~/.bashrc
source ~/.bashrc
```

### Issue: "Permission denied" errors

**Fix:** Use `sudo` for apt install commands:
```bash
sudo apt install <package>
```

### Issue: Build fails with Java errors

**Fix:** Ensure Java 17 is installed:
```bash
java -version  # Should show 17.x
```

If not:
```bash
sudo apt install openjdk-17-jdk
```

### Issue: Out of disk space

**Fix:** Clean old builds:
```bash
buildozer android clean
rm -rf .buildozer
```

### Issue: Build takes forever

**Expected!** First build downloads ~1.5 GB and compiles everything. Grab coffee ☕

Subsequent builds are much faster (5-10 minutes).

---

## Quick Reference - Complete Build Process

```bash
# 1. Open WSL
wsl -d Ubuntu

# 2. Navigate to project
cd /mnt/c/Users/xegui/Galapagos2025

# 3. Clean (optional but recommended)
buildozer android clean

# 4. Build
buildozer android debug

# 5. Wait (first time: 30-60 min, subsequent: 5-10 min)

# 6. Install on phone
adb install -r bin/*.apk

# 7. Monitor logs
adb logcat | grep -E "python|GPS|Supabase"
```

---

## Building for Production

When ready to publish to Google Play:

### Step 1: Create Keystore (One Time Only)

```bash
keytool -genkey -v \
  -keystore galapagos-release.keystore \
  -alias galapagos \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# Save the password somewhere safe!
```

### Step 2: Build Release APK

```bash
buildozer android release
```

### Step 3: Sign the APK

```bash
jarsigner -verbose \
  -sigalg SHA1withRSA \
  -digestalg SHA1 \
  -keystore galapagos-release.keystore \
  bin/gct-0.1-release-unsigned.apk \
  galapagos
```

### Step 4: Align APK

```bash
zipalign -v 4 \
  bin/gct-0.1-release-unsigned.apk \
  bin/gct-0.1-release.apk
```

### Step 5: Upload to Google Play

Go to play.google.com/console and upload `gct-0.1-release.apk`

---

## Troubleshooting Buildozer

### Enable verbose output:

Edit `buildozer.spec`:
```ini
log_level = 2
```

### Check specific errors:

```bash
buildozer android debug 2>&1 | tee build.log
```

This saves all output to `build.log` for review.

### Clean everything:

```bash
buildozer android clean
rm -rf .buildozer
rm -rf bin
```

Then rebuild from scratch.

---

## File Sizes

**Expected APK size:**
- Debug APK: ~25-30 MB
- Release APK: ~20-25 MB (smaller due to optimization)

**Download sizes during first build:**
- Android SDK: ~500 MB
- Android NDK: ~900 MB
- Python dependencies: ~100 MB
- **Total:** ~1.5 GB (only downloaded once)

---

## Performance Tips

### Speed up builds:

1. **Use ccache** (already installed in setup)
2. **Don't clean** between builds unless necessary
3. **Use SSD** for WSL if possible

### Reduce APK size:

Edit `buildozer.spec`:
```ini
# Remove unused architectures
android.archs = arm64-v8a

# Strip debug symbols in release
android.release_artifact = aab
```

---

## Testing Checklist

After building and installing:

1. ☐ App launches successfully
2. ☐ Can register new user
3. ☐ Can login
4. ☐ Can start trip - notification appears
5. ☐ GPS updates visible in logcat
6. ☐ Lock screen - GPS continues
7. ☐ Complete trip - data uploads
8. ☐ Statistics display correctly
9. ☐ No crashes during 15-minute trip
10. ☐ Battery usage acceptable

---

## Need Help?

### Check build logs:
```bash
cat build.log
```

### Check device logs:
```bash
adb logcat > device.log
```

### Verify APK contents:
```bash
unzip -l bin/*.apk | grep -E "\.py$"
```

Should show your Python files are included.

---

## Summary

**Quick start (after setup):**
```bash
wsl -d Ubuntu
cd /mnt/c/Users/xegui/Galapagos2025
buildozer android debug
adb install -r bin/*.apk
```

**First build:** 30-60 minutes  
**Subsequent builds:** 5-10 minutes  
**Result:** APK ready to install on any Android 5.0+ device

**Your app is ready to package! Follow the steps above and you'll have an installable APK.** 📦
