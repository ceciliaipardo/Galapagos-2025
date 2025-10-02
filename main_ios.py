import sqlite3
from kivy.app import App
from kivy.lang import Builder
from kivy.utils import platform
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.checkbox import CheckBox
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import NoTransition
from kivy.uix.screenmanager import SlideTransition
from kivy.logger import Logger
from datetime import datetime
from datetime import timedelta
from plyer import gps
from math import radians, sin, cos, sqrt, atan2
import json
import os

# iOS-specific imports
try:
    import requests
except ImportError:
    requests = None
    Logger.warning("Requests not available - remote database features disabled")

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

# iOS Configuration
API_BASE_URL = "https://your-api-server.com/api"  # Replace with your actual API endpoint
USE_LOCAL_ONLY = True  # Set to False when you have a working API

def APIRequest(endpoint, method="GET", data=None):
    """Make API requests to replace MySQL functionality"""
    if not requests or USE_LOCAL_ONLY:
        Logger.warning("API requests disabled - using local storage only")
        return None
    
    try:
        url = f"{API_BASE_URL}/{endpoint}"
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        elif method == "PUT":
            response = requests.put(url, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            Logger.error(f"API request failed: {response.status_code}")
            return None
    except Exception as e:
        Logger.error(f"API request error: {e}")
        return None

def DBConnect():
    """iOS version - uses API instead of direct MySQL connection"""
    # This function is kept for compatibility but will use API calls
    Logger.info("Using API connection instead of direct MySQL")
    return [None, None]

def DBCreate():
    """iOS version - API handles database creation"""
    Logger.info("Database creation handled by API server")
    pass

def DBClearUsers():
    """iOS version - API call to clear users"""
    if not USE_LOCAL_ONLY:
        APIRequest("users/clear", "POST")

def DBClearTracking():
    """iOS version - API call to clear tracking data"""
    if not USE_LOCAL_ONLY:
        APIRequest("tracking/clear", "POST")

def DBDelete():
    """iOS version - API call to delete tables"""
    if not USE_LOCAL_ONLY:
        APIRequest("database/delete", "POST")

def DBShowAll():
    """iOS version - API call to show all data"""
    if not USE_LOCAL_ONLY:
        users = APIRequest("users")
        tracking = APIRequest("tracking")
        if users:
            print("User Data:", users)
        if tracking:
            print("Tracking Data:", tracking)
 
def DBCheckUsernameExists(username):
    """iOS version - API call to check username"""
    if username == '':
        return "Username Invalid"
    
    if USE_LOCAL_ONLY:
        # Use local database for checking
        [cursor, localdb] = localDBConnect()
        query = "SELECT * FROM accountData WHERE username = ?"
        cursor.execute(query, (username,))
        test = cursor.fetchone()
        localdb.close()
        
        if test:
            return "This username is already in use. Please choose another username."
        else:
            return "Valid"
    else:
        result = APIRequest(f"users/check/{username}")
        if result and result.get('exists'):
            return "This username is already in use. Please choose another username."
        return "Valid"

def DBCheckPhoneExists(phone):
    """iOS version - API call to check phone"""
    try:
        int(phone)
    except: 
        return "Phone Number Invalid"
    
    if USE_LOCAL_ONLY:
        return "Valid"  # Skip phone check for local mode
    else:
        result = APIRequest(f"users/check-phone/{phone}")
        if result and result.get('exists'):
            return "This phone number is already in use"
        return "Valid"
    
def DBRegister(username, password, name, phone, company1, comp1num, company2, comp2num):
    """iOS version - API call to register user"""
    if USE_LOCAL_ONLY:
        # Store in local database
        localDBRegister(username, password, name, phone, company1, comp1num, company2, comp2num)
    else:
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
        APIRequest("users/register", "POST", data)

def DBLogin(username, password):
    """iOS version - API call to login"""
    if USE_LOCAL_ONLY:
        return localDBLogin(username, password)
    else:
        data = {'username': username, 'password': password}
        result = APIRequest("users/login", "POST", data)
        if result and result.get('success'):
            account = result.get('user')
            localDBStoreAccount(account)
            return True
        return False

def DBPullUserData():
    """iOS version - get user data from local storage"""
    return localDBPullAccountData()

def DBUploadDataPoint(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    """iOS version - API call to upload data point"""
    if USE_LOCAL_ONLY:
        localDBRecord(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time)
    else:
        data = {
            'tripID': tripID,
            'company': company,
            'carnum': carnum,
            'destination': destination,
            'passengers': passengers,
            'cargo': cargo,
            'gpslon': gpslon,
            'gpslat': gpslat,
            'time': str(time)
        }
        APIRequest("tracking/upload", "POST", data)

def DBCheckConnection():
    """iOS version - check API connection"""
    if USE_LOCAL_ONLY:
        return True
    else:
        result = APIRequest("health")
        return result is not None

def DBGetDayStats(username, date):
    """iOS version - API call to get day stats"""
    if USE_LOCAL_ONLY:
        return localDBGetDayStats(username, date)
    else:
        result = APIRequest(f"stats/day/{username}/{date}")
        if result:
            return [
                result.get('numTrips', 0),
                result.get('totalDist', 0),
                result.get('totalFuel', 0),
                timedelta(seconds=result.get('totalTime', 0)),
                timedelta(seconds=result.get('idleTime', 0))
            ]
        return [0, 0, 0, timedelta(), timedelta()]

def localDBConnect():
    """Connect to local SQLite database"""
    db_path = os.path.join(os.path.expanduser('~'), 'Documents', 'local_db.db')
    localdb = sqlite3.connect(db_path)
    cursor = localdb.cursor()
    return [cursor, localdb]

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

def localDBDumptoServer():
    """Upload local data to server"""
    if USE_LOCAL_ONLY:
        Logger.info("Local only mode - not uploading to server")
        return
        
    [cursor, localdb] = localDBConnect()
    cursor.execute("SELECT * FROM tripData")
    records = cursor.fetchall()
    for row in records:
        DBUploadDataPoint(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8])
    localdb.commit()
    localdb.close()
    localDBClearTrip()

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
    """Get day statistics from local database"""
    dayID = "{}{}".format(username, date)
    [cursor, localdb] = localDBConnect()
    query = "SELECT passengersXtotalTime,cargoXtotalDist,gpslonXworkingFuel,time FROM tripData WHERE destinationXstatus = 'End Trip' AND tripID LIKE ?"
    cursor.execute(query, (f"%{dayID}%",))
    trips = cursor.fetchall()
    
    numTrips = 0
    totalDist = 0
    totalTime = timedelta()
    totalFuel = 0
    
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
            idleTime = endTime - dayStart - totalTime
        else:
            idleTime = timedelta()
    else:
        idleTime = timedelta()
    
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

# Screen classes remain the same as original main.py
class Welcome(Screen):            
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
                self.ids.Incorrect.text = 'Invalid Username or Password'
        else:
            self.ids.Incorrect.text = 'Connection Required to Log In'

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
                self.manager.current = "Register2"
                self.manager.transition.direction = "up"
        else:
            self.ids.Incorrect.text = "Connection Required to Register New Account"

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
            self.manager.current = "Welcome"
            self.manager.transition.direction = "up"
        else:
            self.ids.Incorrect.text = "Connection Required to Register New Account"

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
        dist = round(getTripDistance(currentTripID),3)
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
        self.ids.Destination.text = str(statistics[0])
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
    def build(self):
        return kv
    
    def on_start(self):
        # iOS permissions are handled differently
        if platform == "ios":
            Logger.info("iOS platform detected")
        elif platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.ACCESS_BACKGROUND_LOCATION, Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        
        localDBCreate()
        onLaunch()
        kv.transition = NoTransition()
        
        try:
            account_data = localDBPullAccountData()
            if account_data and account_data[0] != '':
                kv.current = "Home"
            else:
                kv.current = "Welcome"
        except:
            kv.current = "Welcome"
        
        kv.transition = SlideTransition()
        
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

# Load the kivy file
kv = Builder.load_file('GalapagosCarTracking.kv')

# Run the application
if __name__=='__main__':
    MainApp().run()
