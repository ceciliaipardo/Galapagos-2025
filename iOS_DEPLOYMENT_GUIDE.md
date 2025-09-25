# iOS Deployment Guide for Galapagos Car Tracking App

This guide will help you package and deploy your Kivy-based Galapagos Car Tracking app to iOS devices.

## Prerequisites

### Required Software
1. **macOS** - iOS development requires a Mac
2. **Xcode** - Download from the Mac App Store (latest version recommended)
3. **Python 3.8+** - Should already be installed
4. **Git** - For cloning repositories
5. **Apple Developer Account** - Required for device testing and App Store distribution

### Verify Prerequisites
```bash
# Check Xcode installation
xcode-select --print-path

# Check Python version
python3 --version

# Check Git
git --version
```

## Step 1: Prepare Your Environment

### Install Required Python Packages
```bash
# Make sure you're in your project directory
cd Galapagos-2025/

# Install required packages
pip3 install cython
pip3 install kivy-ios
```

## Step 2: Run the Automated Build Script

We've created an automated build script that handles most of the iOS packaging process:

```bash
# Make the script executable (already done)
chmod +x ios_build.py

# Run the build script
python3 ios_build.py
```

The script will:
- Check prerequisites
- Clone and set up kivy-ios
- Build required packages for iOS
- Create an Xcode project
- Copy your app files

## Step 3: Manual iOS Setup (Alternative Method)

If you prefer to do it manually or the script encounters issues:

### Clone kivy-ios
```bash
git clone https://github.com/kivy/kivy-ios.git
cd kivy-ios
```

### Install kivy-ios Requirements
```bash
pip3 install -r requirements.txt
```

### Build Required Packages
```bash
# Build core packages (this may take 30-60 minutes)
./toolchain.py build python3
./toolchain.py build kivy
./toolchain.py build kivymd
./toolchain.py build sqlite3
./toolchain.py build plyer

# Note: If any package fails, try building it individually
```

### Create Xcode Project
```bash
# Create the iOS project
./toolchain.py create GCT ../
```

## Step 4: Configure the Xcode Project

### Open the Project
1. Navigate to `kivy-ios/GCT-ios/`
2. Open `GCT.xcodeproj` in Xcode

### Copy App Files
Copy these files to your Xcode project directory (`kivy-ios/GCT-ios/`):
- `main_ios.py` (rename to `main.py`)
- `GalapagosCarTracking.kv`
- All image assets (*.png, *.jpg files)

### Configure Info.plist
Add the following permissions to your `Info.plist` file:

```xml
<!-- Location permissions -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access to track car routes.</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>This app needs location access to track car routes.</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>This app needs location access to track car routes.</string>

<!-- Network permissions -->
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
</dict>

<!-- App metadata -->
<key>CFBundleDisplayName</key>
<string>Galapagos Car Tracking</string>
<key>CFBundleVersion</key>
<string>1.0</string>
<key>CFBundleShortVersionString</key>
<string>1.0</string>
```

## Step 5: Configure Code Signing

### Set Up Your Apple Developer Account
1. In Xcode, go to **Preferences > Accounts**
2. Add your Apple ID
3. Download certificates and provisioning profiles

### Configure Project Settings
1. Select your project in Xcode
2. Go to **Signing & Capabilities**
3. Select your development team
4. Choose automatic signing (recommended for development)
5. Set a unique Bundle Identifier (e.g., `com.yourname.galapagoscartracking`)

## Step 6: Build and Test

### Build for Simulator
1. Select an iOS Simulator from the device menu
2. Click the **Build and Run** button (▶️)

### Build for Device
1. Connect your iPhone via USB
2. Trust the computer on your iPhone if prompted
3. Select your device from the device menu
4. Click **Build and Run**

## Important Notes and Limitations

### Database Connectivity
- **MySQL is NOT available on iOS**
- The iOS version (`main_ios.py`) uses local SQLite storage by default
- For remote database access, you'll need to:
  - Set up a REST API server
  - Update `API_BASE_URL` in `main_ios.py`
  - Set `USE_LOCAL_ONLY = False`

### GPS and Location Services
- GPS functionality requires testing on a real device
- Simulator location can be simulated in Xcode
- Make sure location permissions are properly configured

### App Store Distribution
For App Store submission, you'll need:
1. App Store Connect account
2. App icons in required sizes
3. Screenshots for different device sizes
4. App description and metadata
5. Privacy policy (required for location-based apps)

## Troubleshooting

### Common Build Issues

**"No module named 'mysql'"**
- This is expected on iOS - the app uses local SQLite storage

**GPS not working**
- Test on a real device, not simulator
- Check location permissions in device settings

**Build fails during package compilation**
- Try building packages individually
- Check Xcode version compatibility
- Ensure sufficient disk space (5GB+ recommended)

**Code signing errors**
- Verify Apple Developer account setup
- Check Bundle Identifier uniqueness
- Try manual provisioning profile setup

### Performance Tips
- Test on older devices to ensure good performance
- Monitor memory usage during GPS tracking
- Consider reducing GPS update frequency for battery life

## File Structure After Setup

```
Galapagos/Barnwell-Code/
├── ios_requirements.txt          # iOS-specific requirements
├── ios_build.py                  # Automated build script
├── main_ios.py                   # iOS-adapted main file
├── main.py                       # Original Android version
├── GalapagosCarTracking.kv       # UI layout file
├── buildozer.spec               # Android build config
├── kivy-ios/                    # iOS build tools
│   └── GCT-ios/                 # Your Xcode project
│       ├── GCT.xcodeproj        # Xcode project file
│       ├── main.py              # App entry point
│       ├── GalapagosCarTracking.kv
│       └── assets/              # Image files
└── iOS_DEPLOYMENT_GUIDE.md     # This guide
```

## Next Steps

1. **Test thoroughly** on multiple iOS devices
2. **Implement API server** for remote database functionality
3. **Add app icons** and splash screens
4. **Prepare for App Store** submission if desired
5. **Set up TestFlight** for beta testing

## Support

If you encounter issues:
1. Check the [kivy-ios documentation](https://github.com/kivy/kivy-ios)
2. Review [Kivy iOS deployment guide](https://kivy.org/doc/stable/guide/packaging-ios.html)
3. Search [Kivy community forums](https://github.com/kivy/kivy/discussions)

Remember: iOS development can be complex, and the first build may take significant time. Be patient and follow each step carefully.
