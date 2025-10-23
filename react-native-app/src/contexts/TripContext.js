import React, { createContext, useState, useContext } from 'react';

const TripContext = createContext();

export const useTrip = () => {
  const context = useContext(TripContext);
  if (!context) {
    throw new Error('useTrip must be used within a TripProvider');
  }
  return context;
};

export const TripProvider = ({ children }) => {
  const [currentTripId, setCurrentTripId] = useState('');
  const [company, setCompany] = useState('');
  const [carNumber, setCarNumber] = useState('');
  const [destination, setDestination] = useState('');
  const [passengers, setPassengers] = useState('');
  const [cargo, setCargo] = useState('');
  const [tripStartTime, setTripStartTime] = useState(null);
  const [gpsCoordinates, setGpsCoordinates] = useState([]);

  const startNewTrip = (username) => {
    const now = new Date();
    const tripId = `${username}${now.getFullYear()}${now.getMonth() + 1}${now.getDate()}${now.getHours()}${now.getMinutes()}${now.getSeconds()}`;
    setCurrentTripId(tripId);
    setTripStartTime(now);
    setGpsCoordinates([]);
  };

  const addGpsCoordinate = (lat, lon) => {
    setGpsCoordinates(prev => [...prev, { lat, lon, timestamp: new Date() }]);
  };

  const clearTrip = () => {
    setCurrentTripId('');
    setCompany('');
    setCarNumber('');
    setDestination('');
    setPassengers('');
    setCargo('');
    setTripStartTime(null);
    setGpsCoordinates([]);
  };

  return (
    <TripContext.Provider
      value={{
        currentTripId,
        company,
        carNumber,
        destination,
        passengers,
        cargo,
        tripStartTime,
        gpsCoordinates,
        setCompany,
        setCarNumber,
        setDestination,
        setPassengers,
        setCargo,
        startNewTrip,
        addGpsCoordinate,
        clearTrip,
      }}
    >
      {children}
    </TripContext.Provider>
  );
};
