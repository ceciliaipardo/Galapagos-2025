import SQLite from 'react-native-sqlite-storage';
import AsyncStorage from '@react-native-async-storage/async-storage';

SQLite.DEBUG(false);
SQLite.enablePromise(true);

let db = null;

export const initDatabase = async () => {
  try {
    db = await SQLite.openDatabase({
      name: 'galapagos.db',
      location: 'default',
    });

    await createTables();
    console.log('Database initialized successfully');
  } catch (error) {
    console.error('Error initializing database:', error);
    throw error;
  }
};

const createTables = async () => {
  await db.executeSql(`
    CREATE TABLE IF NOT EXISTS accountData (
      username TEXT PRIMARY KEY,
      password TEXT,
      name TEXT,
      phone TEXT,
      company1 TEXT,
      comp1num TEXT,
      company2 TEXT,
      comp2num TEXT
    )
  `);

  await db.executeSql(`
    CREATE TABLE IF NOT EXISTS tripData (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tripID TEXT,
      company TEXT,
      carnum TEXT,
      destinationXstatus TEXT,
      passengersXtotalTime TEXT,
      cargoXtotalDist TEXT,
      gpslonXworkingFuel TEXT,
      gpslat TEXT,
      time TEXT
    )
  `);
};

// User Management
export const registerUser = async (userData) => {
  const { username, password, name, phone, company1, comp1num, company2, comp2num } = userData;
  
  try {
    await db.executeSql(
      `INSERT INTO accountData (username, password, name, phone, company1, comp1num, company2, comp2num)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [username, password, name, phone, company1, comp1num, company2, comp2num]
    );
    return { success: true };
  } catch (error) {
    console.error('Error registering user:', error);
    return { success: false, error: error.message };
  }
};

export const loginUser = async (username, password) => {
  try {
    const [results] = await db.executeSql(
      'SELECT * FROM accountData WHERE username = ? AND password = ?',
      [username, password]
    );

    if (results.rows.length > 0) {
      const user = results.rows.item(0);
      await AsyncStorage.setItem('currentUser', JSON.stringify(user));
      return { success: true, user };
    }
    return { success: false, message: 'Invalid credentials' };
  } catch (error) {
    console.error('Error logging in:', error);
    return { success: false, error: error.message };
  }
};

export const checkUsernameExists = async (username) => {
  try {
    const [results] = await db.executeSql(
      'SELECT username FROM accountData WHERE username = ?',
      [username]
    );
    return results.rows.length > 0;
  } catch (error) {
    console.error('Error checking username:', error);
    return false;
  }
};

export const checkPhoneExists = async (phone) => {
  try {
    const [results] = await db.executeSql(
      'SELECT phone FROM accountData WHERE phone = ?',
      [phone]
    );
    return results.rows.length > 0;
  } catch (error) {
    console.error('Error checking phone:', error);
    return false;
  }
};

export const getCurrentUser = async () => {
  try {
    const userData = await AsyncStorage.getItem('currentUser');
    return userData ? JSON.parse(userData) : null;
  } catch (error) {
    console.error('Error getting current user:', error);
    return null;
  }
};

export const logoutUser = async () => {
  try {
    await AsyncStorage.removeItem('currentUser');
    return { success: true };
  } catch (error) {
    console.error('Error logging out:', error);
    return { success: false, error: error.message };
  }
};

// Trip Management
export const recordTripData = async (tripData) => {
  const { tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time } = tripData;
  
  try {
    await db.executeSql(
      `INSERT INTO tripData (tripID, company, carnum, destinationXstatus, passengersXtotalTime, 
       cargoXtotalDist, gpslonXworkingFuel, gpslat, time)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time]
    );
    return { success: true };
  } catch (error) {
    console.error('Error recording trip data:', error);
    return { success: false, error: error.message };
  }
};

export const getTripCoordinates = async (tripID) => {
  try {
    const [results] = await db.executeSql(
      `SELECT gpslonXworkingFuel, gpslat FROM tripData 
       WHERE tripID = ? AND destinationXstatus != 'Start Trip' AND destinationXstatus != 'End Trip'`,
      [tripID]
    );

    const coords = [];
    for (let i = 0; i < results.rows.length; i++) {
      coords.push(results.rows.item(i));
    }
    return coords;
  } catch (error) {
    console.error('Error getting trip coordinates:', error);
    return [];
  }
};

export const getTripStats = async (tripID) => {
  try {
    // Get trip data
    const [tripResults] = await db.executeSql(
      `SELECT passengersXtotalTime, cargoXtotalDist, destinationXstatus 
       FROM tripData WHERE tripID = ? AND destinationXstatus != 'Start Trip' AND destinationXstatus != 'End Trip'
       LIMIT 1`,
      [tripID]
    );

    // Get end trip data
    const [endResults] = await db.executeSql(
      `SELECT passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel 
       FROM tripData WHERE tripID = ? AND destinationXstatus = 'End Trip'`,
      [tripID]
    );

    if (endResults.rows.length > 0 && tripResults.rows.length > 0) {
      const endData = endResults.rows.item(0);
      const tripData = tripResults.rows.item(0);

      return {
        destination: tripData.destinationXstatus,
        passengers: `${tripData.passengersXtotalTime} with ${tripData.cargoXtotalDist}`,
        totalDistance: endData.cargoXtotalDist,
        totalTime: endData.passengersXtotalTime,
        totalFuel: endData.gpslonXworkingFuel,
      };
    }

    return null;
  } catch (error) {
    console.error('Error getting trip stats:', error);
    return null;
  }
};

export const getDayStats = async (username, date) => {
  try {
    const dayID = `${username}${date}%`;
    const [results] = await db.executeSql(
      `SELECT passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, time 
       FROM tripData WHERE destinationXstatus = 'End Trip' AND tripID LIKE ?`,
      [dayID]
    );

    let numTrips = 0;
    let totalDist = 0;
    let totalFuel = 0;
    let totalTime = 0;

    for (let i = 0; i < results.rows.length; i++) {
      const row = results.rows.item(i);
      numTrips++;
      totalDist += parseFloat(row.cargoXtotalDist || 0);
      totalFuel += parseFloat(row.gpslonXworkingFuel || 0);
      // Parse time if needed
    }

    return {
      numTrips,
      totalDist: totalDist.toFixed(2),
      totalFuel: totalFuel.toFixed(2),
      totalTime,
    };
  } catch (error) {
    console.error('Error getting day stats:', error);
    return null;
  }
};

export const clearTripData = async () => {
  try {
    await db.executeSql('DELETE FROM tripData');
    return { success: true };
  } catch (error) {
    console.error('Error clearing trip data:', error);
    return { success: false, error: error.message };
  }
};
