import supabase_rest_api as supabase_api
import sqlite3
from kivy.config import Config
# Disable multitouch emulation (removes red dots on screen)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.core.window import Window
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
import os
import time


currentUser = ''
currentCompany = ''
currentCar = ''
currentDest = ''
currentStartPoint = ''
currentPass = ''
currentCargo = ''
currentlat = 0
currentlon = 0
currentTripID = ''
mpg = 25 # the average miles per gallon of taxi cars
checkFrequency = 10 #seconds
minKph = 3.2




def DBShowAll():
    """Show all records from Supabase database"""
    try:
        # Get UserData records
        user_data = supabase_api.select('UserData')
        print("\nUser Data Database")
        for row in user_data:
            print(row)
        
        # Get TripData records
        tracking_data = supabase_api.select('TripData')
        print("\n\nTrip Data Database")
        for row in tracking_data:
            print(row)
        print("\n")
    except Exception as e:
        Logger.error(f"DBShowAll failed: {e}")
 
def DBCheckUsernameExists(username):
    """Check if username exists in Supabase"""
    if username == '':
        return translator.get_text('username_invalid')
    try:
        if supabase_api.check_username_exists(username):
            return translator.get_text('username_exists')
        else:
            return "Valid"
    except Exception as e:
        Logger.error(f"DBCheckUsernameExists failed: {e}")
        return "Error"

def DBCheckPhoneExists(phone):
    """Check if phone exists in Supabase"""
    try:
        int(phone)
    except Exception:
        return translator.get_text('phone_invalid')
    
    try:
        if supabase_api.check_phone_exists(phone):
            return translator.get_text('phone_exists')
        else:
            return "Valid"
    except Exception as e:
        Logger.error(f"DBCheckPhoneExists failed: {e}")
        return "Error"
    
def DBRegister(username, password, name, phone, company1, comp1num, company2, comp2num):
    """Register new user in Supabase"""
    try:
        supabase_api.register_user(username, password, name, phone, company1, comp1num, company2, comp2num)
    except Exception as e:
        Logger.error(f"DBRegister failed: {e}")
        raise

def DBLogin(username, password):
    """Login user from Supabase"""
    try:
        account = supabase_api.login_user(username, password)
        
        if account:
            localDBLogin(
                account['username'], account['password'], account['name'], 
                account['phone'], account['company1'], account['comp1num'], 
                account['company2'], account['comp2num']
            )
            return True
        else:
            return False
    except Exception as e:
        Logger.error(f"DBLogin failed: {e}")
        return False

def DBPullUserData():
    """Pull user data from Supabase"""
    try:
        user = supabase_api.get_user_data(currentUser)
        
        if user:
            return (user['username'], user['password'], user['name'], user['phone'], 
                   user['company1'], user['comp1num'], user['company2'], user['comp2num'])
        return None
    except Exception as e:
        Logger.error(f"DBPullUserData failed: {e}")
        return None

def DBUploadDataPoint(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    """Legacy function - no longer uploads individual GPS points"""
    # GPS points are now only stored locally
    # Trip summaries are uploaded via DBUploadTripSummary
    pass

def DBUploadTripSummary(trip_id, username, company, car_number, destination, passenger_info, 
                        cargo_type, distance_km, duration_seconds, fuel_gallons, 
                        start_time, end_time, starting_point=""):
    """Upload complete trip summary to TripData table"""
    try:
        # Parse passenger_info to extract passenger_type and count
        # Format is typically: "passenger_type - count" or just "passenger_type"
        passenger_type = ""
        passenger_count = ""
        
        if passenger_info and ' - ' in passenger_info:
            parts = passenger_info.split(' - ', 1)
            passenger_type = parts[0]
            passenger_count = parts[1] if len(parts) > 1 else ""
        else:
            passenger_type = passenger_info if passenger_info else ""
        
        # Format timestamps to ISO format for PostgreSQL
        if isinstance(start_time, datetime):
            start_time_str = start_time.isoformat()
        else:
            start_time_str = str(start_time)
            
        if isinstance(end_time, datetime):
            end_time_str = end_time.isoformat()
        else:
            end_time_str = str(end_time)
        
        supabase_api.upload_trip_summary(
            trip_id=trip_id,
            username=username,
            company=company,
            car_number=car_number,
            destination=destination,
            passenger_type=passenger_type,
            passenger_count=passenger_count,
            cargo_type=cargo_type,
            distance_km=distance_km,
            duration_seconds=duration_seconds,
            fuel_gallons=fuel_gallons,
            start_time=start_time_str,
            end_time=end_time_str,
            starting_point=starting_point
        )
        Logger.info(f"Trip summary uploaded: {trip_id}")
    except Exception as e:
        Logger.error(f"DBUploadTripSummary failed: {e}")

def DBCheckConnection():
    """Check if Supabase connection is available"""
    return supabase_api.test_connection()

def DBGetDayStats(username, date):
    """Get daily statistics from Supabase using new TripData schema"""
    try:
        result = supabase_api.get_day_stats(username, date)
        trips = result['trips']
        
        numTrips = 0
        totalDist = 0
        totalTime = timedelta()
        totalFuel = 0
        firstStartTime = None
        lastEndTime = None
        
        for row in trips:
            numTrips += 1
            # New schema uses distance_km, duration_seconds, fuel_gallons
            if row.get('distance_km'):
                totalDist += float(row['distance_km'])
            if row.get('duration_seconds'):
                totalTime += timedelta(seconds=int(row['duration_seconds']))
            if row.get('fuel_gallons'):
                totalFuel += float(row['fuel_gallons'])
            
            # Track first start and last end times for idle time calculation
            if row.get('start_time'):
                start = datetime.fromisoformat(str(row['start_time']).replace('Z', '+00:00'))
                if not firstStartTime or start < firstStartTime:
                    firstStartTime = start
            
            if row.get('end_time'):
                end = datetime.fromisoformat(str(row['end_time']).replace('Z', '+00:00'))
                if not lastEndTime or end > lastEndTime:
                    lastEndTime = end
        
        # Calculate idle time (time between first trip start and last trip end, minus total driving time)
        if firstStartTime and lastEndTime:
            totalDayTime = lastEndTime - firstStartTime
            idleTime = totalDayTime - totalTime
        else:
            idleTime = timedelta()
        
        return [numTrips, totalDist, totalFuel, totalTime, idleTime]
    except Exception as e:
        Logger.error(f"DBGetDayStats failed: {e}")
        raise
        
    

def localDBConnect():
    localdb = sqlite3.connect('local_db.db')
    cursor = localdb.cursor()
    return [cursor, localdb]

def localDBCreate():
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
    localdb.commit()
    localdb.close()

def localDBDelete():
    [cursor, localdb] = localDBConnect()
    #cursor.execute("DROP TABLE accountData")
    cursor.execute("DROP TABLE tripData")
    localdb.commit()
    localdb.close()

def localDBShowAll():
    [cursor,localdb] = localDBConnect()
    # Grab records from database
    cursor.execute("SELECT * FROM accountData")
    records = cursor.fetchall()
    print("\nAccount Data Data Base")
    for row in records:
        print(row)
    cursor.execute("SELECT * FROM tripData")
    records = cursor.fetchall()
    print("\n")
    print("\nTrip Data Data Base")
    for row in records:
        print(row)
    print("\n")
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()

def localDBLogin(username, password, name, phone, company1, comp1num, company2, comp2num):
    [cursor, localdb] = localDBConnect()
    localDBLogOut()
    query = "INSERT INTO accountData (username, password, name, phone, company1, comp1num, company2, comp2num) values ('{}','{}','{}','{}','{}','{}','{}','{}')".format(username, password, name, phone, company1, comp1num, company2, comp2num)
    cursor.execute(query)
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()

def localDBPullAccountData():
    [cursor, localdb] = localDBConnect()
    query = "SELECT * FROM accountData"
    cursor.execute(query)
    records = cursor.fetchone()
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()
    return records

def localDBLogOut():
    [cursor, localdb] = localDBConnect()
    # Clear Data
    query = "DELETE FROM accountData"
    cursor.execute(query)
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()

def localDBClearTrip():
    [cursor, localdb] = localDBConnect()
    # Clear Data
    query = "DELETE FROM tripData"
    cursor.execute(query)
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()

def localDBRecord(username, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    [cursor, localdb] = localDBConnect()
    query = "INSERT INTO tripData (tripID, company, carnum, destinationXstatus, passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, gpslat, time) values ('{}','{}','{}','{}','{}','{}','{}','{}','{}')".format(username, company, carnum, destination, passengers, cargo, gpslon, gpslat, time)
    cursor.execute(query)
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()
    # Don't print every GPS point
    if destination in ['Start Trip', 'End Trip']:
        localDBShowAll()

def localDBDumptoServer():
    """Upload trip summary to TripData table"""
    [cursor, localdb] = localDBConnect()
    
    try:
        # Get the MOST RECENT trip start record
        query = "SELECT tripID, company, carnum, time FROM tripData WHERE destinationXstatus = 'Start Trip' ORDER BY time DESC LIMIT 1"
        cursor.execute(query)
        start_record = cursor.fetchone()
        
        if not start_record:
            Logger.warning("No trip start record found")
            localdb.close()
            return
        
        trip_id = start_record[0]
        print(f"\n==== PROCESSING TRIP: {trip_id} ====")
        Logger.info(f"Processing trip: {trip_id}")
        company = start_record[1]
        car_number = start_record[2]
        start_time = datetime.strptime(str(start_record[3]), '%Y-%m-%d %H:%M:%S.%f')
        
        # Use the global variables for trip info (destination, passengers, cargo)
        # These are set during the trip workflow
        destination = currentDest
        passenger_info = currentPass  
        cargo_type = currentCargo
        starting_point = currentStartPoint
        
        print(f"Destination: {destination}")
        print(f"Passengers: {passenger_info}")
        print(f"Cargo: {cargo_type}")
        print(f"Starting Point: {starting_point}")
        
        # Get the trip end record with totals
        query = "SELECT passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, time FROM tripData WHERE destinationXstatus = 'End Trip' AND tripID = ?"
        cursor.execute(query, (trip_id,))
        end_record = cursor.fetchone()
        
        if not end_record:
            Logger.warning(f"No trip end record found for trip_id: {trip_id}")
            Logger.warning(f"Checking all records for this trip...")
            # Debug: show all records for this trip
            cursor.execute("SELECT * FROM tripData WHERE tripID = ?", (trip_id,))
            all_records = cursor.fetchall()
            for rec in all_records:
                Logger.warning(f"Record: {rec}")
            localdb.close()
            return
        
        # Parse end data
        duration_timedelta = end_record[0]
        distance_km = float(end_record[1])
        fuel_gallons = float(end_record[2])
        end_time = datetime.strptime(str(end_record[3]), '%Y-%m-%d %H:%M:%S.%f')
        
        # Convert timedelta to seconds
        if isinstance(duration_timedelta, timedelta):
            duration_seconds = int(duration_timedelta.total_seconds())
        else:
            # Parse from string if needed
            try:
                t = datetime.strptime(str(duration_timedelta), '%H:%M:%S.%f')
                duration_seconds = t.hour * 3600 + t.minute * 60 + t.second
            except:
                duration_seconds = 0
        
        # Upload to server
        DBUploadTripSummary(
            trip_id=trip_id,
            username=currentUser,
            company=company,
            car_number=car_number,
            destination=destination,
            passenger_info=passenger_info,
            cargo_type=cargo_type,
            distance_km=distance_km,
            duration_seconds=duration_seconds,
            fuel_gallons=fuel_gallons,
            start_time=start_time,
            end_time=end_time,
            starting_point=currentStartPoint if currentStartPoint else ""
        )
        
    except Exception as e:
        Logger.error(f"localDBDumptoServer failed: {e}")
    
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()
    # Clear local data
    localDBClearTrip()

def localDBPullTripCoords(tripID):
    [cursor, localdb] = localDBConnect()
    query = "SELECT gpslonXworkingFuel, gpslat FROM tripData WHERE tripID = '{}' AND destinationXstatus != 'Start Trip' AND destinationXstatus != 'End Trip'".format(tripID)
    cursor.execute(query)
    coords = cursor.fetchall()
    # Save Changes
    localdb.commit()
    # Close our connection
    localdb.close()
    return coords

def localDBGetTripStart(tripID): 
    [cursor, localdb] = localDBConnect()
    query = "SELECT time FROM tripData WHERE tripID = '{}' AND destinationXstatus = 'Start Trip'".format(tripID)
    cursor.execute(query)
    time = datetime.strptime(str(cursor.fetchone()[0]),'%Y-%m-%d %H:%M:%S.%f')
    return time

def localDBGetTripStats(tripID):
    [cursor, localdb] = localDBConnect()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,destinationXstatus FROM tripData WHERE destinationXstatus != 'End Trip' AND destinationXstatus != 'Start Trip' AND tripID = '{}'".format(tripID)
    cursor.execute(query)
    tripData = cursor.fetchone()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,gpslonXworkingFuel FROM tripData WHERE destinationXstatus = 'End Trip' AND tripID = '{}'".format(tripID)
    cursor.execute(query)
    endData = cursor.fetchone()
    totalDist = endData[1]
    t = datetime.strptime(str(endData[0]),'%H:%M:%S.%f')
    totalTime = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
    totalFuel = endData[2]
    try:
        passengers = "{} with {}".format(tripData[0], tripData[1])
        destination = tripData[2]
    except:
        passengers = "Trip Too Short"
        destination = "Trip Too Short"
    return [destination, passengers, totalDist, totalTime, totalFuel]



def onLaunch():
    global currentUser
    global currentCompany
    global currentCar
    global currentDest
    global currentPass
    global currentCargo
    global currentTripID
    try:
        currentUser = localDBPullAccountData()[0]
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

def getTripDistance(tripID):
    coords = localDBPullTripCoords(tripID)
    totalDist = 0
    rowNum = 0
    lon1 = lat1 = lon2 = lat2 = 0.0
    for row in coords:
        if(rowNum < 1):
            lon1 = radians(float(row[0]))
            lat1 = radians(float(row[1]))
        else:
            lon2 = radians(float(row[0]))
            lat2 = radians(float(row[1]))
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))
            R = 6371.0 # radius of earth in kilometers
            d = R * c
            if(d >= (minKph*checkFrequency/3600)): # prevents movements smaller than minKph average speed to not be recorded
                totalDist += d
            lon1 = lon2
            lat1 = lat2
        rowNum += 1
    return totalDist



class Welcome(Screen):
    def logIn(self, username, password):
        if(DBCheckConnection()):
            if DBLogin(username, password):
                self.ids.Incorrect.text = ''
                self.ids.Username.text = ''
                self.ids.Password.text = ''
                self.manager.current = "Home" # sets the window to the window with the name given
                self.manager.transition.direction = "up"  # sets transition direction
                global currentUser
                currentUser = str(username)
            else:
                self.ids.Incorrect.text = translator.get_text('invalid_credentials')
        else:
            self.ids.Incorrect.text = translator.get_text('connection_required_login')
       
class Home(Screen):
    def autoSelectFirstCar(self):
        """Automatically select the first car for the user"""
        global currentCompany
        global currentCar
        userData = localDBPullAccountData()
        currentCompany = userData[4]
        currentCar = userData[5]
        
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
        if(DBCheckConnection()):
            try:
                statistics = DBGetDayStats(currentUser, datetime.today().strftime("%Y%m%d"))
                self.ids.NumberOfTrips.text = "{} {}".format(statistics[0], translator.get_text('trips'))
                self.ids.MilesDriven.text = "{} {}".format(statistics[1], translator.get_text('km'))
                self.ids.EstimatedGas.text = "{} {}".format(statistics[2], translator.get_text('gallons'))
                hours = int(statistics[3].seconds/3600)
                minutes = int((statistics[3].seconds-hours*3600)/60)
                seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
                self.ids.TotalTime.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
                hours = int(statistics[4].seconds/3600)
                minutes = int((statistics[4].seconds-hours*3600)/60)
                seconds = int(statistics[4].seconds - hours*3600 - minutes*60)
                self.ids.TimeBetween.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
            except Exception:
                no_data = translator.get_text('no_data_available')
                self.ids.NumberOfTrips.text = no_data
                self.ids.MilesDriven.text = no_data
                self.ids.EstimatedGas.text = no_data
                self.ids.TotalTime.text = no_data
                self.ids.TimeBetween.text = no_data
        else:
            conn_req = translator.get_text('connection_required')
            self.ids.NumberOfTrips.text = conn_req
            self.ids.MilesDriven.text = conn_req
            self.ids.EstimatedGas.text = conn_req
            self.ids.TotalTime.text = conn_req
            self.ids.TimeBetween.text = conn_req

class IndividualTripsPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_view = 'today'  # Track which view is active
    
    def on_pre_enter(self):
        """Load and display today's trips by default"""
        self.load_todays_trips()
    
    def refresh_current_view(self):
        """Refresh the currently displayed view (used when language changes)"""
        if self.current_view == 'today':
            self.load_todays_trips()
        else:
            self.load_past_trips()
    
    def update_button_styles(self):
        """Update button styles based on current view"""
        if hasattr(self, 'ids'):
            today_btn = self.ids.get('today_btn')
            past_btn = self.ids.get('past_btn')
            
            if today_btn and past_btn:
                if self.current_view == 'today':
                    # Today is selected - black background, white text
                    today_btn.background_color = (0.05, 0.05, 0.05, 1)
                    today_btn.color = (1, 1, 1, 1)
                    # Past is unselected - light background, dark text
                    past_btn.background_color = (0.92, 0.92, 0.92, 1)
                    past_btn.color = (0.4, 0.4, 0.4, 1)
                else:
                    # Past is selected - black background, white text
                    past_btn.background_color = (0.05, 0.05, 0.05, 1)
                    past_btn.color = (1, 1, 1, 1)
                    # Today is unselected - light background, dark text
                    today_btn.background_color = (0.92, 0.92, 0.92, 1)
                    today_btn.color = (0.4, 0.4, 0.4, 1)
    
    def load_todays_trips(self):
        """Load only today's trips"""
        self.current_view = 'today'
        self.update_button_styles()
        Logger.info(f"Loading TODAY's trips for user: {currentUser}")
        if(DBCheckConnection()):
            try:
                # Get today's trips
                date_str = datetime.today().strftime("%Y%m%d")
                trips = supabase_api.get_individual_trips(currentUser, date=date_str)
                Logger.info(f"Retrieved {len(trips) if trips else 0} trips for today")
                self.populate_trips(trips)
            except Exception as e:
                Logger.error(f"Failed to load today's trips: {e}")
                import traceback
                Logger.error(traceback.format_exc())
                self.show_error_message()
        else:
            Logger.warning("No database connection available")
            self.show_connection_error()
    
    def load_past_trips(self):
        """Load all past trips (excluding today)"""
        self.current_view = 'past'
        self.update_button_styles()
        Logger.info(f"Loading PAST trips for user: {currentUser}")
        if(DBCheckConnection()):
            try:
                # Get ALL trips
                all_trips = supabase_api.get_individual_trips(currentUser, date=None)
                
                # Filter out today's trips
                today_str = datetime.today().strftime('%Y-%m-%d')
                past_trips = []
                for trip in all_trips:
                    try:
                        start_time = datetime.fromisoformat(str(trip.get('start_time')).replace('Z', '+00:00'))
                        trip_date = start_time.strftime('%Y-%m-%d')
                        if trip_date != today_str:
                            past_trips.append(trip)
                    except:
                        pass
                
                Logger.info(f"Retrieved {len(past_trips)} past trips")
                self.populate_trips(past_trips)
            except Exception as e:
                Logger.error(f"Failed to load past trips: {e}")
                import traceback
                Logger.error(traceback.format_exc())
                self.show_error_message()
        else:
            Logger.warning("No database connection available")
            self.show_connection_error()
    
    def populate_trips(self, trips):
        """Populate the trips list in the UI with condensed trip cards"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.uix.widget import Widget
        from kivy.uix.button import Button
        from kivy.graphics import Color, RoundedRectangle
        
        # Get the trips container
        trips_container = self.ids.trips_container
        trips_container.clear_widgets()
        
        # Debug logging
        Logger.info(f"Populate trips called with {len(trips) if trips else 0} trips")
        if trips:
            for idx, trip in enumerate(trips):
                Logger.info(f"Trip {idx+1}: {trip.get('destination')} at {trip.get('start_time')}")
        
        if not trips or len(trips) == 0:
            # No trips found
            no_trips_label = Label(
                text=translator.get_text('no_trips_today'),
                font_name='CaviarDreams.ttf',
                font_size='18sp',
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height='100dp',
                halign='center'
            )
            trips_container.add_widget(no_trips_label)
            return
        
        # Display trips with most recent at top, numbered in descending order
        # Database returns trips in reverse chronological order (newest first)
        total_trips = len(trips)
        
        # Display each trip as a condensed clickable card
        for idx, trip in enumerate(trips):
            # Number from highest to lowest (most recent = highest number)
            trip_num = total_trips - idx
            Logger.info(f"Creating card for trip {trip_num}")
            trip_card = self.create_condensed_trip_card(trip_num, trip)
            trips_container.add_widget(trip_card)
            Logger.info(f"Added card {trip_num} to container")
            
            # Add spacing between trips
            if idx < len(trips) - 1:
                spacer = Widget(size_hint_y=None, height='10dp')
                trips_container.add_widget(spacer)
        
        Logger.info(f"Total widgets in container: {len(trips_container.children)}")
        Logger.info(f"Container minimum height: {trips_container.minimum_height}")
    
    def create_condensed_trip_card(self, trip_num, trip):
        """Create a condensed clickable card for a single trip"""
        from kivy.uix.button import Button
        from kivy.graphics import Color, RoundedRectangle
        from kivy.app import App
        
        # Parse timestamps and check if trip is from today
        try:
            start_time = datetime.fromisoformat(str(trip.get('start_time')).replace('Z', '+00:00'))
            time_str = start_time.strftime('%I:%M %p')
            trip_date = start_time.strftime('%m/%d/%Y')
            today_date = datetime.today().strftime('%m/%d/%Y')
            is_today = (trip_date == today_date)
        except Exception as e:
            Logger.error(f"Error parsing time: {e}")
            time_str = 'N/A'
            trip_date = ''
            is_today = True
        
        starting = trip.get('starting_point', 'N/A')
        ending = trip.get('destination', 'N/A')
        
        # Create button text - include date if not today
        if is_today:
            button_text = f"Trip #{trip_num}     {time_str}\n{starting} → {ending}"
        else:
            button_text = f"{trip_date}  {time_str}\n{starting} → {ending}"
        
        # Square styled button with more padding
        card = Button(
            text=button_text,
            font_name='CaviarDreams.ttf',
            font_size='15sp',
            size_hint_y=None,
            height='90dp',
            halign='center',
            valign='middle',
            text_size=(None, None),
            background_normal='',
            background_color=(0, 0, 0, 0),
            color=(0.1, 0.1, 0.1, 1)
        )
        
        # Bind text_size to button size for text wrapping
        card.bind(size=lambda instance, value: setattr(instance, 'text_size', (value[0] - 40, None)))
        
        # Add white background with rounded corners
        with card.canvas.before:
            Color(1, 1, 1, 1)
            card.bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12, 12, 12, 12])
        
        def update_bg(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        card.bind(pos=update_bg, size=update_bg)
        
        # Make button clickable - navigate to detail page
        def on_button_click(instance):
            try:
                Logger.info(f"Trip card {trip_num} clicked")
                app = App.get_running_app()
                detail_screen = app.root.get_screen('TripDetailPage')
                detail_screen.load_trip_details(trip, trip_num)
                app.root.current = "TripDetailPage"
                app.root.transition.direction = "left"
            except Exception as e:
                Logger.error(f"Error navigating to detail page: {e}")
                import traceback
                Logger.error(traceback.format_exc())
        
        card.bind(on_release=on_button_click)
        
        return card
    
    def create_trip_card(self, trip_num, trip):
        """Create a card widget for a single trip"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.label import Label
        from kivy.graphics import Color, RoundedRectangle
        
        # Main card container
        card = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=['15dp', '15dp'],
            spacing='8dp'
        )
        
        # Add white background with rounded corners
        with card.canvas.before:
            Color(1, 1, 1, 1)
            card.bg_rect = RoundedRectangle(pos=card.pos, size=card.size, radius=[12, 12, 12, 12])
        
        def update_bg(instance, value):
            instance.bg_rect.pos = instance.pos
            instance.bg_rect.size = instance.size
        
        card.bind(pos=update_bg, size=update_bg)
        
        # Trip header
        header = Label(
            text=f"{translator.get_text('trip')} #{trip_num}",
            font_name='CaviarDreams_Bold.ttf',
            font_size='20sp',
            color=(0.1, 0.1, 0.1, 1),
            size_hint_y=None,
            height='30dp',
            halign='left'
        )
        header.bind(size=header.setter('text_size'))
        card.add_widget(header)
        
        # Parse timestamps
        try:
            start_time = datetime.fromisoformat(str(trip.get('start_time')).replace('Z', '+00:00'))
            end_time = datetime.fromisoformat(str(trip.get('end_time')).replace('Z', '+00:00'))
            
            start_str = start_time.strftime('%I:%M %p')
            end_str = end_time.strftime('%I:%M %p')
            
            time_label = Label(
                text=f"{start_str} - {end_str}",
                font_name='CaviarDreams.ttf',
                font_size='16sp',
                color=(0.4, 0.4, 0.4, 1),
                size_hint_y=None,
                height='25dp',
                halign='left'
            )
            time_label.bind(size=time_label.setter('text_size'))
            card.add_widget(time_label)
        except:
            pass
        
        # Trip details
        details = [
            (translator.get_text('destination'), trip.get('destination', 'N/A')),
            (translator.get_text('starting_point'), trip.get('starting_point', 'N/A')),
            (translator.get_text('passengers'), f"{trip.get('passenger_type', 'N/A')} - {trip.get('passenger_count', '')}"),
            (translator.get_text('cargo'), trip.get('cargo_type', 'N/A')),
            (translator.get_text('distance'), f"{trip.get('distance_km', 0):.2f} {translator.get_text('km')}"),
            (translator.get_text('duration'), self.format_duration(trip.get('duration_seconds', 0))),
            (translator.get_text('fuel'), f"{trip.get('fuel_gallons', 0):.2f} {translator.get_text('gallons')}")
        ]
        
        for label, value in details:
            detail_row = BoxLayout(
                orientation='horizontal',
                size_hint_y=None,
                height='25dp',
                spacing='10dp'
            )
            
            label_widget = Label(
                text=f"{label}:",
                font_name='CaviarDreams_Bold.ttf',
                font_size='14sp',
                color=(0.3, 0.3, 0.3, 1),
                size_hint_x=0.4,
                halign='left'
            )
            label_widget.bind(size=label_widget.setter('text_size'))
            
            value_widget = Label(
                text=str(value),
                font_name='CaviarDreams.ttf',
                font_size='14sp',
                color=(0.1, 0.1, 0.1, 1),
                size_hint_x=0.6,
                halign='left'
            )
            value_widget.bind(size=value_widget.setter('text_size'))
            
            detail_row.add_widget(label_widget)
            detail_row.add_widget(value_widget)
            card.add_widget(detail_row)
        
        # Calculate card height based on content
        card.height = '320dp'
        
        return card
    
    def format_duration(self, seconds):
        """Format duration in seconds to readable string"""
        hours = int(seconds / 3600)
        minutes = int((seconds - hours * 3600) / 60)
        secs = int(seconds - hours * 3600 - minutes * 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def show_error_message(self):
        """Show error message when data cannot be loaded"""
        from kivy.uix.label import Label
        trips_container = self.ids.trips_container
        trips_container.clear_widgets()
        
        error_label = Label(
            text=translator.get_text('error_loading_trips'),
            font_name='CaviarDreams.ttf',
            font_size='16sp',
            color=(0.85, 0.2, 0.2, 1),
            size_hint_y=None,
            height='100dp',
            halign='center'
        )
        trips_container.add_widget(error_label)
    
    def show_connection_error(self):
        """Show connection error message"""
        from kivy.uix.label import Label
        trips_container = self.ids.trips_container
        trips_container.clear_widgets()
        
        error_label = Label(
            text=translator.get_text('connection_required'),
            font_name='CaviarDreams.ttf',
            font_size='16sp',
            color=(0.85, 0.2, 0.2, 1),
            size_hint_y=None,
            height='100dp',
            halign='center'
        )
        trips_container.add_widget(error_label)

class Register1(Screen):        
    def checkRegPg1(self, username, phone):
        if(DBCheckConnection()):
            if(DBCheckUsernameExists(username) != "Valid"):
                self.ids.Incorrect.text = DBCheckUsernameExists(username)
            elif(DBCheckPhoneExists(phone) != "Valid"):
                self.ids.Incorrect.text = DBCheckPhoneExists(phone)
            else:
                self.manager.current = "Register2" # sets the window to the window with the name given
                self.manager.transition.direction = "up" # sets transition direction    
        else:
            self.ids.Incorrect.text = translator.get_text('connection_required_register')
   
class Register2(Screen):
    def register(self, username, password, name, phone, car_num):
        if(DBCheckConnection()):
            # Get selected company from dropdown
            selected_company = self.ids.CompanySpinner.text
            
            # Check if user selected from dropdown (not the default text)
            if selected_company == translator.get_text('select_company'):
                selected_company = ''
            
            # Add additional company if specified
            additional_company = self.ids.AdditionalCompanyReg.text.strip()
            if additional_company:
                if selected_company:
                    selected_company = f"{selected_company}, {additional_company}"
                else:
                    selected_company = additional_company
            
            # Register with companies as comp1, empty comp2
            DBRegister(username, password, name, phone, selected_company, car_num, '', '')
            
            # Clear all fields
            self.manager.get_screen('Register1').ids.UsernameReg.text = ''
            self.manager.get_screen('Register1').ids.PasswordReg.text = ''
            self.manager.get_screen('Register1').ids.NameReg.text = ''
            self.manager.get_screen('Register1').ids.PhoneReg.text = ''
            self.ids.Car1NumReg.text = ''
            self.ids.CompanySpinner.text = translator.get_text('select_company')
            self.ids.AnotherCompanyCheck.active = False
            self.ids.AdditionalCompanyReg.text = ''
            
            self.manager.current = "Welcome"
            self.manager.transition.direction = "up"
        else:
            self.ids.Incorrect.text = translator.get_text('connection_required_register')

class StartTrip(Screen):
    def on_pre_enter(self):
        userData = localDBPullAccountData()
        self.ids.car1.text = "{}".format(userData[4])
        self.ids.car2.text = "{}".format(userData[6])
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
        currentCompany = userData[2*companyNum+2]
        currentCar = userData[2*companyNum+3]
        
    def getCarLabel(self, companyNum):
        userData = localDBPullAccountData()       
        try:
            return("{} {}".format(userData[2*companyNum+2], userData[2*companyNum+1+3]))
        except:
            return "None"
        
    def clearCar(self):
        global currentCompany
        currentCompany = ''

class Destination(Screen):
    def setDest(self, destination):
        global currentDest
        currentDest = destination
        
    def clearCar(self):
        global currentCompany
        currentCompany = ''

class StartingPoint(Screen):
    def setStartPoint(self, startPoint):
        global currentStartPoint
        currentStartPoint = startPoint
        
    def clearStartPoint(self):
        global currentStartPoint
        currentStartPoint = ''
    
class People(Screen):
    def setPass(self, people):
        global currentPass
        currentPass = people
        
    def clearStartPoint(self):
        global currentStartPoint
        currentStartPoint = ''

class PassengerCount(Screen):
    def setPassengerCount(self, count):
        global currentPass
        # Combine passenger type (from People screen) with count
        # currentPass already has the passenger type from the People screen
        if currentPass and currentPass != '':
            # Append the count to the passenger type: "Students - 3"
            currentPass = f"{currentPass} - {count}"
        else:
            # Fallback if passenger type is missing
            currentPass = count
        
    def clearPeople(self):
        global currentPass
        currentPass = ''

class Cargo(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected_cargo = {}  # Changed to dict to track button states
        self._last_click_time = 0  # Track last click time for debouncing
    
    def on_pre_enter(self):
        # Reset all selections
        self.selected_cargo = {
            'Luggage': False,
            'Bike': False,
            'Work Equipment': False,
            'Food and Goods': False,
            'Miscellaneous Cargo': False
        }
        # Update button states
        if hasattr(self, 'ids'):
            self.update_button_appearance('luggage_btn', False, 'Luggage')
            self.update_button_appearance('bike_btn', False, 'Bike')
            self.update_button_appearance('work_btn', False, 'Work Equipment')
            self.update_button_appearance('food_btn', False, 'Food and Goods')
            self.update_button_appearance('misc_btn', False, 'Miscellaneous Cargo')
    
    def toggle_cargo(self, cargo_type, button_id):
        """Toggle cargo selection and update button appearance with debouncing"""
        # Debounce: ignore if called within 300ms of last click
        current_time = time.time()
        if current_time - self._last_click_time < 0.3:
            Logger.info(f"[DEBOUNCE] Cargo click ignored - too soon ({(current_time - self._last_click_time)*1000:.0f}ms since last click)")
            return
        
        self._last_click_time = current_time
        Logger.info(f"[CARGO] Toggling {cargo_type}")
        
        # Toggle the selection state
        self.selected_cargo[cargo_type] = not self.selected_cargo[cargo_type]
        # Update button appearance
        self.update_button_appearance(button_id, self.selected_cargo[cargo_type], cargo_type)
    
    def update_button_appearance(self, button_id, is_selected, cargo_type=None):
        """Bordered-box style: white+outline when unselected, filled green+checkmark when selected"""
        from kivy.app import App
        from kivy.graphics import Color, RoundedRectangle, Line
        app = App.get_running_app()

        if not hasattr(self, 'ids'):
            return
        button = getattr(self.ids, button_id, None)
        if not button:
            return

        translation_map = {
            'Luggage': 'luggage',
            'Bike': 'bike',
            'Work Equipment': 'work_equipment',
            'Food and Goods': 'food_goods',
            'Miscellaneous Cargo': 'misc_cargo'
        }
        if cargo_type not in translation_map:
            return

        base_text = app.translator.get_text(translation_map[cargo_type])
        # Transparent native background — canvas drives the visuals
        button.background_normal = ''
        button.background_color = (0, 0, 0, 0)

        button.canvas.before.clear()
        with button.canvas.before:
            if is_selected:
                Color(0.18, 0.65, 0.18, 1)
                RoundedRectangle(pos=button.pos, size=button.size, radius=[10, 10, 10, 10])
            else:
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=button.pos, size=button.size, radius=[10, 10, 10, 10])
                Color(0.3, 0.3, 0.3, 1)
                Line(rounded_rectangle=(button.x, button.y, button.width, button.height, 10), width=1.5)

        button.text = (f'✓  {base_text}') if is_selected else base_text
        button.color = (1, 1, 1, 1) if is_selected else (0.15, 0.15, 0.15, 1)

        # Bind once so the drawn shapes follow layout changes
        if not getattr(button, '_cargo_bound', False):
            def _redraw(instance, _value):
                self._draw_cargo_button(instance, cargo_type)
            button.bind(pos=_redraw, size=_redraw)
            button._cargo_bound = True

    def _draw_cargo_button(self, button, cargo_type):
        """Redraw cargo button canvas after a pos/size change"""
        from kivy.graphics import Color, RoundedRectangle, Line
        is_selected = self.selected_cargo.get(cargo_type, False)
        button.canvas.before.clear()
        with button.canvas.before:
            if is_selected:
                Color(0.18, 0.65, 0.18, 1)
                RoundedRectangle(pos=button.pos, size=button.size, radius=[10, 10, 10, 10])
            else:
                Color(1, 1, 1, 1)
                RoundedRectangle(pos=button.pos, size=button.size, radius=[10, 10, 10, 10])
                Color(0.3, 0.3, 0.3, 1)
                Line(rounded_rectangle=(button.x, button.y, button.width, button.height, 10), width=1.5)
    
    def proceed_to_next(self):
        global currentCargo
        # Get list of selected items
        selected_items = [cargo for cargo, selected in self.selected_cargo.items() if selected]
        if selected_items:
            currentCargo = ', '.join(selected_items)
        else:
            currentCargo = 'None'
        self.manager.current = "StartTripConfirmation"
        self.manager.transition.direction = "up"
        
    def clearPassengerCount(self):
        global currentPass
        currentPass = ''

class StartTripConfirmation(Screen):
    """Screen to confirm and initiate trip tracking"""
    def start_trip_now(self):
        """Initialize GPS tracking and start the trip"""
        try:
            app = App.get_running_app()
            if app:
                app.startGPS(checkFrequency)
        except Exception as e:
            Logger.error(f"GPS initialization failed: {e}")
        
        try:
            startTrip()
        except Exception as e:
            Logger.error(f"Failed to start trip: {e}")
        
        # Navigate to FinishTrip screen
        self.manager.current = "FinishTrip"
        self.manager.transition.direction = "up"

class FinishTrip(Screen):
    def on_enter(self):
        # GPS is now started in StartTripConfirmation screen
        pass
    
    def endTrip(self):
        try:
            app = App.get_running_app()
            if app:
                app.stopGPS()
        except Exception as e:
            Logger.error(f"Failed to stop GPS: {e}")
        
        try:
            now = datetime.now()
            dist = round(getTripDistance(currentTripID), 3) # rounds to 3 decimal places
            tripTime = now - localDBGetTripStart(currentTripID)
            tripFuel = round(dist/mpg, 3)
            localDBRecord(currentTripID, currentCompany, currentCar, 'End Trip', tripTime, dist, tripFuel, '', now)
        except Exception as e:
            Logger.error(f"Failed to end trip: {e}")
    
    def clearCargo(self):
        global currentCargo
        global currentTripID
        self.endTrip()
        currentCargo = ''
        currentTripID = ''
        
class TripStats(Screen):
    def on_enter(self):
        self.refresh_display()
    
    def refresh_display(self):
        """Refresh the trip statistics display with current language"""
        try:
            Logger.info("TripStats refresh_display called")
            Logger.info(f"Current trip ID: {currentTripID}")
            
            if not currentTripID:
                Logger.warning("No current trip ID")
                return
            
            statistics = localDBGetTripStats(currentTripID)
            Logger.info(f"Got statistics: {statistics}")
            
            # Translate destination text if it's a known destination
            destination = str(statistics[0])
            if destination == "Other":
                destination = translator.get_text('other')
            elif destination == "The Highlands":
                destination = translator.get_text('the_highlands')
            elif destination == "Puerto Ayora":
                destination = translator.get_text('puerto_ayora')
            elif destination == "Airport":
                destination = translator.get_text('airport')
            elif destination == "Trip Too Short":
                destination = translator.get_text('trip_too_short')
            
            # Translate passenger/cargo info
            passengers_cargo = str(statistics[1])
            if passengers_cargo == "Trip Too Short":
                passengers_cargo = translator.get_text('trip_too_short')
            
            Logger.info(f"Setting destination to: {destination}")
            self.ids.Destination.text = destination
            self.ids.PassengersCargo.text = passengers_cargo
            self.ids.tripDist.text = "{} {}".format(statistics[2], translator.get_text('km'))
            hours = int(statistics[3].seconds/3600)
            minutes = int((statistics[3].seconds-hours*3600)/60)
            seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
            self.ids.tripTime.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
            self.ids.tripFuel.text = "{} {}".format(statistics[4], translator.get_text('gallons'))
            Logger.info("TripStats refresh_display completed successfully")
        except Exception as e:
            Logger.error(f"Error in refresh_display: {e}")
            import traceback
            Logger.error(traceback.format_exc())
    
    def on_pre_leave(self):
        """Upload trip data to server before leaving screen"""
        try:
            if DBCheckConnection():
                Logger.info("TripStats: Attempting to upload trip data to server")
                localDBDumptoServer()
                Logger.info("TripStats: Trip data uploaded successfully")
            else:
                Logger.warning("TripStats: No connection available, trip data not uploaded")
        except Exception as e:
            Logger.error(f"TripStats on_pre_leave error: {e}")
            import traceback
            Logger.error(traceback.format_exc())
            # Don't crash - just log the error and continue
        
    def clearCurrent(self):
        # DON'T clear the globals here - they're needed for upload in on_pre_leave
        # They will be cleared after upload in localDBDumptoServer
        pass
        
class TripDetailPage(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_trip = None
        self.trip_number = None

    def load_trip_details(self, trip, trip_num):
        """Load and display detailed information for a specific trip"""
        Logger.info(f"Loading trip details for trip #{trip_num}")
        Logger.info(f"Trip data: {trip}")
        self.current_trip = trip
        self.trip_number = trip_num
        
    def on_enter(self):
        """Populate the detail view when entering the screen"""
        from kivy.clock import Clock
        Logger.info("TripDetailPage on_enter called")
        if hasattr(self, 'current_trip'):
            # Use Clock to delay update until screen is fully rendered
            Clock.schedule_once(lambda dt: self.update_display(), 0.1)
        else:
            Logger.warning("No current_trip when entering screen")
    
    def update_display(self):
        """Update all display fields with trip data"""
        try:
            if not hasattr(self, 'current_trip'):
                Logger.warning("No current_trip data available")
                return
            
            if not hasattr(self, 'ids'):
                Logger.warning("IDs not yet available, rescheduling")
                from kivy.clock import Clock
                Clock.schedule_once(lambda dt: self.update_display(), 0.2)
                return
            
            trip = self.current_trip
            trip_num = self.trip_number
            
            Logger.info(f"Updating display for trip #{trip_num}")
            
            # Set trip number
            self.ids.trip_number_label.text = f"{translator.get_text('trip')} #{trip_num}"
            
            # Parse and display timestamps
            try:
                start_time = datetime.fromisoformat(str(trip.get('start_time')).replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(str(trip.get('end_time')).replace('Z', '+00:00'))
                
                start_str = start_time.strftime('%I:%M %p')
                end_str = end_time.strftime('%I:%M %p')
                
                self.ids.time_label.text = f"{start_str} - {end_str}"
                Logger.info(f"Time set to: {start_str} - {end_str}")
            except Exception as e:
                Logger.error(f"Error parsing timestamps: {e}")
                self.ids.time_label.text = 'N/A'
            
            # Display trip details - all with str() to avoid type issues
            self.ids.destination_value.text = str(trip.get('destination', 'N/A'))
            self.ids.starting_point_value.text = str(trip.get('starting_point', 'N/A'))
            
            # Format passengers
            passenger_text = str(trip.get('passenger_type', 'N/A'))
            if trip.get('passenger_count'):
                passenger_text += f" - {trip.get('passenger_count')}"
            self.ids.passengers_value.text = passenger_text
            
            self.ids.cargo_value.text = str(trip.get('cargo_type', 'N/A'))
            self.ids.distance_value.text = f"{float(trip.get('distance_km', 0)):.2f} {translator.get_text('km')}"
            self.ids.duration_value.text = self.format_duration(int(trip.get('duration_seconds', 0)))
            self.ids.fuel_value.text = f"{float(trip.get('fuel_gallons', 0)):.2f} {translator.get_text('gallons')}"
            
            # Display company and car info if available
            if trip.get('company'):
                self.ids.company_value.text = f"Company: {trip.get('company')}"
            if trip.get('car_number'):
                self.ids.car_value.text = f"Car: {trip.get('car_number')}"
            
            Logger.info("Display update complete")
            
        except Exception as e:
            Logger.error(f"CRASH in update_display: {e}")
            import traceback
            Logger.error(traceback.format_exc())
    
    def format_duration(self, seconds):
        """Format duration in seconds to readable string"""
        hours = int(seconds / 3600)
        minutes = int((seconds - hours * 3600) / 60)
        secs = int(seconds - hours * 3600 - minutes * 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"

class Loading(Screen):
    pass
        
class WindowManager(ScreenManager):
    pass

class MainApp(App):
    # Observable property that triggers KV re-evaluation when language changes
    language = StringProperty('es')
    language_button_text = StringProperty('EN')  # Shows which language to switch TO
    
    # Create observable string properties for all translatable text
    welcome_text = StringProperty()
    username_text = StringProperty()
    password_text = StringProperty()
    login_text = StringProperty()
    register_link_text = StringProperty()
    home_text = StringProperty()
    start_trip_text = StringProperty()
    log_out_text = StringProperty()
    get_stats_text = StringProperty()
    back_text = StringProperty()
    next_text = StringProperty()
    done_text = StringProperty()
    complete_text = StringProperty()
    all_trips_text = StringProperty()
    today_text = StringProperty()
    past_text = StringProperty()
    students_text = StringProperty()
    tourists_text = StringProperty()
    locals_text = StringProperty()
    trip_statistics_text = StringProperty()
    destination_text = StringProperty()
    passengers_cargo_text = StringProperty()
    distance_driven_text = StringProperty()
    trip_duration_text = StringProperty()
    estimated_fuel_text = StringProperty()
    home_text2 = StringProperty()
    view_all_trips_text = StringProperty()
    start_next_trip_text = StringProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = translator
        self._last_toggle_time = 0  # Track last toggle time for debouncing
        self.update_text_properties()
    
    def update_text_properties(self):
        """Update all text properties with current language"""
        self.welcome_text = self.translator.get_text('welcome')
        self.username_text = self.translator.get_text('username')
        self.password_text = self.translator.get_text('password')
        self.login_text = self.translator.get_text('login')
        self.register_link_text = self.translator.get_text('register_link')
        self.home_text = self.translator.get_text('home')
        self.start_trip_text = self.translator.get_text('start_trip')
        self.log_out_text = self.translator.get_text('log_out')
        self.get_stats_text = self.translator.get_text('get_stats')
        self.back_text = self.translator.get_text('back')
        self.next_text = self.translator.get_text('next')
        self.done_text = self.translator.get_text('done')
        self.complete_text = self.translator.get_text('complete')
        self.all_trips_text = self.translator.get_text('all_trips')
        self.today_text = self.translator.get_text('today')
        self.past_text = self.translator.get_text('past')
        self.students_text = self.translator.get_text('students')
        self.tourists_text = self.translator.get_text('tourists')
        self.locals_text = self.translator.get_text('locals')
        self.trip_statistics_text = self.translator.get_text('trip_statistics')
        self.destination_text = self.translator.get_text('destination')
        self.passengers_cargo_text = self.translator.get_text('passengers_cargo')
        self.distance_driven_text = self.translator.get_text('distance_driven')
        self.trip_duration_text = self.translator.get_text('trip_duration')
        self.estimated_fuel_text = self.translator.get_text('estimated_fuel')
        self.home_text2 = self.translator.get_text('home')
        self.view_all_trips_text = self.translator.get_text('view_all_trips')
        self.start_next_trip_text = self.translator.get_text('start_next_trip')
    
    def build(self):
        # Load the KV file
        return Builder.load_file('GalapagosCarTracking_translated.kv')
    
    def on_start(self):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            try:
                request_permissions([
                    Permission.INTERNET,
                    Permission.ACCESS_BACKGROUND_LOCATION,
                    Permission.ACCESS_FINE_LOCATION,
                    Permission.ACCESS_COARSE_LOCATION,
                    Permission.WAKE_LOCK
                ])
            except Exception as e:
                Logger.error(f"Permission request failed: {e}")
            # Push layout up when soft keyboard appears so inputs stay visible
            Window.softinput_mode = 'below_target'

        # Handle Android hardware back button (key 27)
        Window.bind(on_keyboard=self.on_keyboard)

        try:
            localDBCreate()
        except Exception as e:
            Logger.error(f"Local DB creation failed: {e}")

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

    def on_keyboard(self, window, key, *largs):
        """Handle Android hardware/gesture back button (keycode 27)"""
        if key == 27:
            current = self.root.current
            # Map each screen to where back should go
            back_nav = {
                'HomeStatsPage':        'Home',
                'IndividualTripsPage':  'HomeStatsPage',
                'TripDetailPage':       'IndividualTripsPage',
                'StartTrip':            'Home',
                'Destination':          'StartTrip',
                'StartingPoint':        'Destination',
                'People':               'StartingPoint',
                'PassengerCount':       'People',
                'Cargo':                'PassengerCount',
                'StartTripConfirmation':'Cargo',
                'Register1':            'Welcome',
                'Register2':            'Register1',
            }
            if current in back_nav:
                self.root.transition.direction = 'down'
                self.root.current = back_nav[current]
                return True  # consume event — don't let Android exit the app
            # Mid-trip screens: block back entirely so driver can't exit by accident
            if current in ('FinishTrip', 'TripStats'):
                return True
        return False
        
    def toggle_language(self):
        """Toggle between English and Spanish with debouncing"""
        # Debounce: ignore if called within 500ms of last toggle
        current_time = time.time()
        if current_time - self._last_toggle_time < 0.5:
            Logger.info(f"[DEBOUNCE] Toggle ignored - too soon ({(current_time - self._last_toggle_time)*1000:.0f}ms since last toggle)")
            return
        
        self._last_toggle_time = current_time
        Logger.info("[TOGGLE] Language toggle starting")
        
        self.translator.toggle_language()
        
        # Update button text to show which language to switch TO
        current_lang = self.translator.get_current_language()
        self.language = current_lang  # triggers KV re-evaluation of all app.language bindings
        self.language_button_text = 'EN' if current_lang == 'es' else 'ES'
        Logger.info(f"[TOGGLE] Language toggled to: {current_lang}, button now shows: {self.language_button_text}")
        
        self.update_text_properties()
        self.update_all_screen_texts()
        self.update_all_images()
        
        # Refresh screens with dynamic content
        try:
            current_screen_name = self.root.current
            Logger.info(f"Current screen: {current_screen_name}")

            if current_screen_name == 'IndividualTripsPage':
                self.root.get_screen('IndividualTripsPage').refresh_current_view()
                Logger.info("Refreshed IndividualTripsPage")
            elif current_screen_name == 'TripStats':
                self.root.get_screen('TripStats').refresh_display()
                Logger.info("TripStats refresh complete")
            elif current_screen_name == 'HomeStatsPage':
                self.root.get_screen('HomeStatsPage').on_pre_enter()
                Logger.info("Refreshed HomeStatsPage")
            elif current_screen_name == 'TripDetailPage':
                self.root.get_screen('TripDetailPage').update_display()
                Logger.info("Refreshed TripDetailPage")
        except Exception as e:
            Logger.error(f"Error refreshing screens: {e}")
            import traceback
            Logger.error(traceback.format_exc())
    
    def update_all_images(self):
        """Update all button background images based on current language"""
        # No image backgrounds needed for the clean design
        # All buttons use solid colors instead of images
        pass
    
    def update_widget_texts(self, widget):
        """Recursively update text properties of widgets"""
        from kivy.uix.label import Label
        from kivy.uix.button import Button
        
        # Update this widget if it has text
        if hasattr(widget, 'text'):
            # Map both English and Spanish text to translation keys
            text_map = {
                # English
                'Welcome!': 'welcome',
                'Username:': 'username', 
                'Password:': 'password',
                'Log In': 'login',
                "Don't have an account? Register Here": 'register_link',
                'Home': 'home',
                'Start Trip': 'start_trip',
                'Log Out': 'log_out',
                'Get Stats': 'get_stats',
                'Back': 'back',
                'Next': 'next',
                'Done': 'done',
                'Complete': 'complete',
                # Spanish
                '¡Bienvenido!': 'welcome',
                'Usuario:': 'username',
                'Contraseña:': 'password',
                'Iniciar Sesión': 'login',
                '¿No tienes cuenta? Regístrate Aquí': 'register_link',
                'Inicio': 'home',
                'Iniciar Viaje': 'start_trip',
                'Cerrar Sesión': 'log_out',
                'Ver Estadísticas': 'get_stats',
                'Atrás': 'back',
                'Siguiente': 'next',
                'Listo': 'done',
                'Completar': 'complete',
                'Please Fill Out the following:': 'fill_out_following',
                'Por favor complete lo siguiente:': 'fill_out_following',
                'Complete your Registration:': 'complete_registration',
                'Complete su Registro:': 'complete_registration',
                'Name:': 'name',
                'Nombre:': 'name',
                'Phone Number:': 'phone_number',
                'Número de Teléfono:': 'phone_number',
                'Car Company:': 'car_company',
                'Compañía de Taxi:': 'car_company',
                'Car Number:': 'car_number',
                'Número de Auto:': 'car_number',
                'Which car are you using?': 'which_car',
                '¿Qué auto está usando?': 'which_car',
                'Where are you going?': 'where_going',
                '¿A dónde va?': 'where_going',
                'Where are you coming from?': 'where_from',
                '¿De dónde viene?': 'where_from',
                'Who are you driving?': 'who_driving',
                '¿A quién está transportando?': 'who_driving',
                'What kind of cargo are they carrying?': 'what_cargo',
                '¿Qué tipo de carga llevan?': 'what_cargo',
                'Statistics for Today': 'statistics_today',
                'Estadísticas de Hoy': 'statistics_today',
                'Number of Trips': 'number_of_trips',
                'Número de Viajes': 'number_of_trips',
                'Kilometers Driven': 'kilometers_driven',
                'Kilómetros Conducidos': 'kilometers_driven',
                'Estimated Total Gas Usage': 'estimated_gas',
                'Uso Total Estimado de Gasolina': 'estimated_gas',
                'Total Driving Time': 'total_time',
                'Tiempo Total de Conducción': 'total_time',
                'Time Spent Between Trips': 'time_between',
                'Tiempo Entre Viajes': 'time_between',
                'Back to Home': 'back_to_home',
                'Volver al Inicio': 'back_to_home',
                # Destination options
                'The Highlands': 'highlands',
                'Parte Alta': 'highlands',
                'Puerto Ayora': 'town',
                'Airport': 'airport',
                'Aeropuerto': 'airport',
                'Other': 'other',
                'Otro': 'other',
                # People options
                'Students': 'students',
                'Estudiantes': 'students',
                'Tourist': 'tourist',
                'Turista': 'tourist',
                'Single Tourist': 'single_tourist',
                'Turista Individual': 'single_tourist',
                'Multiple Tourists': 'multiple_tourists',
                'Múltiples Turistas': 'multiple_tourists',
                'Locals': 'locals',
                'Locales': 'locals',
                'Miscellaneous Passengers': 'misc_passengers',
                'Pasajeros Varios': 'misc_passengers',
                # Passenger Count options
                'How many passengers?': 'passenger_count',
                '¿Cuántos pasajeros?': 'passenger_count',
                '1 Passenger': '1_passenger',
                '1 Pasajero': '1_passenger',
                '2 Passengers': '2_passengers',
                '2 Pasajeros': '2_passengers',
                '3 Passengers': '3_passengers',
                '3 Pasajeros': '3_passengers',
                '4 Passengers': '4_passengers',
                '4 Pasajeros': '4_passengers',
                '5+ Passengers': '5_plus_passengers',
                '5+ Pasajeros': '5_plus_passengers',
                # Cargo options
                'Luggage': 'luggage',
                'Equipaje': 'luggage',
                'Bike': 'bike',
                'Bicicleta': 'bike',
                'Work Equipment': 'work_equipment',
                'Equipo de Trabajo': 'work_equipment',
                'Food and Goods': 'food_goods',
                'Comida y Productos': 'food_goods',
                'Miscellaneous Cargo': 'misc_cargo',
                'Carga Variada': 'misc_cargo',
                # Trip Stats labels
                'Here are the statistics of your latest trip': 'trip_statistics',
                'Aquí están las estadísticas de su último viaje': 'trip_statistics',
                'Destination:': 'destination',
                'Destino:': 'destination',
                'Passengers & Cargo:': 'passengers_cargo',
                'Pasajeros y Carga:': 'passengers_cargo',
                'Distance Driven:': 'distance_driven',
                'Distancia Conducida:': 'distance_driven',
                'Trip Duration:': 'trip_duration',
                'Duración del Viaje:': 'trip_duration',
                'Estimated Fuel Used:': 'estimated_fuel',
                'Combustible Estimado Usado:': 'estimated_fuel',
                'Start Your Next Trip': 'start_next_trip',
                'Iniciar su Próximo Viaje': 'start_next_trip',
                'Trip Too Short': 'trip_too_short',
                'Viaje Muy Corto': 'trip_too_short',
                'Click Complete when you have dropped \n       your passenger and cargo off': 'click_complete',
                'Haga clic en Completar cuando haya dejado \n       a su pasajero y carga': 'click_complete',
                # Additional registration fields
                'Check this Box if you Drive for Another Company:': 'check_another_company',
                'Marque esta casilla si maneja para otra compañía:': 'check_another_company',
                '2nd Car Company:': 'second_car_company',
                '2da Compañía de Taxi:': 'second_car_company',
                '2nd Car Number:': 'second_car_number',
                '2do Número de Auto:': 'second_car_number',
                'Select Company': 'select_company',
                'Seleccionar Compañía': 'select_company',
                'Additional Company:': 'second_car_company',
                'Compañía Adicional:': 'second_car_company'
            }
            
            if widget.text in text_map:
                key = text_map[widget.text]
                widget.text = self.translator.get_text(key)
        
        # Update hint_text if it exists (for TextInput)
        if hasattr(widget, 'hint_text'):
            hint_map = {
                'Username:': 'username',
                'Usuario:': 'username',
                'Password:': 'password',
                'Contraseña:': 'password',
                'Name:': 'name',
                'Nombre:': 'name',
                'Phone Number:': 'phone_number',
                'Número de Teléfono:': 'phone_number',
                'Car Company:': 'car_company',
                'Compañía de Taxi:': 'car_company',
                'Car Number:': 'car_number',
                'Número de Auto:': 'car_number',
                '2nd Car Company:': 'second_car_company',
                '2da Compañía de Taxi:': 'second_car_company',
                '2nd Car Number:': 'second_car_number',
                '2do Número de Auto:': 'second_car_number'
            }
            
            if widget.hint_text in hint_map:
                key = hint_map[widget.hint_text]
                widget.hint_text = self.translator.get_text(key)
        
        # Recursively update children
        if hasattr(widget, 'children'):
            for child in widget.children:
                self.update_widget_texts(child)
    
    def update_all_screen_texts(self):
        """Update text on all screens"""
        for screen in self.root.screens:
            self.update_widget_texts(screen)
    
    def handle_another_company_checkbox(self, active):
        """Handle checkbox state change for additional company field"""
        register2 = self.root.get_screen('Register2')
        if active:
            register2.ids.AdditionalCompanyBox.opacity = 1
            register2.ids.AdditionalCompanyReg.disabled = False
            # Clear the dropdown selection when checkbox is activated
            register2.ids.CompanySpinner.text = self.translator.get_text('select_company')
        else:
            register2.ids.AdditionalCompanyBox.opacity = 0
            register2.ids.AdditionalCompanyReg.disabled = True
            register2.ids.AdditionalCompanyReg.text = ''
    
    def startGPS(self, min_time):
        try:
            gps.configure(on_location = self.update_gps_location)
            gps.start(minTime = min_time*1000, minDistance = 0)
        except NotImplementedError:
            Logger.critical("GPS not implemented on this platform")
    
    def update_gps_location(self, **kwargs):
        global currentlat, currentlon
        currentlat = kwargs['lat']
        currentlon = kwargs['lon']
        now = datetime.now()
        localDBRecord(currentTripID, currentCompany, currentCar, currentDest, currentPass, currentCargo, currentlon, currentlat, now)
    
    def stopGPS(self):
        try:
            gps.stop()
        except NotImplementedError:
            Logger.critical("GPS not implemented on this platform")
        
if __name__ == '__main__':
    MainApp().run()
