# How to Package Your Android App

## Important: You Need Linux

Buildozer (the tool to package Kivy apps for Android) **only works on Linux**. Since you're on Windows 11, you have two options:

### Option 1: Windows Subsystem for Linux (WSL) - RECOMMENDED
This is the easiest option for Windows users.

### Option 2: Use a Linux Virtual Machine or Dual Boot

---

## Step-by-Step Instructions for WSL (Windows)

### Step 1: Install WSL

1. Open PowerShell as Administrator
2. Run:
```powershell
wsl --install
```

3. Restart your computer when prompted
4. After restart, Ubuntu will open automatically
5. Create a username and password when prompted

### Step 2: Install Required Dependencies in WSL

Open your Ubuntu terminal and run these commands one by one:

```bash
# Update package list
sudo apt update

# Install Python and pip
sudo apt install -y python3 python3-pip

# Install Java (required for Android builds)
sudo apt install -y openjdk-11-jdk

# Install other build dependencies
sudo apt install -y build-essential git zip unzip

# Install Cython
pip3 install --upgrade cython

# Install Buildozer
pip3 install --upgrade buildozer
```

### Step 3: Copy Your Project to WSL

In WSL Ubuntu terminal:

```bash
# Navigate to your home directory
cd ~

# Create a projects folder
mkdir projects
cd projects

# Copy your project from Windows to WSL
# Replace 'xegui' with your Windows username if different
cp -r /mnt/c/Users/xegui/OneDrive/Documentos/Galapagos-2025 .

# Navigate into the project
cd Galapagos-2025
```

### Step 4: Clean Previous Build (if any)

```bash
buildozer android clean
```

### Step 5: Build the APK

This is the main command - it will take 30-60 minutes the first time:

```bash
buildozer -v android debug
```

The `-v` flag shows verbose output so you can see progress.

**What happens during the build:**
- Downloads Android SDK (~1 GB)
- Downloads Android NDK (~1 GB)
- Downloads Python-for-Android
- Compiles all your Python code and dependencies
- Creates an APK file

**Expected time:** 30-60 minutes for first build, 5-10 minutes for subsequent builds

### Step 6: Find Your APK

After the build completes successfully, your APK will be in:
```bash
bin/gct-0.1-arm64-v8a-debug.apk
```

To copy it to your Windows desktop:
```bash
cp bin/gct-0.1-arm64-v8a-debug.apk /mnt/c/Users/xegui/Desktop/
```

---

## Installing the APK on Your Phone

### Method 1: USB Transfer (Easiest)

1. Connect your phone to computer via USB
2. Copy the APK from Desktop to your phone
3. On your phone, open the APK file
4. Android may warn "Install from unknown sources" - allow it
5. Click Install

### Method 2: Direct Deploy via USB (If you have ADB)

In WSL terminal:

```bash
# This installs directly to your phone
buildozer android deploy run
```

**Requirements for this method:**
- Phone connected via USB
- USB Debugging enabled on phone
- ADB must work in WSL (may need additional setup)

---

## Common Build Errors and Solutions

### Error: "Command failed: python3 -m pip..."
**Solution:**
```bash
pip3 install --upgrade pip
pip3 install --upgrade setuptools wheel
```

### Error: "Could not find a version that satisfies..."
**Solution:** Update buildozer:
```bash
pip3 install --upgrade buildozer
```

### Error: "No space left on device"
**Solution:** You need at least 10 GB free space. Clean up WSL:
```bash
buildozer android clean
rm -rf .buildozer
```

### Error: "SDK License not accepted"
**Solution:** In buildozer.spec, uncomment this line:
```
android.accept_sdk_license = True
```

### Error: Build seems stuck
**Don't panic!** The first build takes a very long time. If it's downloading or compiling, let it continue. Check if it's making progress by looking at the output.

---

## Quick Reference Commands

```bash
# Clean everything and start fresh
buildozer android clean
rm -rf .buildozer

# Build debug APK (for testing)
buildozer android debug

# Build and install on connected phone
buildozer android debug deploy run

# Build release APK (for Google Play Store - needs signing)
buildozer android release

# Show buildozer version
buildozer --version

# Get help
buildozer --help
```

---

## Building a Release Version (for Google Play Store)

If you want to publish to Google Play Store:

1. Create a keystore file:
```bash
keytool -genkey -v -keystore my-release-key.keystore -alias my-key-alias -keyalg RSA -keysize 2048 -validity 10000
```

2. Update buildozer.spec:
```ini
[app]
android.release_artifact = aab

# Add at the end
android.p4a_whitelist = lib-dynload/termios.so
```

3. Build release:
```bash
buildozer android release
```

The signed APK/AAB will be in the `bin/` folder.

---

## Troubleshooting WSL Access

If you can't access your files in WSL from Windows:

1. Open File Explorer
2. In the address bar, type: `\\wsl$\Ubuntu\home\YOUR_USERNAME\projects\Galapagos-2025`
3. You can now drag/drop files between Windows and WSL

---

## Alternative: Use GitHub Actions (Advanced)

If you don't want to set up WSL, you can use GitHub Actions to build automatically in the cloud. This requires:
1. Pushing your code to GitHub
2. Setting up a GitHub Actions workflow file
3. GitHub will build the APK for you

Let me know if you want instructions for this method.

---

## What Now?

1. **Install WSL** if you haven't already
2. **Copy your project** to WSL
3. **Run** `buildozer android debug`
4. **Wait** 30-60 minutes
5. **Copy APK** to your phone
6. **Install and test**

If you encounter any errors during the build, copy the error message and I can help you troubleshoot!
