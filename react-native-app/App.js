import React, { useEffect, useState } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import screens
import WelcomeScreen from './src/screens/WelcomeScreen';
import HomeScreen from './src/screens/HomeScreen';
import RegisterScreen1 from './src/screens/RegisterScreen1';
import RegisterScreen2 from './src/screens/RegisterScreen2';
import StartTripScreen from './src/screens/StartTripScreen';
import DestinationScreen from './src/screens/DestinationScreen';
import PeopleScreen from './src/screens/PeopleScreen';
import CargoScreen from './src/screens/CargoScreen';
import FinishTripScreen from './src/screens/FinishTripScreen';
import TripStatsScreen from './src/screens/TripStatsScreen';
import HomeStatsScreen from './src/screens/HomeStatsScreen';

// Import services
import { initDatabase } from './src/services/DatabaseService';
import { LanguageProvider } from './src/contexts/LanguageContext';
import { TripProvider } from './src/contexts/TripContext';

const Stack = createNativeStackNavigator();

function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [initialRoute, setInitialRoute] = useState('Welcome');

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize database
      await initDatabase();

      // Check if user is already logged in
      const userData = await AsyncStorage.getItem('currentUser');
      if (userData) {
        setInitialRoute('Home');
      }
    } catch (error) {
      console.error('Error initializing app:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return null; // Or a loading screen
  }

  return (
    <LanguageProvider>
      <TripProvider>
        <NavigationContainer>
          <Stack.Navigator
            initialRouteName={initialRoute}
            screenOptions={{
              headerShown: false,
              animation: 'slide_from_right',
            }}
          >
            <Stack.Screen name="Welcome" component={WelcomeScreen} />
            <Stack.Screen name="Home" component={HomeScreen} />
            <Stack.Screen name="Register1" component={RegisterScreen1} />
            <Stack.Screen name="Register2" component={RegisterScreen2} />
            <Stack.Screen name="StartTrip" component={StartTripScreen} />
            <Stack.Screen name="Destination" component={DestinationScreen} />
            <Stack.Screen name="People" component={PeopleScreen} />
            <Stack.Screen name="Cargo" component={CargoScreen} />
            <Stack.Screen name="FinishTrip" component={FinishTripScreen} />
            <Stack.Screen name="TripStats" component={TripStatsScreen} />
            <Stack.Screen name="HomeStats" component={HomeStatsScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </TripProvider>
    </LanguageProvider>
  );
}

export default App;
