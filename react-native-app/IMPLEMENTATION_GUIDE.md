# React Native Implementation Guide

## What's Been Created

### ✅ Complete Core Infrastructure
1. **App.js** - Main app with navigation setup
2. **package.json** - All required dependencies
3. **README.md** - Complete setup and usage documentation

### ✅ Contexts
1. **LanguageContext.js** - Bilingual support (EN/ES)
2. **TripContext.js** - Trip state management

### ✅ Services
1. **DatabaseService.js** - Complete SQLite database layer
2. **GPSService.js** - GPS tracking with Haversine distance calculation

### ✅ Utilities
1. **translations.js** - All English and Spanish translations

### ✅ Example Screens
1. **WelcomeScreen.js** - Login screen (COMPLETE)
2. **HomeScreen.js** - Home dashboard (COMPLETE)
3. **ScreenPlaceholders.js** - Templates for remaining screens

## What Needs to Be Done

### Step 1: Initialize React Native Project

```bash
# In your project root directory
npx react-native init GalapagosCarTracking
```

### Step 2: Copy Files

Copy all files from `react-native-app/` to your new `GalapagosCarTracking/` directory:
- Replace `App.js`
- Replace `package.json`
- Copy all `src/` folders

### Step 3: Install Dependencies

```bash
cd GalapagosCarTracking
npm install
```

### Step 4: Configure Android Permissions

Edit `android/app/src/main/AndroidManifest.xml` and add before `<application>`:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
<uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
```

### Step 5: Link Native Dependencies (Android)

```bash
npx react-native link react-native-geolocation-service
npx react-native link react-native-sqlite-storage
```

### Step 6: Configure iOS (Mac Only)

Edit `ios/GalapagosCarTracking/Info.plist` and add:

```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>We need your location to track trips</string>
<key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
<string>We need your location to track trips in the background</string>
<key>NSLocationAlwaysUsageDescription</key>
<string>We need your location to track trips in the background</string>
```

Then install pods:
```bash
cd ios
pod install
cd ..
```

### Step 7: Create Individual Screen Files

Copy each screen from `ScreenPlaceholders.js` to its own file:

#### Create RegisterScreen1.js:
```javascript
import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { useLanguage } from '../contexts/LanguageContext';
import { checkUsernameExists, checkPhoneExists } from '../services/DatabaseService';

const RegisterScreen1 = ({ navigation }) => {
  const { getText } = useLanguage();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [error, setError] = useState('');

  const handleNext = async () => {
    // Validate inputs
    if (!username || !password || !name || !phone) {
      setError('Please fill in all fields');
      return;
    }

    // Check if username exists
    const usernameExists = await checkUsernameExists(username);
    if (usernameExists) {
      setError(getText('username_exists'));
      return;
    }

    // Check if phone exists
    const phoneExists = await checkPhoneExists(phone);
    if (phoneExists) {
      setError(getText('phone_exists'));
      return;
    }

    // Navigate to next screen with data
    navigation.navigate('Register2', {
      username,
      password,
      name,
      phone,
    });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{getText('fill_out_following')}</Text>
      
      <TextInput
        style={styles.input}
        placeholder={getText('username')}
        value={username}
        onChangeText={setUsername}
        autoCapitalize="none"
      />
      
      <TextInput
        style={styles.input}
        placeholder={getText('password')}
        value={password}
        onChangeText={setPassword}
        secureTextEntry
      />
      
      <TextInput
        style={styles.input}
        placeholder={getText('name')}
        value={name}
        onChangeText={setName}
      />
      
      <TextInput
        style={styles.input}
        placeholder={getText('phone_number')}
        value={phone}
        onChangeText={setPhone}
        keyboardType="phone-pad"
      />

      {error ? <Text style={styles.errorText}>{error}</Text> : null}

      <View style={styles.buttons}>
        <TouchableOpacity 
          style={styles.button}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.buttonText}>{getText('back')}</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.button, styles.nextButton]}
          onPress={handleNext}
        >
          <Text style={styles.buttonText}>{getText('next')}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F5F5F5',
    padding: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 30,
    textAlign: 'center',
  },
  input: {
    backgroundColor: '#fff',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
    fontSize: 16,
  },
  errorText: {
    color: '#E74C3C',
    marginBottom: 15,
    textAlign: 'center',
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginTop: 20,
  },
  button: {
    backgroundColor: '#4A90E2',
    padding: 15,
    borderRadius: 10,
    flex: 0.45,
  },
  nextButton: {
    backgroundColor: '#2ECC71',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default RegisterScreen1;
```

#### Create the remaining screens following similar patterns:
- **RegisterScreen2.js** - Company/car info, calls `registerUser`
- **StartTripScreen.js** - Select car, calls `startNewTrip` from TripContext
- **DestinationScreen.js** - Select destination with image buttons
- **PeopleScreen.js** - Select passenger type
- **CargoScreen.js** - Select cargo type
- **FinishTripScreen.js** - GPS tracking active, calls `startGPSTracking`
- **TripStatsScreen.js** - Display trip statistics
- **HomeStatsScreen.js** - Display daily statistics

### Step 8: Update App.js Imports

Replace the placeholder imports in App.js with actual screen imports:

```javascript
import WelcomeScreen from './src/screens/WelcomeScreen';
import HomeScreen from './src/screens/HomeScreen';
import RegisterScreen1 from './src/screens/RegisterScreen1';
import RegisterScreen2 from './src/screens/RegisterScreen2';
// ... etc for all screens
```

### Step 9: Add Images

Create directories and add images:
```
assets/
  images/
    en/
      airport.png
      highlands.png
      town.png
      tourist.png
      student.png
      luggage.png
      farm.png
      food.png
      other.png
      otherpeople.png
      2tourists.png
      local.png
    es/
      (same files, Spanish versions)
```

You can copy images from your original Kivy app's `images/` folders.

### Step 10: Test on Device/Emulator

#### Android
```bash
npm run android
```

#### iOS
```bash
npm run ios
```

## Implementation Priority

### Phase 1: Core Functionality (Most Important)
1. ✅ WelcomeScreen - DONE
2. ✅ HomeScreen - DONE  
3. RegisterScreen1 - Template provided above
4. RegisterScreen2
5. StartTripScreen

### Phase 2: Trip Flow
6. DestinationScreen
7. PeopleScreen
8. CargoScreen
9. FinishTripScreen (with GPS)

### Phase 3: Statistics
10. TripStatsScreen
11. HomeStatsScreen

## Key Implementation Notes

### GPS Tracking in FinishTripScreen

```javascript
useEffect(() => {
  const { startNewTrip, addGpsCoordinate } = useTrip();
  const user = getCurrentUser();
  
  startNewTrip(user.username);
  
  startGPSTracking((lat, lon) => {
    addGpsCoordinate(lat, lon);
    // Also record to database
    recordTripData({
      tripID: currentTripId,
      company,
      carnum,
      destination,
      passengers,
      cargo,
      gpslon: lon,
      gpslat: lat,
      time: new Date().toISOString(),
    });
  }, 10); // 10 second interval

  return () => {
    stopGPSTracking();
  };
}, []);
```

### Button Images in Destination/People/Cargo Screens

```javascript
<TouchableOpacity 
  onPress={() => setDestination('The Highlands')}
>
  <Image 
    source={require(`../../assets/images/${currentLanguage}/highlands.png`)}
    style={styles.optionImage}
  />
</TouchableOpacity>
```

### Statistics Calculation

Use the database service functions:
```javascript
const stats = await getDayStats(username, '20251002');
// stats will contain: numTrips, totalDist, totalFuel, totalTime
```

## Debugging Tips

### Enable Remote Debugging
1. Shake device or Cmd+M/Cmd+D
2. Select "Debug"
3. Chrome DevTools will open

### View Console Logs
```javascript
console.log('Debug info:', variable);
```

### Common Issues

**SQLite not working:**
```bash
cd android
./gradlew clean
cd ..
npm run android
```

**GPS permissions denied:**
- Check Settings > App > Permissions on device
- Ensure location services enabled

**Metro bundler cache issues:**
```bash
npx react-native start --reset-cache
```

## Building for Production

### Android APK
```bash
cd android
./gradlew assembleRelease
```

Output: `android/app/build/outputs/apk/release/app-release.apk`

### Android AAB (Google Play)
```bash
cd android
./gradlew bundleRelease
```

Output: `android/app/build/outputs/bundle/release/app-release.aab`

## Next Steps

1. **Complete all screen implementations** using the templates provided
2. **Add image assets** to the assets folder
3. **Test thoroughly** on physical devices
4. **Optimize performance** - lazy loading, memoization
5. **Add error handling** - network errors, GPS failures
6. **Add loading indicators** - while database queries run
7. **Polish UI/UX** - animations, transitions, feedback

## Resources

- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [React Navigation](https://reactnavigation.org/docs/getting-started)
- [SQLite Storage](https://github.com/andpor/react-native-sqlite-storage)
- [Geolocation Service](https://github.com/Agontuk/react-native-geolocation-service)

## Support

If you encounter issues:
1. Check the README.md troubleshooting section
2. Review error messages in Metro bundler
3. Check device logs with `adb logcat` (Android)
4. Verify all dependencies are installed correctly

## Advantages Over Kivy

✅ **Direct Windows development** - No WSL needed
✅ **Better performance** - Native components
✅ **Easier deployment** - Standard Android/iOS build process
✅ **Hot reload** - Instant feedback during development
✅ **Larger ecosystem** - More libraries and community support
✅ **Better documentation** - Extensive React Native resources
✅ **Professional tools** - React DevTools, debugger support

Good luck with your React Native implementation!
