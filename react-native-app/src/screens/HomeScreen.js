import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Alert,
} from 'react-native';
import { useLanguage } from '../contexts/LanguageContext';
import { logoutUser, getCurrentUser } from '../services/DatabaseService';

const HomeScreen = ({ navigation }) => {
  const { getText, toggleLanguage, currentLanguage } = useLanguage();
  const [userName, setUserName] = useState('');

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    const user = await getCurrentUser();
    if (user) {
      setUserName(user.name);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      getText('log_out'),
      'Are you sure you want to log out?',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'OK',
          onPress: async () => {
            await logoutUser();
            navigation.replace('Welcome');
          },
        },
      ]
    );
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.greeting}>
          {getText('home')} {userName}!
        </Text>
        <TouchableOpacity
          style={styles.languageButton}
          onPress={toggleLanguage}
        >
          <Text style={styles.languageButtonText}>
            {currentLanguage === 'en' ? 'ES' : 'EN'}
          </Text>
        </TouchableOpacity>
      </View>

      <View style={styles.content}>
        <TouchableOpacity
          style={[styles.button, styles.startTripButton]}
          onPress={() => navigation.navigate('StartTrip')}
        >
          <Text style={styles.buttonText}>{getText('start_trip')}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.statsButton]}
          onPress={() => navigation.navigate('HomeStats')}
        >
          <Text style={styles.buttonText}>{getText('get_stats')}</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.logoutButton]}
          onPress={handleLogout}
        >
          <Text style={styles.buttonText}>{getText('log_out')}</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFB',
  },
  header: {
    backgroundColor: '#0A7EA4',
    padding: 24,
    paddingTop: 60,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 3 },
    shadowOpacity: 0.15,
    shadowRadius: 6,
    elevation: 6,
  },
  greeting: {
    fontSize: 26,
    fontWeight: '700',
    color: '#fff',
    flex: 1,
    letterSpacing: 0.3,
  },
  languageButton: {
    backgroundColor: 'rgba(255, 255, 255, 0.25)',
    paddingHorizontal: 18,
    paddingVertical: 10,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.3)',
  },
  languageButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  content: {
    flex: 1,
    padding: 24,
    justifyContent: 'center',
  },
  button: {
    padding: 28,
    borderRadius: 16,
    marginBottom: 18,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 6,
    borderWidth: 1,
  },
  startTripButton: {
    backgroundColor: '#10B981',
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  statsButton: {
    backgroundColor: '#3B82F6',
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  logoutButton: {
    backgroundColor: '#EF4444',
    borderColor: 'rgba(255, 255, 255, 0.2)',
  },
  buttonText: {
    color: '#fff',
    fontSize: 20,
    fontWeight: '700',
    textAlign: 'center',
    letterSpacing: 0.5,
  },
});

export default HomeScreen;
