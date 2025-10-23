import React, { createContext, useState, useContext } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { translations } from '../utils/translations';

const LanguageContext = createContext();

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

export const LanguageProvider = ({ children }) => {
  const [currentLanguage, setCurrentLanguage] = useState('en');

  const toggleLanguage = async () => {
    const newLang = currentLanguage === 'en' ? 'es' : 'en';
    setCurrentLanguage(newLang);
    await AsyncStorage.setItem('appLanguage', newLang);
  };

  const getText = (key) => {
    return translations[currentLanguage][key] || key;
  };

  const getImagePath = (imageName) => {
    return `../assets/images/${currentLanguage}/${imageName}`;
  };

  React.useEffect(() => {
    loadLanguage();
  }, []);

  const loadLanguage = async () => {
    try {
      const savedLang = await AsyncStorage.getItem('appLanguage');
      if (savedLang) {
        setCurrentLanguage(savedLang);
      }
    } catch (error) {
      console.error('Error loading language:', error);
    }
  };

  return (
    <LanguageContext.Provider
      value={{
        currentLanguage,
        toggleLanguage,
        getText,
        getImagePath,
      }}
    >
      {children}
    </LanguageContext.Provider>
  );
};
