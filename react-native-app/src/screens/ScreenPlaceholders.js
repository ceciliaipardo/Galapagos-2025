// This file contains placeholder screens that need to be fully implemented
// Copy each screen to its own file in the src/screens/ directory

import React from 'react';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useLanguage } from '../contexts/LanguageContext';

// Placeholder template - customize for each screen
const ScreenTemplate = ({ navigation, title, nextScreen, prevScreen }) => {
  const { getText } = useLanguage();
  
  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.subtitle}>This screen needs to be implemented</Text>
      
      <View style={styles.buttons}>
        {prevScreen && (
          <TouchableOpacity 
            style={styles.button}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.buttonText}>{getText('back')}</Text>
          </TouchableOpacity>
        )}
        
        {nextScreen && (
          <TouchableOpacity 
            style={[styles.button, styles.nextButton]}
            onPress={() => navigation.navigate(nextScreen)}
          >
            <Text style={styles.buttonText}>{getText('next')}</Text>
          </TouchableOpacity>
        )}
      </View>
    </View>
  );
};

// Register Screen 1
export const RegisterScreen1 = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Register - Page 1"
    nextScreen="Register2"
    prevScreen="Welcome"
  />
);

// Register Screen 2
export const RegisterScreen2 = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Register - Page 2"
    nextScreen="Welcome"
    prevScreen="Register1"
  />
);

// Start Trip Screen
export const StartTripScreen = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Start Trip"
    nextScreen="Destination"
    prevScreen="Home"
  />
);

// Destination Screen
export const DestinationScreen = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Select Destination"
    nextScreen="People"
    prevScreen="StartTrip"
  />
);

// People Screen
export const PeopleScreen = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Select Passengers"
    nextScreen="Cargo"
    prevScreen="Destination"
  />
);

// Cargo Screen
export const CargoScreen = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Select Cargo"
    nextScreen="FinishTrip"
    prevScreen="People"
  />
);

// Finish Trip Screen
export const FinishTripScreen = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Trip in Progress"
    nextScreen="TripStats"
    prevScreen={null}
  />
);

// Trip Stats Screen
export const TripStatsScreen = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Trip Statistics"
    nextScreen="Home"
    prevScreen={null}
  />
);

// Home Stats Screen
export const HomeStatsScreen = ({ navigation }) => (
  <ScreenTemplate 
    navigation={navigation}
    title="Today's Statistics"
    nextScreen={null}
    prevScreen="Home"
  />
);

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFB',
    padding: 24,
    justifyContent: 'center',
    alignItems: 'center',
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    marginBottom: 16,
    color: '#0A7EA4',
    letterSpacing: 0.3,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    marginBottom: 48,
    fontWeight: '500',
  },
  buttons: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    width: '100%',
    paddingHorizontal: 12,
  },
  button: {
    backgroundColor: '#3B82F6',
    padding: 18,
    borderRadius: 14,
    minWidth: 130,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5,
  },
  nextButton: {
    backgroundColor: '#10B981',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
});
