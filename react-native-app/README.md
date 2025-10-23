# Galapagos Car Tracking - React Native App

## Overview
This is a complete React Native rewrite of the Galapagos Car Tracking app. It supports both Android and iOS, includes GPS tracking, SQLite database, and bilingual support (English/Spanish).

## Prerequisites

### Required Software
1. **Node.js** (v16 or higher) - [Download](https://nodejs.org/)
2. **React Native CLI**
3. **For Android:**
   - Android Studio
   - Android SDK
   - Java JDK 11 or higher
4. **For iOS (Mac only):**
   - Xcode 12 or higher
   - CocoaPods

## Installation Steps

### 1. Install Node.js
Download and install from https://nodejs.org/

### 2. Install React Native CLI
```bash
npm install -g react-native-cli
```

### 3. Install Project Dependencies
Navigate to the react-native-app folder and run:
```bash
cd react-native-app
npm install
```

### 4. Android Setup

#### Install Android Studio
1. Download from https://developer.android.com/studio
2. Install Android Studio
3. Open Android Studio > SDK Manager
4. Install:
   - Android SDK Platform 33
   - Android SDK Build-Tools
   - Android Emulator
   - Android SDK Platform-Tools

#### Set Environment Variables
Add to your system environment variables (or ~/.bashrc on Linux/Mac):
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/emulator
export PATH=$PATH:$ANDROID_HOME/tools
export PATH=$PATH:$ANDROID_HOME/tools/bin
export PATH=$PATH:$ANDROID_HOME/platform-tools
```

### 5. iOS Setup (Mac Only)

#### Install Xcode
1. Download from Mac App Store
2. Install Command Line Tools:
```bash
xcode-select --install
```

#### Install CocoaPods
```bash
sudo gem install cocoapods
```

#### Install iOS Dependencies
```bash
cd ios
pod install
cd ..
```

## Running the App

### Android

#### Using Emulator
1. Start Android emulator from Android Studio
2. Run:
```bash
npm run android
```

#### Using Physical Device
1. Enable Developer Options on Android device
2. Enable USB Debugging
3. Connect device via USB
4. Run:
```bash
npm run android
```

### iOS (Mac Only)

#### Using Simulator
```bash
npm run ios
```

#### Using Physical Device
1. Open `ios/GalapagosCarTracking.xcworkspace` in Xcode
2. Select your device
3. Click Run

## Building for Production

### Android APK

```bash
cd android
./gradlew assembleRelease
```

APK location: `android/app/build/outputs/apk/release/app-release.apk`

### Android AAB (for Play Store)

```bash
cd android
./gradlew bundleRelease
```

AAB location: `android/app/build/outputs/bundle/release/app-release.aab`

### iOS (Mac Only)

1. Open Xcode
2. Product > Archive
3. Follow prompts to submit to App Store

## Project Structure

```
react-native-app/
├── src/
│   ├── contexts/          # React contexts (Language, Trip)
│   ├── screens/           # All app screens
│   ├── components/        # Reusable components
│   ├── services/          # Database, GPS services
│   ├── utils/             # Translations, helpers
│   └── styles/            # Shared styles
├── android/               # Android native code
├── ios/                   # iOS native code
├── App.js                 # Main app component
└── package.json           # Dependencies
```

## Features

### Implemented
- ✅ User authentication (login/register)
- ✅ SQLite database for offline storage
- ✅ GPS tracking with background support
- ✅ Trip management (start, track, end trips)
- ✅ Statistics and reporting
- ✅ Bilingual support (English/Spanish)
- ✅ Navigation between screens
- ✅ Context-based state management

### Database Schema

#### accountData Table
- username (TEXT PRIMARY KEY)
- password (TEXT)
- name (TEXT)
- phone (TEXT)
- company1 (TEXT)
- comp1num (TEXT)
- company2 (TEXT)
- comp2num (TEXT)

#### tripData Table
- id (INTEGER PRIMARY KEY)
- tripID (TEXT)
- company (TEXT)
- carnum (TEXT)
- destinationXstatus (TEXT)
- passengersXtotalTime (TEXT)
- cargoXtotalDist (TEXT)
- gpslonXworkingFuel (TEXT)
- gpslat (TEXT)
- time (TEXT)

## Key Services

### DatabaseService
Handles all SQLite operations:
- User registration and login
- Trip data storage and retrieval
- Statistics calculations

### GPSService
Manages GPS tracking:
- Request location permissions
- Start/stop GPS tracking
- Calculate distances using Haversine formula
- Background location support

### LanguageContext
Manages bilingual support:
- Toggle between English and Spanish
- Persistent language selection
- Translation utilities

### TripContext
Manages trip state:
- Current trip information
- GPS coordinates
- Trip start/end times

## Required Permissions

### Android (android/app/src/main/AndroidManifest.xml)
```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

### iOS (ios/GalapagosCarTracking/Info.plist)
```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location to track trips</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>We need your location to track trips in the background</string>
```

## Troubleshooting

### Metro Bundler Issues
```bash
# Clear cache
npx react-native start --reset-cache
```

### Android Build Fails
```bash
cd android
./gradlew clean
cd ..
npm run android
```

### iOS Build Fails
```bash
cd ios
pod deintegrate
pod install
cd ..
npm run ios
```

### SQLite Issues
Make sure react-native-sqlite-storage is properly linked:
```bash
npx react-native link react-native-sqlite-storage
```

### GPS Not Working
1. Check permissions are granted on device
2. Ensure location services are enabled
3. Test outdoors for better GPS signal

## Development Tips

### Hot Reload
Press `r` in Metro bundler terminal to reload
Press `d` to open developer menu

### Debugging
1. Shake device or press Cmd+D (iOS) / Cmd+M (Android)
2. Select "Debug"
3. Open Chrome DevTools at `chrome://inspect`

### VS Code Extensions (Recommended)
- React Native Tools
- ES7+ React/Redux/React-Native snippets
- Prettier - Code formatter
- ESLint

## Creating New Screens

Example screen template:
```javascript
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { useLanguage } from '../contexts/LanguageContext';

const NewScreen = ({ navigation }) => {
  const { getText } = useLanguage();

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{getText('screen_title')}</Text>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
  },
});

export default NewScreen;
```

## Performance Optimization

### Images
- Use appropriate image sizes
- Consider using react-native-fast-image for better performance
- Store language-specific images in assets/images/en and assets/images/es

### Database
- Use transactions for multiple operations
- Index frequently queried columns
- Close database connections when not needed

### GPS
- Adjust tracking frequency based on needs (default: 10 seconds)
- Stop GPS tracking when not recording trips
- Filter out insignificant movements

## Support & Contact

For issues or questions about the app functionality, refer to the original Kivy app documentation or contact the development team.

## License

[Add your license here]

## Version History

### v0.1.0 (Current)
- Initial React Native implementation
- Core features: Authentication, GPS tracking, Trip management
- Bilingual support (EN/ES)
- SQLite database integration
