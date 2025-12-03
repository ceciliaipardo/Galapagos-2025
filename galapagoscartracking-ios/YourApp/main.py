import sqlite3
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
        # Insert already returns response in newer Supabase client
        response = client.table('TrackingData').insert(data)
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
        passengers = translator.get_text('trip_too_short')
        destination = translator.get_text('trip_too_short')
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
            R = 6371 # radius of earth in kilometers
            d = R * c
            if(d >= (minMph*checkFrequency/3600)): # prevents movements smaller than minMph average speed to not be recorded 
                totalDist += d
            lon1 = lon2
            lat1 = lat2
        rowNum += 1
    return totalDist



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
                    # Check for Register link (this one was staying Spanish)
                    elif "Don't have an account" in widget.text or 'tienes cuenta' in widget.text or 'Regístrate' in widget.text:
                        widget.text = translator.get_text('register_link')
            
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
                # Category label: Total Time (this one is "Total Driving Time")
                elif 'Total Driving Time' in widget.text or 'Tiempo Total de Conducción' in widget.text:
                    widget.text = translator.get_text('total_time')
                # Category label: Time Between Trips
                elif 'Time Spent Between Trips' in widget.text or 'Tiempo Entre Viajes' in widget.text:
                    widget.text = translator.get_text('time_between')
        
        # Now update data values
        if(DBCheckConnection()):
            try:
                statistics = DBGetDayStats(currentUser, datetime.today().strftime("%Y%m%d"))
                self.ids.NumberOfTrips.text = "{} {}".format(statistics[0], translator.get_text('trips'))
                self.ids.MilesDriven.text = "{} {}".format(statistics[1], translator.get_text('miles'))
                self.ids.EstimatedGas.text = "{} {}".format(statistics[2], translator.get_text('gallons'))
                hours = int(statistics[3].seconds/3600)
                minutes = int((statistics[3].seconds-hours*3600)/60)
                seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
                self.ids.TotalTime.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
                hours = int(statistics[4].seconds/3600)
                minutes = int((statistics[4].seconds-hours*3600)/60)
                seconds = int(statistics[4].seconds - hours*3600 - minutes*60)
                self.ids.TimeBetween.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
            except:
                self.ids.NumberOfTrips.text = translator.get_text('no_data_available')
                self.ids.MilesDriven.text = translator.get_text('no_data_available')
                self.ids.EstimatedGas.text = translator.get_text('no_data_available')
                self.ids.TotalTime.text = translator.get_text('no_data_available')
                self.ids.TimeBetween.text = translator.get_text('no_data_available')
        else:
            self.ids.NumberOfTrips.text = translator.get_text('connection_required')
            self.ids.MilesDriven.text = translator.get_text('connection_required')
            self.ids.EstimatedGas.text = translator.get_text('connection_required')
            self.ids.TotalTime.text = translator.get_text('connection_required')
            self.ids.TimeBetween.text = translator.get_text('connection_required')

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
                self.manager.current = "Register2" # sets the window to the window with the name given
                self.manager.transition.direction = "up" # sets transition direction    
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
            self.manager.current = "Welcome"# sets the window to the window with the name given
            self.manager.transition.direction = "up" # sets transition direction
        else:
            self.ids.Incorrect.text = translator.get_text('connection_required_register')

class StartTrip(Screen):
    def on_pre_enter(self):
        # Update screen title and button text
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label':
                # Update "Which Car?" / "Qué auto está usando?" title
                if hasattr(widget, 'text'):
                    widget.text = translator.get_text('which_car')
        
        userData = localDBPullAccountData()
        if userData is None:
            # If no user data, use default placeholder text
            self.ids.car1.text = translator.get_text('company_1')
            self.ids.car2.text = translator.get_text('company_2')
            self.ids.car2.disabled = True
            self.ids.car2.opacity = 0
            return
            
        # Use translated company names for display - if the database has placeholder values, translate them
        company1_name = translator.get_text('company_1') if userData[4] in ['Company1', 'Company 1'] else userData[4]
        company2_name = translator.get_text('company_2') if userData[6] in ['Company2', 'Company 2'] else userData[6]
        
        self.ids.car1.text = company1_name
        self.ids.car2.text = company2_name
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
        if userData is not None:
            currentCompany = userData[2*companyNum+2]
            currentCar = userData[2*companyNum+3]
        else:
            # Use default values if no user data
            currentCompany = f'Company{companyNum}'
            currentCar = str(companyNum)
        
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
    def on_pre_enter(self):
        # Update all text to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label':
                widget.text = translator.get_text('where_going')
            elif widget.__class__.__name__ == 'Button' and hasattr(widget, 'text') and widget.text:
                if widget.text not in ['←', '', 'EN', 'ES']:
                    # Check for Highlands/Parte Alta (case-insensitive, handle both variations)
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
        dist = round(getTripDistance(currentTripID),3) # rounds to the nearest 5ft
        tripTime = now - localDBGetTripStart(currentTripID)
        tripFuel = round(dist/mpg, 3)
        # Convert tripTime to string for SQLite
        localDBRecord(currentTripID, currentCompany, currentCar, 'End Trip', str(tripTime), dist, tripFuel, '', now)
    
    def clearCargo(self):
        global currentCargo
        global currentTripID
        self.endTrip()
        currentCargo = ''
        currentTripID = ''
        
class TripStats(Screen):
    def on_pre_enter(self):
        # Update all static labels and buttons to current language
        for widget in self.walk():
            if widget.__class__.__name__ == 'Label' and hasattr(widget, 'text') and widget.text:
                # Check each possible label heading by ID or by text content
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
        statistics = localDBGetTripStats(currentTripID)
        self.ids.Destination.text = str(statistics[0])
        self.ids.PassengersCargo.text = str(statistics[1])
        self.ids.tripDist.text = "{} {}".format(statistics[2], translator.get_text('miles'))
        hours = int(statistics[3].seconds/3600)
        minutes = int((statistics[3].seconds-hours*3600)/60)
        seconds = int(statistics[3].seconds - hours*3600 - minutes*60)
        self.ids.tripTime.text = '{} {}, {} {}, {} {}'.format(hours, translator.get_text('hours'), minutes, translator.get_text('minutes'), seconds, translator.get_text('seconds'))
        self.ids.tripFuel.text = "{} {}".format(statistics[4], translator.get_text('gallons'))
    
    def on_pre_leave(self):
        if(DBCheckConnection()):
            localDBDumptoServer()
        
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
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.INTERNET, Permission.ACCESS_BACKGROUND_LOCATION, Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        localDBCreate()
        localDBLogin('testUser', 'testPassword', 'Test User', '1234567890', 'Company1', '1', 'Company2', '2') # DELETE ONCE LOGIN IS POSSIBLE - Company1/2 are placeholders that get translated to "Company 1"/"Compañía 1" etc.
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
        """Toggle between English and Spanish"""
        # Toggle language
        translator.toggle_language()
        self.language = translator.get_current_language()
        Logger.info(f"Language toggled to: {self.language}")
        
        # Refresh current screen
        try:
            current_screen = self.root.current
            screen_obj = self.root.get_screen(current_screen)
            if hasattr(screen_obj, 'on_pre_enter'):
                screen_obj.on_pre_enter()
                Logger.info(f"Refreshed {current_screen} screen after language change")
        except Exception as e:
            Logger.error(f"Error refreshing screen: {e}")
    


# run the application
if __name__=='__main__':
    MainApp().run()
