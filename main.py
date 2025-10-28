import sqlite3
from kivy.config import Config
# Disable multitouch emulation (removes red dots on screen)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from supabase_config import get_supabase_client, test_connection

# Get Supabase client
supabase = get_supabase_client()
from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import SlideTransition
from kivymd.app import MDApp
from kivy.logger import Logger
from kivy.event import EventDispatcher
from kivy.properties import StringProperty
from datetime import datetime
from datetime import timedelta
from plyer import gps
from math import radians, sin, cos, sqrt, atan2
from translations import translator
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
mpg = 25 # the average miles per gallon of taxi cars
checkFrequency = 10 #seconds
minMph = 2



def DBConnect():
    """Connect to Supabase"""
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
        response = client.table('UserData').delete().neq('username', '').execute()
        Logger.info("Supabase: Cleared UserData table")
    except Exception as e:
        Logger.error(f"Supabase: Error clearing users - {e}")

def DBClearTracking():
    """Clear all tracking data from Supabase"""
    try:
        client = DBConnect()
        response = client.table('TrackingData').delete().neq('tripID', '').execute()
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
        response = client.table('UserData').insert(data).execute()
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
            localDBLogin(
                account['username'], 
                account['password'], 
                account['name'], 
                account['phone'], 
                account['company1'], 
                account['comp1num'], 
                account['company2'], 
                account['comp2num']
            )
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

def DBUploadDataPoint(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    """Upload a tracking data point to Supabase"""
    try:
        client = DBConnect()
        data = {
            'tripID': tripID,
            'company': company,
            'carnum': carnum,
            'destinationXstatus': destination,
            'passengersXtotalTime': str(passengers),
            'cargoXtotalDist': str(cargo),
            'gpslonXworkingFuel': str(gpslon),
            'gpslat': str(gpslat),
            'time': str(time)
        }
        response = client.table('TrackingData').insert(data).execute()
        Logger.info(f"Supabase: Uploaded data point for trip {tripID}")
    except Exception as e:
        Logger.error(f"Supabase: Error uploading data point - {e}")

def DBCheckConnection():
    """Check Supabase connection"""
    try:
        return test_connection()
    except:
        return False

def DBGetDayStats(username, date):
    """Get daily statistics from Supabase"""
    try:
        dayID = f"{username}{date}"
        client = DBConnect()
        response = client.table('TrackingData').select(
            "passengersXtotalTime, cargoXtotalDist, gpslonXworkingFuel, time"
        ).eq('destinationXstatus', 'End Trip').like('tripID', f"%{dayID}%").execute()
        
        trips = response.data
        numTrips = 0
        totalDist = 0
        totalTime = timedelta()
        totalFuel = 0
        endTime = None
        
        for row in trips:
            numTrips += 1
            totalDist += float(row['cargoXtotalDist'])
            t = datetime.strptime(str(row['passengersXtotalTime']), '%H:%M:%S.%f')
            totalTime = totalTime + timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
            totalFuel += float(row['gpslonXworkingFuel'])
            endTime = datetime.strptime(str(row['time']), '%Y-%m-%d %H:%M:%S.%f')
        
        response = client.table('TrackingData').select("time").eq('destinationXstatus', 'Start Trip').like('tripID', f"%{dayID}%").limit(1).execute()
        
        if response.data and len(response.data) > 0:
            dayStart = datetime.strptime(str(response.data[0]['time']), '%Y-%m-%d %H:%M:%S.%f')
            if endTime:
                idleTime = endTime - dayStart - totalTime
            else:
                idleTime = timedelta()
        else:
            idleTime = timedelta()
        
        return [numTrips, totalDist, totalFuel, totalTime, idleTime]
    except Exception as e:
        Logger.error(f"Supabase: Error getting day stats - {e}")
        return [0, 0, 0, timedelta(), timedelta()]
        
    

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
    localDBShowAll()

def localDBDumptoServer():
    [cursor, localdb] = localDBConnect()
    cursor.execute("SELECT * FROM tripData")
    records = cursor.fetchall()
    for row in records:
        DBUploadDataPoint(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
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
    global lon1, lat1, lon2, lat2
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
            R = 3958.8 # radius of earth in miles
            d = R * c
            if(d >= (minMph*checkFrequency/3600)): # prevents movements smaller than minMph average speed to not be recorded 
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
                self.ids.NumberOfTrips.text = "{} Trips".format(statistics[0])
                self.ids.MilesDriven.text = "{} Miles".format(statistics[1])
                self.ids.EstimatedGas.text = "{} Gallons".format(statistics[2])
                hours = int(statistics[3].seconds/3600)
                minutes = int((statistics[3].seconds-hours*3600)/60)
                seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
                self.ids.TotalTime.text = '{} Hours, {} Minutes, {} Seconds'.format(hours, minutes, seconds)
                hours = int(statistics[4].seconds/3600)
                minutes = int((statistics[4].seconds-hours*3600)/60)
                seconds = int(statistics[4].seconds - hours*3600 - minutes*60)
                self.ids.TimeBetween.text = '{} Hours, {} Minutes, {} Seconds'.format(hours, minutes, seconds)
            except:
                self.ids.NumberOfTrips.text = "No Data Available"
                self.ids.MilesDriven.text = "No Data Available"
                self.ids.EstimatedGas.text = "No Data Available"
                self.ids.TotalTime.text = "No Data Available"
                self.ids.TimeBetween.text = "No Data Available"
        else:
            self.ids.NumberOfTrips.text = "Connection Required"
            self.ids.MilesDriven.text = "Connection Required"
            self.ids.EstimatedGas.text = "Connection Required"
            self.ids.TotalTime.text = "Connection Required"
            self.ids.TimeBetween.text = "Connection Required"

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
            self.manager.current = "Welcome"# sets the window to the window with the name given
            self.manager.transition.direction = "up" # sets transition direction
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
    
class People(Screen):
    def setPass(self, people):
        global currentPass
        currentPass = people
        
    def clearDest(self):
        global currentDest
        currentDest = ''

class Cargo(Screen):
    def setCargo(self, cargo):
        global currentCargo
        currentCargo = cargo
        
    def clearPeople(self):
        global currentPass
        currentPass = ''

class FinishTrip(Screen):
    def on_enter(self):
        try:
            MainApp().startGPS(checkFrequency)
        except:
            Logger.critical("GPS Not Enabled on This Device")
        startTrip()
    
    def endTrip(self):
        try:
            MainApp().stopGPS()
        except:
            Logger.critical("GPS Not Set Up on This Device")
        now = datetime.now()
        dist = round(getTripDistance(currentTripID),3) # rounds to the nearest 5ft
        tripTime = now - localDBGetTripStart(currentTripID)
        tripFuel = round(dist/mpg, 3)
        localDBRecord(currentTripID, currentCompany, currentCar, 'End Trip', tripTime, dist, tripFuel, '', now)
    
    def clearCargo(self):
        global currentCargo
        global currentTripID
        self.endTrip()
        currentCargo = ''
        currentTripID = ''
        
class TripStats(Screen):
    def on_enter(self):
        statistics = localDBGetTripStats(currentTripID)
        
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
        
        self.ids.Destination.text = destination
        self.ids.PassengersCargo.text = str(statistics[1])
        self.ids.tripDist.text = "{} Miles".format(statistics[2])
        hours = int(statistics[3].seconds/3600)
        minutes = int((statistics[3].seconds-hours*3600)/60)
        seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
        self.ids.tripTime.text = '{} Hours, {} Minutes, {} Seconds'.format(hours, minutes, seconds)
        self.ids.tripFuel.text = "{} Gallons".format(statistics[4])
    
    def on_pre_leave(self):
        if(DBCheckConnection()):
            localDBDumptoServer()
        
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

class MainApp(App):
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
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.translator = translator
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
    
    def build(self):
        # Load the KV file
        return Builder.load_file('GalapagosCarTracking_translated.kv')
    
    def on_start(self):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.ACCESS_BACKGROUND_LOCATION, Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        localDBCreate()
        localDBLogin('testUser', 'testPassword', 'Test User', '1234567890', 'Company1', '1', 'Company2', '2') # DELETE ONCE LOGIN IS POSSIBLE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
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
            if hasattr(self.root, 'get_screen'):
                finish_screen = self.root.get_screen("FinishTrip")
                if hasattr(finish_screen, 'endTrip'):
                    finish_screen.endTrip()
        except Exception as e:
            Logger.info(f"Error during app close: {e}")
        return True
        
    def startGPS(self, seconds):
        try:
            gps.configure(on_location=self.on_gps_location,on_status=None)
            gps.start(seconds*1000,0) # gathers location every 'seconds' seconds minimum and 0 meters minimum
        except:
            Logger.critical("GPS Not On This Device")
            
    def stopGPS(self):
        gps.stop()
        global currentlat
        global currentlon
        currentlat = 0
        currentlon = 0
    
    def handle_checkbox_active(self, is_checked):
        if is_checked:
            # The CheckBox is checked, show the additional questions or elements
            self.root.get_screen('Register2').ids.CarCompanyTwo.opacity = 1
            self.root.get_screen('Register2').ids.Company2Reg.opacity = 1
            self.root.get_screen('Register2').ids.CarNumberTwo.opacity = 1
            self.root.get_screen('Register2').ids.Car2NumReg.opacity = 1
        else:
            # The CheckBox is unchecked, hide the additional questions or elements
            self.root.get_screen('Register2').ids.CarCompanyTwo.opacity = 0
            self.root.get_screen('Register2').ids.Company2Reg.opacity = 0
            self.root.get_screen('Register2').ids.CarNumberTwo.opacity = 0
            self.root.get_screen('Register2').ids.Car2NumReg.opacity = 0   

    def get_image_path(self, image_name):
        """Get the correct image path based on current language"""
        return get_image_path(image_name)
    
    def toggle_language(self):
        """Toggle between English and Spanish and update all UI text"""
        translator.toggle_language()
        self.update_all_screen_texts()
        self.update_all_images()
    
    def update_all_screen_texts(self):
        """Update text on all screens by directly modifying widget text properties"""
        # Update Welcome screen
        try:
            welcome_screen = self.root.get_screen('Welcome')
            # Find and update all labels and buttons with translation keys
            self.update_widget_texts(welcome_screen)
        except:
            pass
        
        # Update Home screen
        try:
            home_screen = self.root.get_screen('Home')
            self.update_widget_texts(home_screen)
        except:
            pass
            
        # Update all other screens
        for screen_name in ['Register1', 'Register2', 'HomeStatsPage', 'StartTrip', 'Destination', 'People', 'Cargo', 'FinishTrip', 'TripStats']:
            try:
                screen = self.root.get_screen(screen_name)
                self.update_widget_texts(screen)
            except:
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
                'Who are you driving?': 'who_driving',
                '¿A quién está transportando?': 'who_driving',
                'What kind of cargo are they carrying?': 'what_cargo',
                '¿Qué tipo de carga llevan?': 'what_cargo',
                'Statistics for Today': 'statistics_today',
                'Estadísticas de Hoy': 'statistics_today',
                'Number of Trips': 'number_of_trips',
                'Número de Viajes': 'number_of_trips',
                'Miles Driven': 'miles_driven',
                'Millas Conducidas': 'miles_driven',
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
                'Single Tourist': 'single_tourist',
                'Turista Individual': 'single_tourist',
                'Multiple Tourists': 'multiple_tourists',
                'Múltiples Turistas': 'multiple_tourists',
                'Locals': 'locals',
                'Locales': 'locals',
                'Miscellaneous Passengers': 'misc_passengers',
                'Pasajeros Varios': 'misc_passengers',
                # Cargo options
                'Luggage': 'luggage',
                'Equipaje': 'luggage',
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
                '2do Número de Auto:': 'second_car_number'
            }
            
            current_text = str(widget.text).strip()
            if current_text in text_map:
                widget.text = translator.get_text(text_map[current_text])
        
        # Recursively update children
        if hasattr(widget, 'children'):
            for child in widget.children:
                self.update_widget_texts(child)
    
    def update_all_images(self):
        """Update all button background images based on current language"""
        # No image backgrounds needed for the clean design
        # All buttons use solid colors instead of images
        pass
    
    def update_all_text(self):
        """Update all text elements in the UI with current language"""
        self.toggle_language()


# run the application
if __name__=='__main__':
    MainApp().run()
