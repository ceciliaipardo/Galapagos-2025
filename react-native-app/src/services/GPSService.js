import Geolocation from 'react-native-geolocation-service';
import { PermissionsAndroid, Platform } from 'react-native';

let watchId = null;

export const requestLocationPermission = async () => {
  if (Platform.OS === 'android') {
    try {
      const granted = await PermissionsAndroid.requestMultiple([
        PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
        PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION,
        PermissionsAndroid.PERMISSIONS.ACCESS_BACKGROUND_LOCATION,
      ]);

      return (
        granted['android.permission.ACCESS_FINE_LOCATION'] === PermissionsAndroid.RESULTS.GRANTED &&
        granted['android.permission.ACCESS_COARSE_LOCATION'] === PermissionsAndroid.RESULTS.GRANTED
      );
    } catch (err) {
      console.warn(err);
      return false;
    }
  }
  return true;
};

export const startGPSTracking = async (callback, intervalSeconds = 10) => {
  const hasPermission = await requestLocationPermission();
  
  if (!hasPermission) {
    console.error('Location permission denied');
    return false;
  }

  watchId = Geolocation.watchPosition(
    (position) => {
      const { latitude, longitude } = position.coords;
      callback(latitude, longitude);
    },
    (error) => {
      console.error('GPS Error:', error);
    },
    {
      enableHighAccuracy: true,
      distanceFilter: 0,
      interval: intervalSeconds * 1000,
      fastestInterval: intervalSeconds * 1000,
      forceRequestLocation: true,
      showLocationDialog: true,
    }
  );

  return true;
};

export const stopGPSTracking = () => {
  if (watchId !== null) {
    Geolocation.clearWatch(watchId);
    watchId = null;
  }
};

export const getCurrentPosition = async () => {
  const hasPermission = await requestLocationPermission();
  
  if (!hasPermission) {
    throw new Error('Location permission denied');
  }

  return new Promise((resolve, reject) => {
    Geolocation.getCurrentPosition(
      (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
        });
      },
      (error) => {
        reject(error);
      },
      { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
    );
  });
};

// Calculate distance between two coordinates using Haversine formula
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 3958.8; // Radius of Earth in miles
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;
  
  return distance;
};

const toRadians = (degrees) => {
  return degrees * (Math.PI / 180);
};

export const calculateTripDistance = (coordinates, minMph = 2, checkFrequency = 10) => {
  if (coordinates.length < 2) return 0;

  let totalDistance = 0;
  const minDistance = (minMph * checkFrequency) / 3600;

  for (let i = 1; i < coordinates.length; i++) {
    const distance = calculateDistance(
      coordinates[i - 1].lat,
      coordinates[i - 1].lon,
      coordinates[i].lat,
      coordinates[i].lon
    );

    if (distance >= minDistance) {
      totalDistance += distance;
    }
  }

  return totalDistance;
};
