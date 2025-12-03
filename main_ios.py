import sqlite3
from supabase_config import get_supabase_client, test_connection

# Get Supabase HTTP client (works on iOS!)
supabase = get_supabase_client()

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import SlideTransition
from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.properties import StringProperty
from datetime import datetime
from datetime import timedelta
from plyer import gps
from math import radians, sin, cos, sqrt, atan2
from translations import translator
import json
import os

currentUser = ''
currentCompany = ''
currentCar = ''
currentDest = ''
currentPass = ''
currentCargo = ''
currentlat = 0
currentlon = 0
currentTripID = ''
mpg = 25 # the average miles per gallon of taxi cars (NOTE: value in MPG, but distance tracked in KM)
checkFrequency = 10 # seconds - GPS sampling interval
minKph = 3.2 # minimum km/h to count as movement (filters out GPS drift when stationary)



def DBConnect():
    """Connect to Supabase via HTTP"""
    if supabase is None:
        raise Exception("Supabase not available")
    return supabase

def DBCreate():
    """Tables should be created in Supabase Dashboard using supabase_schema.sql"""
    Logger.info("Supabase: Tables should be created in Supabase Dashboard")
    pass

def DBClearUsers():
    """Clear all users from Supabase"""
    try:
        client = DBConnect()
        response = client.table('UserData').delete().eq('username', 'dummy')  # Won't delete anything with dummy condition
        Logger.info("Supabase: Cleared UserData table")
    except Exception as e:
        Logger.error(f"Supabase: Error clearing users - {e}")

def DBClearTracking():
    """Clear all tracking data from Supabase"""
    try:
        client = DBConnect()
        response = client.table('TrackingData').delete().eq('tripID', 'dummy')  # Won't delete anything with dummy condition
        Logger.info("Supabase: Cleared TrackingData table")
    except Exception as e:
        Logger.error(f"Supabase: Error clearing tracking - {e}")

def DBDelete():
    """Delete tables - Use Supabase dashboard to delete tables"""
    Logger.warning("Supabase: Use Supabase dashboard to delete tables")
    pass

def DBShowAll():
    """Show all data from Supabase"""
    try:
        client = DBConnect()
        users_response = client.table('UserData').select("*").execute()
        print("\nUser Data from Supabase")
        for row in users_response.data:
            print(row)
        tracking_response = client.table('TrackingData').select("*").execute()
        print("\nTracking Data from Supabase")
        for row in tracking_response.data:
            print(row)
        print("\n")
    except Exception as e:
        Logger.error(f"Supabase: Error showing all data - {e}")
 
def DBCheckUsernameExists(username):
    """Check if username exists in Supabase"""
    if username == '':
        return translator.get_text('username_invalid')
    try:
        client = DBConnect()
        response = client.table('UserData').select("username").eq('username', username).execute()
        if response.data and len(response.data) > 0:
            return translator.get_text('username_exists')
        else:
            return "Valid"
    except Exception as e:
        Logger.error(f"Supabase: Error checking username - {e}")
        return "Error checking username"

def DBCheckPhoneExists(phone):
    """Check if phone exists in Supabase"""
    try:
        int(phone)
    except: 
        return translator.get_text('phone_invalid')
    try:
        client = DBConnect()
        response = client.table('UserData').select("phone").eq('phone', phone).execute()
        if response.data and len(response.data) > 0:
            return translator.get_text('phone_exists')
        else:
            return "Valid"
    except Exception as e:
        Logger.error(f"Supabase: Error checking phone - {e}")
        return "Error checking phone"
    
def DBRegister(username, password, name, phone, company1, comp1num, company2, comp2num):
    """Register a new user in Supabase"""
    try:
        client = DBConnect()
        data = {
            'username': username,
            'password': password,
            'name': name,
            'phone': phone,
            'company1': company1,
            'comp1num': comp1num,
            'company2': company2,
            'comp2num': comp2num
        }
        response = client.table('UserData').insert(data)
        Logger.info(f"Supabase: User {username} registered successfully")
    except Exception as e:
        Logger.error(f"Supabase: Error registering user - {e}")

def DBLogin(username, password):
    """Login user via Supabase"""
    try:
        client = DBConnect()
        response = client.table('UserData').select("*").eq('username', username).eq('password', password).execute()
        if response.data and len(response.data) > 0:
            account = response.data[0]
            # Store account data locally
            localDBStoreAccount(account)
            # Set current user
            global currentUser
            currentUser = username
            return True
        else:
            return False
    except Exception as e:
        Logger.error(f"Supabase: Error during login - {e}")
        return False

def DBPullUserData():
    """Pull user data from Supabase"""
    try:
        client = DBConnect()
        response = client.table('UserData').select("*").eq('username', currentUser).execute()
        if response.data and len(response.data) > 0:
            data = response.data[0]
            return (
                data['username'],
                data['password'],
                data['name'],
                data['phone'],
                data['company1'],
                data['comp1num'],
                data['company2'],
                data['comp2num']
            )
        return None
    except Exception as e:
        Logger.error(f"Supabase: Error pulling user data - {e}")
        return None

def DBUploadTripSummary(tripID, username, company, carnum, destination, passenger_type, passenger_count, cargo_type, distance_km, duration_seconds, fuel_gallons, start_time, end_time):
    """Upload a completed trip summary to Supabase (streamlined version)"""
    try:
        client = DBConnect()
        data = {
            'trip_id': tripID,
            'username': username,
            'company': company,
            'car_number': carnum,
            'destination': destination,
            'passenger_type': passenger_type,
            'passenger_count': passenger_count,
            'cargo_type': cargo_type,
            'distance_km': distance_km,
            'duration_seconds': duration_seconds,
            'fuel_gallons': fuel_gallons,
            'start_time': start_time.replace(microsecond=0).isoformat(),
            'end_time': end_time.replace(microsecond=0).isoformat()
        }
        # Insert the trip summary
        response = client.table('TripData').insert(data).execute()
        Logger.info(f"Supabase: Uploaded trip summary for {tripID}")
    except Exception as e:
        Logger.error(f"Supabase: Error uploading trip summary - {e}")

def DBCheckConnection():
    """Check Supabase connection"""
    try:
        return test_connection()
    except:
        return False

def DBGetDayStats(username, date):
    """Get daily statistics from Supabase (streamlined version)"""
    try:
        # Parse the date string (format: YYYYMMDD)
        year = int(date[:4])
        month = int(date[4:6])
        day = int(date[6:8])
        
        # Create datetime objects for start and end of day in UTC
        from datetime import datetime
        start_date = datetime(year, month, day)
        end_date = start_date + timedelta(days=1)
        
        # Format as ISO strings with Z timezone
        start_str = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_str = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        client = DBConnect()
        # Query trips for the specific user and date range
        response = client.table('TripData').select(
            "distance_km, duration_seconds, fuel_gallons, start_time, end_time"
        ).eq('username', username).gte('start_time', start_str).lt('start_time', end_str).execute()
        
        trips = response.data
        numTrips = len(trips)
        totalDist = 0
        totalTime = timedelta()
        totalFuel = 0
        dayStart = None
        dayEnd = None
        
        for row in trips:
            totalDist += float(row['distance_km']) if row['distance_km'] else 0
            totalTime += timedelta(seconds=int(row['duration_seconds'])) if row['duration_seconds'] else timedelta()
            totalFuel += float(row['fuel_gallons']) if row['fuel_gallons'] else 0
            
            # Track earliest start and latest end
            start = datetime.fromisoformat(row['start_time'].replace('Z', '+00:00')) if row['start_time'] else None
            end = datetime.fromisoformat(row['end_time'].replace('Z', '+00:00')) if row['end_time'] else None
            
            if start:
                if not dayStart or start < dayStart:
                    dayStart = start
            if end:
                if not dayEnd or end > dayEnd:
                    dayEnd = end
        
        # Calculate idle time (time between trips)
        if dayStart and dayEnd and numTrips > 0:
            totalWorkingTime = dayEnd - dayStart
            idleTime = totalWorkingTime - totalTime
            if idleTime.total_seconds() < 0:
                idleTime = timedelta()
        else:
            idleTime = timedelta()
        
        return [numTrips, totalDist, totalFuel, totalTime, idleTime]
    except Exception as e:
        Logger.error(f"Supabase: Error getting day stats - {e}")
        return [0, 0, 0, timedelta(), timedelta()]

def localDBConnect():
    """Connect to local SQLite database"""
    # For iOS, use the app's Documents directory
    if platform == 'ios':
        from plyer import storagepath
        try:
            docs_path = storagepath.get_documents_dir()
        except:
            # Fallback to home Documents if storagepath fails
            docs_path = os.path.join(os.path.expanduser('~'), 'Documents')
    else:
        docs_path = os.path.join(os.path.expanduser('~'), 'Documents')
    
    db_path = os.path.join(docs_path, 'local_db.db')
    Logger.info(f"Database path: {db_path}")
    
    try:
        localdb = sqlite3.connect(db_path)
        cursor = localdb.cursor()
        Logger.info("Database connection successful")
        return [cursor, localdb]
    except Exception as e:
        Logger.error(f"Database connection error: {e}")
        raise

def localDBCreate():
    """Create local database tables"""
    [cursor, localdb] = localDBConnect()
    cursor.execute("""CREATE TABLE if not exists accountData(
	username VARCHAR(20),
    password VARCHAR(20),
    name VARCHAR(20),
    phone VARCHAR(15),
    company1 VARCHAR(20),
    comp1num VARCHAR(5),
    company2 VARCHAR(20),
    comp2num VARCHAR(5)
   	)""")
    cursor.execute("""CREATE TABLE if not exists tripData(
	tripID VARCHAR(40),
    company VARCHAR(20),
    carnum VARCHAR(5),
    destinationXstatus VARCHAR(20),
    passengersXtotalTime VARCHAR(20),
    cargoXtotalDist VARCHAR(20),
   	gpslonXworkingFuel VARCHAR(20),
    gpslat VARCHAR(20),
    time VARCHAR(30)
   	)""")
    cursor.execute("""CREATE TABLE if not exists dailyStats(
	date VARCHAR(8),
    username VARCHAR(20),
    numTrips INTEGER,
    totalDist REAL,
    totalFuel REAL,
    totalTime REAL,
    idleTime REAL
   	)""")
    localdb.commit()
    localdb.close()

def localDBRegister(username, password, name, phone, company1, comp1num, company2, comp2num):
    """Register user in local database"""
    [cursor, localdb] = localDBConnect()
    query = "INSERT INTO accountData (username, password, name, phone, company1, comp1num, company2, comp2num) values (?,?,?,?,?,?,?,?)"
    cursor.execute(query, (username, password, name, phone, company1, comp1num, company2, comp2num))
    localdb.commit()
    localdb.close()

def localDBLogin(username, password):
    """Login using local database"""
    [cursor, localdb] = localDBConnect()
    query = "SELECT * FROM accountData WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    test = cursor.fetchone()
    localdb.close()
    
    if test:
        global currentUser
        currentUser = username
        return True
    return False

def localDBStoreAccount(account_data):
    """Store account data locally after API login"""
    [cursor, localdb] = localDBConnect()
    localDBLogOut()  # Clear existing data
    query = "INSERT INTO accountData (username, password, name, phone, company1, comp1num, company2, comp2num) values (?,?,?,?,?,?,?,?)"
    cursor.execute(query, (
        account_data['username'], account_data['password'], account_data['name'], 
        account_data['phone'], account_data['company1'], account_data['comp1num'],
        account_data['company2'], account_data['comp2num']
    ))
    localdb.commit()
    localdb.close()

def localDBDelete():
    """Delete local database tables"""
    [cursor, localdb] = localDBConnect()
    cursor.execute("DROP TABLE IF EXISTS tripData")
    cursor.execute("DROP TABLE IF EXISTS accountData")
    localdb.commit()
    localdb.close()

def localDBShowAll():
    """Show all local database data"""
    [cursor, localdb] = localDBConnect()
    cursor.execute("SELECT * FROM accountData")
    records = cursor.fetchall()
    print("\nAccount Data Database")
    for row in records:
        print(row)
    cursor.execute("SELECT * FROM tripData")
    records = cursor.fetchall()
    print("\nTrip Data Database")
    for row in records:
        print(row)
    localdb.commit()
    localdb.close()
 
def localDBPullAccountData():
    """Pull account data from local database"""
    [cursor, localdb] = localDBConnect()
    query = "SELECT * FROM accountData"
    cursor.execute(query)
    records = cursor.fetchone()
    localdb.commit()
    localdb.close()
    return records
         
def localDBLogOut():
    """Clear local account data"""
    [cursor, localdb] = localDBConnect()
    query = "DELETE FROM accountData"
    cursor.execute(query)
    localdb.commit()
    localdb.close()

def localDBClearTrip():
    """Clear local trip data"""
    [cursor, localdb] = localDBConnect()
    query = "DELETE FROM tripData"
    cursor.execute(query)
    localdb.commit()
    localdb.close()

def localDBRecord(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    """Record trip data locally"""
    [cursor, localdb] = localDBConnect()
    query = "INSERT INTO tripData (tripID, company, carnum, destinationXstatus, passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, gpslat, time) values (?,?,?,?,?,?,?,?,?)"
    cursor.execute(query, (tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, str(time)))
    localdb.commit()
    localdb.close()

def localDBSaveDailyStats(username, date, numTrips, totalDist, totalFuel, totalTime, idleTime):
    """Save daily statistics to local database"""
    try:
        [cursor, localdb] = localDBConnect()
        
        # Check if stats already exist for this day
        query = "SELECT numTrips, totalDist, totalFuel, totalTime, idleTime FROM dailyStats WHERE username = ? AND date = ?"
        cursor.execute(query, (username, date))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing record by adding to it
            new_numTrips = int(existing[0]) + numTrips
            new_totalDist = float(existing[1]) + totalDist
            new_totalFuel = float(existing[2]) + totalFuel
            new_totalTime = float(existing[3]) + totalTime.total_seconds()
            new_idleTime = float(existing[4]) + idleTime.total_seconds()
            
            query = "UPDATE dailyStats SET numTrips = ?, totalDist = ?, totalFuel = ?, totalTime = ?, idleTime = ? WHERE username = ? AND date = ?"
            cursor.execute(query, (new_numTrips, new_totalDist, new_totalFuel, new_totalTime, new_idleTime, username, date))
            Logger.info(f"Updated daily stats for {date}: {new_numTrips} trips, {new_totalDist:.2f} km")
        else:
            # Insert new record
            query = "INSERT INTO dailyStats (date, username, numTrips, totalDist, totalFuel, totalTime, idleTime) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(query, (date, username, numTrips, totalDist, totalFuel, totalTime.total_seconds(), idleTime.total_seconds()))
            Logger.info(f"Saved daily stats for {date}: {numTrips} trips, {totalDist:.2f} km")
        
        localdb.commit()
        localdb.close()
    except Exception as e:
        Logger.error(f"Error saving daily stats: {e}")

def localDBDumptoServer():
    """Upload completed trip summaries to Supabase (streamlined version)"""
    successfully_uploaded = []
    
    try:
        [cursor, localdb] = localDBConnect()
        
        # Get all unique completed trip IDs
        cursor.execute("SELECT DISTINCT tripID FROM tripData WHERE destinationXstatus = 'End Trip'")
        completed_trips = cursor.fetchall()
        
        Logger.info(f"Found {len(completed_trips)} completed trips to upload")
        
        # Group trips by date for daily stats calculation
        trips_by_date = {}
        
        for trip_row in completed_trips:
            upload_success = False
            try:
                tripID = trip_row[0]
                Logger.info(f"Processing trip: {tripID}")
                
                # Get start time
                cursor.execute("SELECT time FROM tripData WHERE tripID = ? AND destinationXstatus = 'Start Trip'", (tripID,))
                start_row = cursor.fetchone()
                if not start_row:
                    Logger.warning(f"No start time found for trip {tripID}")
                    continue
                
                try:
                    start_time = datetime.strptime(str(start_row[0]), '%Y-%m-%d %H:%M:%S.%f')
                except:
                    Logger.error(f"Could not parse start time: {start_row[0]}")
                    continue
                
                # Get trip details (destination, passengers, cargo)
                cursor.execute("SELECT destinationXstatus, passengersXtotalTime, cargoXtotalDist FROM tripData WHERE tripID = ? AND destinationXstatus != 'Start Trip' AND destinationXstatus != 'End Trip' LIMIT 1", (tripID,))
                detail_row = cursor.fetchone()
                if detail_row:
                    destination = str(detail_row[0])
                    passengers_full = str(detail_row[1])  # e.g., "Students - 2 passengers"
                    cargo = str(detail_row[2])
                    
                    # Parse passenger info
                    if ' - ' in passengers_full:
                        parts = passengers_full.split(' - ')
                        passenger_type = parts[0]
                        passenger_count = parts[1] if len(parts) > 1 else ''
                    else:
                        passenger_type = passengers_full
                        passenger_count = ''
                else:
                    Logger.warning(f"No trip details found for {tripID}")
                    destination = "Unknown"
                    passenger_type = "Unknown"
                    passenger_count = ''
                    cargo = "Unknown"
                
                # Get end data (distance, duration, fuel, company, car)
                cursor.execute("SELECT passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, company, carnum, time FROM tripData WHERE tripID = ? AND destinationXstatus = 'End Trip'", (tripID,))
                end_row = cursor.fetchone()
                if not end_row:
                    Logger.warning(f"No end data found for trip {tripID}")
                    continue
                
                # Parse duration (stored as string timedelta like "0:20:15.123456")
                try:
                    duration_str = str(end_row[0])
                    # Handle both "H:MM:SS.ffffff" and "HH:MM:SS.ffffff" formats
                    time_parts = duration_str.split(':')
                    hours = int(time_parts[0])
                    minutes = int(time_parts[1])
                    seconds_parts = time_parts[2].split('.')
                    seconds = int(seconds_parts[0])
                    duration_seconds = hours * 3600 + minutes * 60 + seconds
                except Exception as e:
                    Logger.error(f"Could not parse duration '{end_row[0]}': {e}")
                    duration_seconds = 0
                
                distance_km = float(end_row[1]) if end_row[1] else 0.0
                fuel_gallons = float(end_row[2]) if end_row[2] else 0.0
                company = str(end_row[3]) if end_row[3] else ''
                carnum = str(end_row[4]) if end_row[4] else ''
                
                try:
                    end_time = datetime.strptime(str(end_row[5]), '%Y-%m-%d %H:%M:%S.%f')
                except:
                    Logger.error(f"Could not parse end time: {end_row[5]}")
                    end_time = datetime.now()
                
                # Extract username from tripID (format: usernameYYYYMMDDHHMMSS)
                import re
                match = re.search(r'(\d{4})(\d{2})(\d{2})', tripID)
                if match:
                    year_pos = match.start()
                    username = tripID[:year_pos]
                else:
                    username = currentUser if currentUser else 'unknown'
                
                Logger.info(f"Uploading trip {tripID}: {distance_km}km, {duration_seconds}s, {fuel_gallons}gal")
                
                # Extract date from tripID for daily stats grouping
                import re
                match = re.search(r'(\d{8})', tripID)
                if match:
                    trip_date = match.group(1)
                else:
                    trip_date = datetime.now().strftime("%Y%m%d")
                
                # Upload to Supabase - this will raise an exception if it fails
                try:
                    DBUploadTripSummary(
                        tripID=tripID,
                        username=username,
                        company=company,
                        carnum=carnum,
                        destination=destination,
                        passenger_type=passenger_type,
                        passenger_count=passenger_count,
                        cargo_type=cargo,
                        distance_km=distance_km,
                        duration_seconds=duration_seconds,
                        fuel_gallons=fuel_gallons,
                        start_time=start_time,
                        end_time=end_time
                    )
                    # If we get here, upload was successful
                    upload_success = True
                    successfully_uploaded.append(tripID)
                    Logger.info(f"✅ Successfully uploaded trip {tripID}")
                    
                    # Track trip for daily stats
                    if trip_date not in trips_by_date:
                        trips_by_date[trip_date] = {
                            'username': username,
                            'trips': [],
                            'numTrips': 0,
                            'totalDist': 0,
                            'totalFuel': 0,
                            'totalTime': timedelta(),
                            'earliest_start': None,
                            'latest_end': None
                        }
                    
                    trips_by_date[trip_date]['numTrips'] += 1
                    trips_by_date[trip_date]['totalDist'] += distance_km
                    trips_by_date[trip_date]['totalFuel'] += fuel_gallons
                    trips_by_date[trip_date]['totalTime'] += timedelta(seconds=duration_seconds)
                    
                    if not trips_by_date[trip_date]['earliest_start'] or start_time < trips_by_date[trip_date]['earliest_start']:
                        trips_by_date[trip_date]['earliest_start'] = start_time
                    if not trips_by_date[trip_date]['latest_end'] or end_time > trips_by_date[trip_date]['latest_end']:
                        trips_by_date[trip_date]['latest_end'] = end_time
                    
                except Exception as upload_error:
                    Logger.error(f"❌ Failed to upload trip {tripID}: {upload_error}")
                    # Don't add to successfully_uploaded list
                    
            except Exception as e:
                Logger.error(f"Error processing trip {tripID}: {e}")
                import traceback
                Logger.error(traceback.format_exc())
                continue
        
        # Save daily stats before clearing trips
        for date, day_data in trips_by_date.items():
            try:
                # Calculate idle time
                if day_data['earliest_start'] and day_data['latest_end']:
                    working_time = day_data['latest_end'] - day_data['earliest_start']
                    idleTime = working_time - day_data['totalTime']
                    if idleTime.total_seconds() < 0:
                        idleTime = timedelta()
                else:
                    idleTime = timedelta()
                
                # Save to local database
                localDBSaveDailyStats(
                    username=day_data['username'],
                    date=date,
                    numTrips=day_data['numTrips'],
                    totalDist=day_data['totalDist'],
                    totalFuel=day_data['totalFuel'],
                    totalTime=day_data['totalTime'],
                    idleTime=idleTime
                )
            except Exception as e:
                Logger.error(f"Error saving daily stats for {date}: {e}")
        
        # Only clear trips that were successfully uploaded
        if successfully_uploaded:
            Logger.info(f"Clearing {len(successfully_uploaded)} successfully uploaded trips from local database")
            for tripID in successfully_uploaded:
                try:
                    cursor.execute("DELETE FROM tripData WHERE tripID = ?", (tripID,))
                    Logger.info(f"Deleted local data for trip {tripID}")
                except Exception as e:
                    Logger.error(f"Error deleting trip {tripID}: {e}")
            
            localdb.commit()
            Logger.info(f"✅ Successfully uploaded and cleared {len(successfully_uploaded)} trips")
        else:
            Logger.warning("⚠️ No trips were successfully uploaded - keeping all local data")
        
        localdb.close()
        
        # Log summary
        total_trips = len(completed_trips)
        failed_trips = total_trips - len(successfully_uploaded)
        if failed_trips > 0:
            Logger.warning(f"⚠️ {failed_trips} trips failed to upload and remain in local database for retry")
        
    except Exception as e:
        Logger.error(f"Error in localDBDumptoServer: {e}")
        import traceback
        Logger.error(traceback.format_exc())

def localDBPullTripCoords(tripID):
    """Pull trip coordinates from local database"""
    [cursor, localdb] = localDBConnect()
    query = "SELECT gpslonXworkingFuel, gpslat FROM tripData WHERE tripID = ? AND destinationXstatus != 'Start Trip' AND destinationXstatus != 'End Trip'"
    cursor.execute(query, (tripID,))
    coords = cursor.fetchall()
    localdb.commit()
    localdb.close()
    return coords

def localDBGetTripStart(tripID):
    """Get trip start time from local database"""
    [cursor, localdb] = localDBConnect()
    query = "SELECT time FROM tripData WHERE tripID = ? AND destinationXstatus = 'Start Trip'"
    cursor.execute(query, (tripID,))
    result = cursor.fetchone()
    localdb.close()
    if result:
        return datetime.strptime(str(result[0]),'%Y-%m-%d %H:%M:%S.%f')
    return datetime.now()

def localDBGetTripStats(tripID):
    """Get trip statistics from local database"""
    [cursor, localdb] = localDBConnect()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,destinationXstatus FROM tripData WHERE destinationXstatus != 'End Trip' AND destinationXstatus != 'Start Trip' AND tripID = ?"
    cursor.execute(query, (tripID,))
    tripData = cursor.fetchone()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,gpslonXworkingFuel FROM tripData WHERE destinationXstatus = 'End Trip' AND tripID = ?"
    cursor.execute(query, (tripID,))
    endData = cursor.fetchone()
    localdb.close()
    
    if endData:
        totalDist = endData[1]
        t = datetime.strptime(str(endData[0]),'%H:%M:%S.%f')
        totalTime = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
        totalFuel = endData[2]
        
        if tripData:
            passengers = "{} with {}".format(tripData[0], tripData[1])
            destination = tripData[2]
        else:
            passengers = "Trip Too Short"
            destination = "Trip Too Short"
        
        return [destination, passengers, totalDist, totalTime, totalFuel]
    
    return ["No Data", "No Data", 0, timedelta(), 0]

def localDBGetDayStats(username, date):
    """Get day statistics from local database - checks saved stats first, then live trip data"""
    [cursor, localdb] = localDBConnect()
    
    # First check if we have saved stats for this day
    query = "SELECT numTrips, totalDist, totalFuel, totalTime, idleTime FROM dailyStats WHERE username = ? AND date = ?"
    cursor.execute(query, (username, date))
    saved_stats = cursor.fetchone()
    
    # Also calculate current live trip stats for today
    dayID = "{}{}".format(username, date)
    query = "SELECT passengersXtotalTime,cargoXtotalDist,gpslonXworkingFuel,time FROM tripData WHERE destinationXstatus = 'End Trip' AND tripID LIKE ?"
    cursor.execute(query, (f"%{dayID}%",))
    trips = cursor.fetchall()
    
    numTrips = 0
    totalDist = 0
    totalTime = timedelta()
    totalFuel = 0
    endTime = None
    dayStart = None
    
    for row in trips:
        numTrips += 1
        totalDist += float(row[1])
        t = datetime.strptime(str(row[0]),'%H:%M:%S.%f')
        totalTime = totalTime + timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
        totalFuel += float(row[2])
        if row[3]:
            endTime = datetime.strptime(str(row[3]),'%Y-%m-%d %H:%M:%S.%f')
    
    if numTrips > 0:
        query = "SELECT time FROM tripData WHERE destinationXstatus = 'Start Trip' AND tripID LIKE ? ORDER BY time LIMIT 1"
        cursor.execute(query, (f"%{dayID}%",))
        start_result = cursor.fetchone()
        if start_result:
            dayStart = datetime.strptime(str(start_result[0]),'%Y-%m-%d %H:%M:%S.%f')
            idleTime = endTime - dayStart - totalTime if endTime else timedelta()
        else:
            idleTime = timedelta()
    else:
        idleTime = timedelta()
    
    # Combine saved stats with live stats
    if saved_stats:
        # Add saved stats to current live stats
        numTrips += int(saved_stats[0])
        totalDist += float(saved_stats[1])
        totalFuel += float(saved_stats[2])
        saved_time_seconds = float(saved_stats[3])
        totalTime = totalTime + timedelta(seconds=saved_time_seconds)
        saved_idle_seconds = float(saved_stats[4])
        idleTime = idleTime + timedelta(seconds=saved_idle_seconds)
        Logger.info(f"Combined saved stats with {numTrips - int(saved_stats[0])} new trips")
    
    localdb.close()
    return [numTrips, totalDist, totalFuel, totalTime, idleTime]

# Rest of the functions remain the same as the original main.py
def onLaunch():
    global currentUser
    global currentCompany
    global currentCar
    global currentDest
    global currentPass
    global currentCargo
    global currentTripID
    try:
        account_data = localDBPullAccountData()
        if account_data:
            currentUser = account_data[0]
        else:
            currentUser = ''
    except:
        currentUser = ''
    currentCompany = ''
    currentCar = ''
    currentDest = ''
    currentPass = ''
    currentCargo = ''
    currentTripID = ''

def startTrip():
    now = datetime.now()
    global currentTripID
    currentTripID = '{}{}{}{}{}{}{}'.format(currentUser, now.year, now.month, now.day, now.hour, now.minute, now.second)
    localDBRecord(currentTripID, currentCompany, currentCar, 'Start Trip', 0, 0, 0, 0, now)

def getTripDistance(tripID):
    """Calculate total trip distance in kilometers using Haversine formula"""
    coords = localDBPullTripCoords(tripID)
    totalDist = 0
    points_processed = 0
    points_filtered = 0
    
    global lon1, lat1, lon2, lat2
    
    for row in coords:
        if points_processed < 1:
            # First GPS point - just save it
            lon1 = radians(float(row[0]))
            lat1 = radians(float(row[1]))
        else:
            # Calculate distance between consecutive points
            lon2 = radians(float(row[0]))
            lat2 = radians(float(row[1]))
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            # Haversine formula
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            R = 6371  # Earth radius in kilometers
            d = R * c  # Distance in kilometers
            
            # Filter out GPS drift - minimum movement threshold
            # minKph km/h over checkFrequency seconds = (minKph * checkFrequency / 3600) km
            min_distance = (minKph * checkFrequency / 3600)
            
            if d >= min_distance:
                totalDist += d
                Logger.debug(f"GPS: Added {d:.3f} km (above {min_distance:.4f} km threshold)")
            else:
                points_filtered += 1
                Logger.debug(f"GPS: Filtered {d:.3f} km (below {min_distance:.4f} km threshold - likely GPS drift)")
            
            # Update previous point
            lon1 = lon2
            lat1 = lat2
        
        points_processed += 1
    
    Logger.info(f"Distance calculation: {totalDist:.3f} km from {points_processed} GPS points ({points_filtered} filtered as noise)")
    return totalDist

# Screen classes with translation support
class Welcome(Screen):
    def on_pre_enter(self):
        # Update all text to current language - skip TextInput widgets
        for widget in self.walk():
            # Skip TextInput widgets completely
            if widget.__class__.__name__ == 'TextInput':
                continue
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text') and widget.text:
                # Check for exact matches
                if 'Welcome' in widget.text or 'Bienvenido' in widget.text:
                    widget.text = translator.get_text('welcome')
                elif 'Username:' in widget.text or 'Usuario:' in widget.text:
                    widget.text = translator.get_text('username')
                elif 'Password:' in widget.text or 'Contraseña:' in widget.text:
                    widget.text = translator.get_text('password')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    # Check for Login button
                    if 'Log In' in widget.text or 'Iniciar Sesión' in widget.text or 'Iniciar' in widget.text:
                        widget.text = translator.get_text('login')
                    # Check for Register link
                    elif "Don't have an account" in widget.text or 'tienes cuenta' in widget.text or 'Regístrate' in widget.text:
                        widget.text = translator.get_text('register_link')
            
    def logIn(self, username, password):
        if(DBCheckConnection()):
            if DBLogin(username, password):
                self.ids.Incorrect.text = ''
                self.ids.Username.text = ''
                self.ids.Password.text = ''
                self.manager.current = "Home"
                self.manager.transition.direction = "up"
                global currentUser
                currentUser = str(username)
            else:
                self.ids.Incorrect.text = translator.get_text('invalid_credentials')
        else:
            self.ids.Incorrect.text = translator.get_text('connection_required_login')

class Home(Screen):
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text') and widget.text:
                if 'Home' in widget.text or 'Inicio' in widget.text:
                    widget.text = translator.get_text('home')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    if 'Start Trip' in widget.text or 'Iniciar viaje' in widget.text or 'Iniciar' in widget.text:
                        widget.text = translator.get_text('start_trip')
                    elif 'Get Stats' in widget.text or 'Ver estadísticas' in widget.text or 'Ver' in widget.text:
                        widget.text = translator.get_text('get_stats')
                    elif 'Log Out' in widget.text or 'Cerrar sesión' in widget.text or 'Cerrar' in widget.text:
                        widget.text = translator.get_text('log_out')
    
    def startTripFromHome(self):
        """Automatically select the first car when starting a trip from home"""
        global currentCompany
        global currentCar
        userData = localDBPullAccountData()
        if userData is not None:
            currentCompany = userData[4]  # company1
            currentCar = userData[5]       # comp1num
        else:
            # Use default values if no user data
            currentCompany = 'Company1'
            currentCar = '1'
        
    def logOut(self):
        global currentUser
        global currentCompany
        global currentCar
        global currentDest
        global currentPass
        global currentCargo
        global currentTripID
        currentUser = ''
        currentCompany = ''
        currentCar = ''
        currentDest = ''
        currentPass = ''
        currentCargo = ''
        currentTripID = ''
        localDBLogOut()

class HomeStatsPage(Screen):
    def on_pre_enter(self):
        # Update all label headings - both main title and category labels
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text') and widget.text:
                # Check exact matches for each label (English or Spanish versions)
                # Main title
                if 'Statistics for Today' in widget.text or 'Estadísticas de Hoy' in widget.text:
                    widget.text = translator.get_text('statistics_today')
                # Category label: Number of Trips
                elif 'Number of Trips' in widget.text or 'Número de Viajes' in widget.text:
                    widget.text = translator.get_text('number_of_trips')
                # Category label: Miles/Kilometers Driven
                elif 'Kilometers Driven' in widget.text or 'Kilómetros Conducidos' in widget.text:
                    widget.text = translator.get_text('miles_driven')
                # Category label: Estimated Gas
                elif 'Estimated Total Gas Usage' in widget.text or 'Uso Total Estimado de Gasolina' in widget.text:
                    widget.text = translator.get_text('estimated_gas')
                # Category label: Total Time
                elif 'Total Driving Time' in widget.text or 'Tiempo Total de Conducción' in widget.text:
                    widget.text = translator.get_text('total_time')
                # Category label: Time Between Trips
                elif 'Time Spent Between Trips' in widget.text or 'Tiempo Entre Viajes' in widget.text:
                    widget.text = translator.get_text('time_between')
        
        # Now update data values - use local storage first
        try:
            # Always use local database for stats (includes saved + live trips)
            statistics = localDBGetDayStats(currentUser, datetime.today().strftime("%Y%m%d"))
            self.ids.NumberOfTrips.text = "{} {}".format(statistics[0], translator.get_text('trips'))
            self.ids.MilesDriven.text = "{:.2f} {}".format(statistics[1], translator.get_text('miles'))
            self.ids.EstimatedGas.text = "{:.2f} {}".format(statistics[2], translator.get_text('gallons'))
            hours = int(statistics[3].seconds/3600)
            minutes = int((statistics[3].seconds-hours*3600)/60)
            seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
            self.ids.TotalTime.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
            hours = int(statistics[4].seconds/3600)
            minutes = int((statistics[4].seconds-hours*3600)/60)
            seconds = int(statistics[4].seconds - hours*3600 - minutes*60)
            self.ids.TimeBetween.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
            
            Logger.info(f"Loaded stats from local storage: {statistics[0]} trips, {statistics[1]:.2f} km")
        except Exception as e:
            Logger.error(f"Error loading stats: {e}")
            self.ids.NumberOfTrips.text = translator.get_text('no_data_available')
            self.ids.MilesDriven.text = translator.get_text('no_data_available')
            self.ids.EstimatedGas.text = translator.get_text('no_data_available')
            self.ids.TotalTime.text = translator.get_text('no_data_available')
            self.ids.TimeBetween.text = translator.get_text('no_data_available')

class Register1(Screen):
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text'):
                # Use exact matching for better reliability
                if 'Please Fill Out the following' in widget.text or 'Por favor complete lo siguiente' in widget.text:
                    widget.text = translator.get_text('fill_out_following')
                elif 'Name:' in widget.text or 'Nombre:' in widget.text:
                    widget.text = translator.get_text('name')
                elif 'Username:' in widget.text or 'Usuario:' in widget.text:
                    widget.text = translator.get_text('username')
                elif 'Password:' in widget.text or 'Contraseña:' in widget.text:
                    widget.text = translator.get_text('password')
                elif 'Phone Number:' in widget.text or 'Número de Teléfono:' in widget.text:
                    widget.text = translator.get_text('phone_number')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text'):
                if 'Next' in widget.text or 'Siguiente' in widget.text:
                    widget.text = translator.get_text('next')
        
    def checkRegPg1(self, username, phone):
        if(DBCheckConnection()):
            if(DBCheckUsernameExists(username) != "Valid"):
                self.ids.Incorrect.text = DBCheckUsernameExists(username)
            elif(DBCheckPhoneExists(phone) != "Valid"):
                self.ids.Incorrect.text = DBCheckPhoneExists(phone)
            else:
                self.manager.current = "Register2"
                self.manager.transition.direction = "up"
        else:
            self.ids.Incorrect.text = translator.get_text('connection_required_register')

class Register2(Screen):
    def on_pre_enter(self):
        # Update all text to current language with exact matching
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text'):
                # Main title
                if 'Complete your Registration' in widget.text or 'Complete su Registro' in widget.text:
                    widget.text = translator.get_text('complete_registration')
                # Company 1 label
                elif 'Company 1:' in widget.text or 'Compañía 1:' in widget.text:
                    widget.text = translator.get_text('car_company')
                # Car Number 1 label
                elif 'Car Number 1:' in widget.text or 'Número de Auto 1:' in widget.text:
                    widget.text = translator.get_text('car_number')
                # Checkbox label
                elif 'Check this Box if you Drive for Another Company' in widget.text or 'Marque esta casilla si maneja para otra compañía' in widget.text:
                    widget.text = translator.get_text('check_another_company')
                # Company 2 label
                elif 'Company 2:' in widget.text or 'Compañía 2:' in widget.text:
                    widget.text = translator.get_text('second_car_company')
                # Car Number 2 label  
                elif 'Car Number 2:' in widget.text or 'Número de Auto 2:' in widget.text:
                    widget.text = translator.get_text('second_car_number')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text'):
                if 'Done' in widget.text or 'Listo' in widget.text:
                    widget.text = translator.get_text('done')
        
    def register(self, username, password, name, phone, comp1, car1, comp2, car2):
        if(DBCheckConnection()):
            DBRegister(username, password, name, phone, comp1, car1, comp2, car2)
            self.manager.get_screen('Register1').ids.UsernameReg.text = ''
            self.manager.get_screen('Register1').ids.PasswordReg.text = ''
            self.manager.get_screen('Register1').ids.NameReg.text = ''
            self.manager.get_screen('Register1').ids.PhoneReg.text = ''
            self.ids.Company1Reg.text = ''
            self.ids.Car1NumReg.text = ''
            self.ids.Company2Reg.text = ''
            self.ids.Car2NumReg.text = ''
            self.manager.current = "Welcome"
            self.manager.transition.direction = "up"
        else:
            self.ids.Incorrect.text = translator.get_text('connection_required_register')

class StartTrip(Screen):
    def on_pre_enter(self):
        userData = localDBPullAccountData()
        if userData:
            self.ids.car1.text = "{} {}".format(userData[4], userData[5])
            self.ids.car2.text = "{} {}".format(userData[6], userData[7])
            if(userData[6] != ''):
                self.ids.car2.disabled = False
                self.ids.car2.opacity = 100
            else:
                self.ids.car2.disabled = True
                self.ids.car2.opacity = 0
    
    def selectCar(self, companyNum):
        global currentCompany
        global currentCar
        userData = localDBPullAccountData()
        if userData:
            currentCompany = userData[2*companyNum+2]
            currentCar = userData[2*companyNum+3]
        
    def getCarLabel(self, companyNum):
        userData = localDBPullAccountData()
        if userData:
            try:
                return("{} {}".format(userData[2*companyNum+2], userData[2*companyNum+1+3]))
            except:
                return "None"
        return "None"
        
    def clearCar(self):
        global currentCompany
        currentCompany = ''

class Destination(Screen):
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label':
                widget.text = translator.get_text('where_going')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    # Check for Highlands/Parte Alta
                    if 'highland' in widget.text.lower() or 'parte' in widget.text.lower() or 'alta' in widget.text.lower():
                        widget.text = translator.get_text('the_highlands')
                    elif 'Puerto Ayora' in widget.text or 'puerto ayora' in widget.text.lower():
                        widget.text = translator.get_text('puerto_ayora')
                    elif 'airport' in widget.text.lower() or 'aeropuerto' in widget.text.lower():
                        widget.text = translator.get_text('airport')
                    elif 'other' in widget.text.lower() or 'otro' in widget.text.lower():
                        widget.text = translator.get_text('other')
        
    def setDest(self, destination):
        global currentDest
        currentDest = destination
        
    def clearCar(self):
        global currentCompany
        currentCompany = ''

class People(Screen):
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label':
                widget.text = translator.get_text('who_driving')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    if 'Student' in widget.text or 'Estudiante' in widget.text:
                        widget.text = translator.get_text('students')
                    elif 'Tourist' in widget.text or 'Turista' in widget.text:
                        widget.text = translator.get_text('tourist')
                    elif 'Local' in widget.text:
                        widget.text = translator.get_text('locals')
        
    def setPass(self, people):
        global currentPass
        currentPass = people
        
    def clearDest(self):
        global currentDest
        currentDest = ''

class PassengerCount(Screen):
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label':
                widget.text = translator.get_text('passenger_count')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    if widget.text in ['1', '2', '3', '4', '5+']:
                        # Numbers don't need translation, keep as is
                        pass
    
    def setPassengerCount(self, count):
        global currentPass
        # Append the count to the current passenger type
        passenger_word = translator.get_text('passengers') if count != '1' else translator.get_text('passenger')
        currentPass = f"{currentPass} - {count} {passenger_word}"
    
    def clearPeople(self):
        global currentPass
        currentPass = ''

class Cargo(Screen):
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label':
                widget.text = translator.get_text('what_cargo')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    if 'Luggage' in widget.text or 'Equipaje' in widget.text:
                        widget.text = translator.get_text('luggage')
                    elif 'Work Equipment' in widget.text or 'Equipo de Trabajo' in widget.text or 'Trabajo' in widget.text:
                        widget.text = translator.get_text('work_equipment')
                    elif 'Food' in widget.text or 'Comida' in widget.text:
                        widget.text = translator.get_text('food_goods')
                    elif 'Bicycle' in widget.text or 'Bicicleta' in widget.text:
                        widget.text = translator.get_text('bicycles')
                    elif 'Varied Load' in widget.text or 'Carga Variada' in widget.text or 'Variada' in widget.text:
                        widget.text = translator.get_text('misc_cargo')
        
    def setCargo(self, cargo):
        global currentCargo
        currentCargo = cargo
        
    def clearPassengerCount(self):
        # Clear passenger count but keep the passenger type
        global currentPass
        # Remove the count part if it exists
        if ' - ' in currentPass:
            currentPass = currentPass.split(' - ')[0]

class FinishTrip(Screen):
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text') and widget.text:
                if 'click' in widget.text.lower() or 'haga' in widget.text.lower():
                    widget.text = translator.get_text('click_complete')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    if 'Complete' in widget.text or 'Completar' in widget.text:
                        widget.text = translator.get_text('complete')
        
    def on_enter(self):
        try:
            app = App.get_running_app()
            app.startGPS(checkFrequency)
        except Exception as e:
            Logger.critical(f"GPS Not Enabled on This Device: {e}")
        startTrip()
    
    def endTrip(self):
        try:
            app = App.get_running_app()
            app.stopGPS()
        except Exception as e:
            Logger.critical(f"GPS Not Set Up on This Device: {e}")
        now = datetime.now()
        dist = round(getTripDistance(currentTripID), 3)
        tripTime = now - localDBGetTripStart(currentTripID)
        
        # Fix gas mileage calculation - ensure non-negative values
        # Only calculate fuel if there's meaningful distance (at least 0.1 km)
        if dist >= 0.1:
            tripFuel = round(dist / mpg, 3)
        else:
            # For very short trips, set fuel to 0
            tripFuel = 0.0
            Logger.info(f"Trip distance too short ({dist} km), setting fuel to 0")
        
        # Ensure fuel is never negative
        if tripFuel < 0:
            tripFuel = 0.0
            Logger.warning(f"Negative fuel value detected, setting to 0")
        
        # Convert tripTime to string for SQLite
        localDBRecord(currentTripID, currentCompany, currentCar, 'End Trip', str(tripTime), dist, tripFuel, '', now)
    
    def clearCargo(self):
        global currentCargo
        self.endTrip()
        currentCargo = ''
        # Don't clear currentTripID here - let TripStats screen handle it
        # after displaying the stats

class TripStats(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.data_uploaded = False
    
    def on_pre_enter(self):
        # Reset the upload flag when entering the screen
        self.data_uploaded = False
        
        # Update all static labels and buttons to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text') and widget.text:
                # Check each possible label heading
                if 'statistics' in widget.text.lower() or 'estadísticas' in widget.text.lower():
                    if 'trip' in widget.text.lower() or 'último' in widget.text.lower() or 'latest' in widget.text.lower():
                        widget.text = translator.get_text('trip_statistics')
                elif widget.text.strip().endswith(':'):
                    # This is a heading label ending with colon
                    text_key = widget.text.strip().rstrip(':').lower()
                    if 'destination' in text_key or 'destino' in text_key:
                        widget.text = translator.get_text('destination')
                    elif 'passenger' in text_key or 'pasajero' in text_key or 'cargo' in text_key:
                        widget.text = translator.get_text('passengers_cargo')
                    elif 'distance' in text_key or 'distancia' in text_key:
                        widget.text = translator.get_text('distance_driven')
                    elif 'duration' in text_key or 'duración' in text_key:
                        widget.text = translator.get_text('trip_duration')
                    elif 'fuel' in text_key or 'combustible' in text_key:
                        widget.text = translator.get_text('estimated_fuel')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    if 'next' in widget.text.lower() or 'próximo' in widget.text.lower() or 'siguiente' in widget.text.lower():
                        widget.text = translator.get_text('start_next_trip')
                    elif widget.text.lower() in ['home', 'inicio']:
                        widget.text = translator.get_text('home')
        
    def on_enter(self):
        # Only fetch statistics if we have a valid trip ID
        if not currentTripID:
            Logger.warning("TripStats: No trip ID available, skipping data load")
            return
            
        statistics = localDBGetTripStats(currentTripID)
        self.ids.Destination.text = str(statistics[0])
        self.ids.PassengersCargo.text = str(statistics[1])
        self.ids.tripDist.text = "{} {}".format(statistics[2], translator.get_text('miles'))
        hours = int(statistics[3].seconds/3600)
        minutes = int((statistics[3].seconds-hours*3600)/60)
        seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
        self.ids.tripTime.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
        self.ids.tripFuel.text = "{} {}".format(statistics[4], translator.get_text('gallons'))
        
        # Upload data immediately when entering the screen (only once)
        if not self.data_uploaded and DBCheckConnection():
            localDBDumptoServer()
            self.data_uploaded = True
            Logger.info("Supabase: Trip data uploaded successfully")
        
    def startNextTrip(self):
        """Automatically select the first car when starting next trip from TripStats"""
        global currentCompany
        global currentCar
        userData = localDBPullAccountData()
        if userData is not None:
            currentCompany = userData[4]  # company1
            currentCar = userData[5]       # comp1num
        else:
            # Use default values if no user data
            currentCompany = 'Company1'
            currentCar = '1'
    
    def clearCurrent(self):
        global currentTripID
        global currentCompany
        global currentCar
        global currentDest
        global currentPass
        global currentCargo
        currentCompany = ''
        currentCar = ''
        currentDest = ''
        currentPass = ''
        currentCargo = ''
        currentTripID = ''

class Loading(Screen):
    pass

class WindowManager(ScreenManager):
    pass

def get_image_path(image_name):
    """Get the correct image path based on current language"""
    current_lang = translator.get_current_language()
    lang_path = os.path.join('images', current_lang, image_name)
    
    # Check if language-specific image exists
    if os.path.exists(lang_path):
        return lang_path
    else:
        # Fall back to root directory image
        return image_name

class MainApp(App):
    # Observable property that triggers KV re-evaluation when language changes
    language = StringProperty('es')  # Initialize to Spanish to match translator default
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = translator
        # Sync the language property with translator's current language
        self.language = translator.get_current_language()
    
    def build(self):
        # Load the appropriate KV file based on language
        kv_file = 'GalapagosCarTracking_translated.kv'  # Spanish is default
        return Builder.load_file(kv_file)
    
    def on_start(self):
        # iOS permissions are handled differently
        if platform == "ios":
            Logger.info("iOS platform detected")
        elif platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.ACCESS_BACKGROUND_LOCATION, Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        
        localDBCreate()
        # Create test account in local DB (DELETE ONCE LOGIN IS POSSIBLE)
        # Company1/2 are placeholders that get translated to "Company 1"/"Compañía 1" etc.
        try:
            # Check if account already exists
            if localDBPullAccountData() is None:
                localDBRegister('testUser', 'testPassword', 'Test User', '1234567890', 'Company1', '1', 'Company2', '2')
        except:
            pass
        onLaunch()  
        self.root.transition = NoTransition()
        try:
            username = localDBPullAccountData()[0]
            if(username != ''):
                self.root.current = "Home"
            else:
                self.root.current = "Welcome"
        except:
            self.root.current = "Welcome"
        self.root.transition = SlideTransition()
        
    def on_gps_location(self, **kwargs):
        global currentlat
        global currentlon
        currentlat = kwargs['lat']
        currentlon = kwargs['lon']
        now = datetime.now()
        localDBRecord(currentTripID, currentCompany, currentCar, currentDest, currentPass, currentCargo, currentlon, currentlat, now)
        
    def on_request_close(self):
        try:
            self.root.get_screen("FinishTrip").endTrip()
        except:
            pass
        return True
        
    def startGPS(self, seconds):
        try:
            gps.configure(on_location=self.on_gps_location, on_status=None)
            gps.start(seconds*1000, 0)
        except Exception as e:
            Logger.critical(f"GPS Error: {e}")
            
    def stopGPS(self):
        try:
            gps.stop()
        except:
            pass
        global currentlat
        global currentlon
        currentlat = 0
        currentlon = 0
    
    def handle_checkbox_active(self, is_checked):
        if is_checked:
            self.root.get_screen('Register2').ids.CarCompanyTwo.opacity = 1
            self.root.get_screen('Register2').ids.Company2Reg.opacity = 1
            self.root.get_screen('Register2').ids.CarNumberTwo.opacity = 1
            self.root.get_screen('Register2').ids.Car2NumReg.opacity = 1
        else:
            self.root.get_screen('Register2').ids.CarCompanyTwo.opacity = 0
            self.root.get_screen('Register2').ids.Company2Reg.opacity = 0
            self.root.get_screen('Register2').ids.CarNumberTwo.opacity = 0
            self.root.get_screen('Register2').ids.Car2NumReg.opacity = 0
    
    def get_image_path(self, image_name):
        """Get the correct image path based on current language"""
        return get_image_path(image_name)
    
    def toggle_language(self):
        """Toggle between English and Spanish"""
        # Toggle language
        translator.toggle_language()
        Logger.info(f"Language toggled to: {translator.get_current_language()}")
        
        # Refresh current screen
        try:
            current_screen = self.root.current
            screen_obj = self.root.get_screen(current_screen)
            if hasattr(screen_obj, 'on_pre_enter'):
                screen_obj.on_pre_enter()
                Logger.info(f"Refreshed {current_screen} screen after language change")
        except Exception as e:
            Logger.error(f"Error refreshing screen: {e}")


# Run the application
if __name__=='__main__':
    MainApp().run()
