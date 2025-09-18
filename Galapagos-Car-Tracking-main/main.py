import mysql.connector
import sqlite3
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
from datetime import datetime, timedelta
from plyer import gps
from math import radians, sin, cos, sqrt, atan2


# -----------------------------
# GLOBAL VARIABLES
# -----------------------------
currentUser = ''
currentCompany = ''
currentCar = ''
currentDest = ''
currentPass = ''
currentCargo = ''
currentlat = 0
currentlon = 0
currentTripID = ''
mpg = 25  # average miles per gallon
checkFrequency = 10  # seconds
minMph = 2
is_spanish = False  # Language toggle flag - Start with English, allow toggle to Spanish

# -----------------------------
# TRANSLATION DICTIONARIES
# -----------------------------
translations = {
    'english': {
        'welcome': 'Welcome!',
        'username': 'Username:',
        'password': 'Password:',
        'login': 'Log In',
        'register_link': "Don't have an account? Register Here",
        'invalid_login': 'Invalid Username or Password',
        'home': 'Home',
        'start_trip': 'Start Trip',
        'log_out': 'Log Out',
        'get_stats': 'Get Stats',
        'statistics_today': 'Statistics for Today',
        'number_of_trips': 'Number of Trips',
        'miles_driven': 'Miles Driven',
        'estimated_gas': 'Estimated Total Gas Usage',
        'total_time': 'Total Driving Time',
        'time_between': 'Time Spent Between Trips',
        'back_to_home': 'Back to Home',
        'which_car': 'Which car are you using?',
        'car1_company1': 'Car 1, Company 1',
        'car2_company2': 'Car 2, Company 2',
        'where_going': 'Where are you going?',
        'who_driving': 'Who are you driving?',
        'what_cargo': 'What kind of cargo are they carrying?',
        'complete_trip': 'Click Complete when you have dropped \n       your passenger and cargo off',
        'complete': 'Complete',
        'trip_stats': 'Here are the statistics of your latest trip',
        'destination': 'Destination:',
        'passengers_cargo': 'Passengers & Cargo:',
        'distance_driven': 'Distance Driven:',
        'trip_duration': 'Trip Duration:',
        'estimated_fuel': 'Estimated Fuel Used:',
        'start_next_trip': 'Start Your Next Trip',
        'back': 'Back',
        'next': 'Next',
        'done': 'Done',
        'name': 'Name:',
        'phone_number': 'Phone Number:',
        'car_company': 'Car Company:',
        'car_number': 'Car Number:',
        'fill_out': 'Please Fill Out the following:',
        'complete_registration': 'Complete your Registration:',
        'second_company_check': 'Check this Box if you Drive for Another Company:',
        'second_car_company': '2nd Car Company:',
        'second_car_number': '2nd Car Number:',
        'students': 'Students',
        'single_tourist': 'Single Tourist',
        'multiple_tourists': 'Multiple Tourists',
        'locals': 'Locals',
        'misc_passengers': 'Miscellaneous Passengers',
        'luggage': 'Luggage',
        'work_equipment': 'Work Equipment',
        'food_goods': 'Food and Goods',
        'misc_cargo': 'Miscellaneous Cargo',
        'highlands': 'The Highlands',
        'puerto_ayora': 'Puerto Ayora',
        'airport': 'Airport',
        'other': 'Other',
        'language': 'Español'
    },
    'spanish': {
        'welcome': '¡Bienvenido!',
        'username': 'Usuario:',
        'password': 'Contraseña:',
        'login': 'Iniciar Sesión',
        'register_link': "¿No tienes cuenta? Regístrate Aquí",
        'invalid_login': 'Usuario o Contraseña Inválidos',
        'home': 'Inicio',
        'start_trip': 'Iniciar Viaje',
        'log_out': 'Cerrar Sesión',
        'get_stats': 'Ver Estadísticas',
        'statistics_today': 'Estadísticas de Hoy',
        'number_of_trips': 'Número de Viajes',
        'miles_driven': 'Millas Conducidas',
        'estimated_gas': 'Uso Total Estimado de Gasolina',
        'total_time': 'Tiempo Total de Conducción',
        'time_between': 'Tiempo Entre Viajes',
        'back_to_home': 'Volver al Inicio',
        'which_car': '¿Qué carro estás usando?',
        'car1_company1': 'Carro 1, Compañía 1',
        'car2_company2': 'Carro 2, Compañía 2',
        'where_going': '¿A dónde vas?',
        'who_driving': '¿A quién estás llevando?',
        'what_cargo': '¿Qué tipo de carga llevan?',
        'complete_trip': 'Haz clic en Completar cuando hayas dejado \n       a tu pasajero y carga',
        'complete': 'Completar',
        'trip_stats': 'Aquí están las estadísticas de tu último viaje',
        'destination': 'Destino:',
        'passengers_cargo': 'Pasajeros y Carga:',
        'distance_driven': 'Distancia Conducida:',
        'trip_duration': 'Duración del Viaje:',
        'estimated_fuel': 'Combustible Estimado Usado:',
        'start_next_trip': 'Iniciar tu Próximo Viaje',
        'back': 'Atrás',
        'next': 'Siguiente',
        'done': 'Hecho',
        'name': 'Nombre:',
        'phone_number': 'Número de Teléfono:',
        'car_company': 'Compañía de Carros:',
        'car_number': 'Número de Carro:',
        'fill_out': 'Por favor completa lo siguiente:',
        'complete_registration': 'Completa tu Registro:',
        'second_company_check': 'Marca esta casilla si conduces para otra compañía:',
        'second_car_company': '2da Compañía de Carros:',
        'second_car_number': '2do Número de Carro:',
        'students': 'Estudiantes',
        'single_tourist': 'Turista Individual',
        'multiple_tourists': 'Múltiples Turistas',
        'locals': 'Locales',
        'misc_passengers': 'Pasajeros Varios',
        'luggage': 'Equipaje',
        'work_equipment': 'Equipo de Trabajo',
        'food_goods': 'Comida y Productos',
        'misc_cargo': 'Carga Variada',
        'highlands': 'Las Tierras Altas',
        'puerto_ayora': 'Puerto Ayora',
        'airport': 'Aeropuerto',
        'other': 'Otro',
        'language': 'English'
    }
}

def get_text(key):
    """Get translated text based on current language setting"""
    global is_spanish
    lang = 'spanish' if is_spanish else 'english'
    return translations[lang].get(key, key)

def toggle_language():
    """Toggle between English and Spanish"""
    global is_spanish
    is_spanish = not is_spanish
    return is_spanish


# -----------------------------
# DATABASE (CLOUD MYSQL - RAILWAY)
# -----------------------------
def DBConnect():
    mydb = mysql.connector.connect(
        host="centerbeam.proxy.rlwy.net",   # Railway host
        user="root",                        # Railway user
        password="YOUR_RAILWAY_PASSWORD",   # 🔑 replace with your real Railway password
        database="railway",                 # Railway DB name
        port=20079                          # Railway port
    )
    cursor = mydb.cursor()
    return [cursor, mydb]


def DBCreate():
    [cursor, mydb] = DBConnect()
    # UserData table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS UserData(
            username VARCHAR(20),
            password VARCHAR(20),
            name VARCHAR(20),
            phone VARCHAR(15),
            company1 VARCHAR(20),
            comp1num VARCHAR(5),
            company2 VARCHAR(20),
            comp2num VARCHAR(5)
        )
    """)
    # TrackingData table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS TrackingData(
            tripID VARCHAR(40),
            company VARCHAR(20),
            carnum VARCHAR(5),
            destinationXstatus VARCHAR(20),
            passengersXtotalTime VARCHAR(20),
            cargoXtotalDist VARCHAR(20),
            gpslonXworkingFuel VARCHAR(20),
            gpslat VARCHAR(20),
            time VARCHAR(30)
        )
    """)
    mydb.commit()
    mydb.close()


# -----------------------------
# LOCAL SQLITE (offline fallback)
# -----------------------------
def localDBConnect():
    localdb = sqlite3.connect('local_db.db')
    cursor = localdb.cursor()
    return [cursor, localdb]


def localDBCreate():
    [cursor, localdb] = localDBConnect()
    cursor.execute("""CREATE TABLE IF NOT EXISTS accountData(
        username VARCHAR(20),
        password VARCHAR(20),
        name VARCHAR(20),
        phone VARCHAR(15),
        company1 VARCHAR(20),
        comp1num VARCHAR(5),
        company2 VARCHAR(20),
        comp2num VARCHAR(5)
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS tripData(
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


# -----------------------------
# KIVY SCREENS
# -----------------------------
class Welcome(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def logIn(self, username, password):
        if DBLogin(username, password):
            self.ids.Incorrect.text = ''
            self.manager.current = "Home"
            self.manager.transition.direction = "up"
            global currentUser
            currentUser = str(username)
        else:
            self.ids.Incorrect.text = get_text('invalid_login')
    
    def toggle_language(self):
        """Toggle language and update all texts across all screens"""
        toggle_language()
        # Update all screens in the app
        app = App.get_running_app()
        app.update_all_screen_texts()
    
    def update_texts(self):
        """Update all text elements in the Welcome screen"""
        self.ids.welcome_label.text = get_text('welcome')
        self.ids.username_label.text = get_text('username')
        self.ids.password_label.text = get_text('password')
        self.ids.login_btn.text = get_text('login')
        self.ids.register_btn.text = get_text('register_link')
        self.ids.language_btn.text = get_text('language')


class Home(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def logOut(self):
        global currentUser
        currentUser = ''
        localDBLogOut()
    
    def toggle_language(self):
        """Toggle language and update all texts across all screens"""
        toggle_language()
        # Update all screens in the app
        app = App.get_running_app()
        app.update_all_screen_texts()
    
    def update_texts(self):
        """Update all text elements in the Home screen"""
        self.ids.home_label.text = get_text('home')
        self.ids.start_trip_btn.text = get_text('start_trip')
        self.ids.logout_btn.text = get_text('log_out')
        self.ids.stats_btn.text = get_text('get_stats')
        self.ids.language_btn.text = get_text('language')


class HomeStatsPage(Screen):
    pass


class StartTrip(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def selectCar(self, car_num):
        # Implementation for car selection
        pass
    
    def clearCar(self):
        # Implementation to clear car selection
        pass
    
    def update_texts(self):
        """Update all text elements in the StartTrip screen"""
        # Update the main question label
        for child in self.walk():
            if hasattr(child, 'text'):
                if child.text == 'Which car are you using?':
                    child.text = get_text('which_car')
                elif child.text == 'Car 1, Company 1':
                    child.text = get_text('car1_company1')
                elif child.text == 'Car 2, Company 2':
                    child.text = get_text('car2_company2')
                elif child.text == 'Home':
                    child.text = get_text('home')


class Destination(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def setDest(self, destination):
        # Implementation to set destination
        pass
    
    def clearCar(self):
        # Implementation to clear car selection
        pass
    
    def update_texts(self):
        """Update all text elements in the Destination screen"""
        for child in self.walk():
            if hasattr(child, 'text'):
                if child.text == 'Where are you going?':
                    child.text = get_text('where_going')
                elif child.text == 'Back':
                    child.text = get_text('back')


class Register1(Screen):
    def checkRegPg1(self, username, phone):
        # Implementation for registration page 1 validation
        # For now, just proceed to next screen
        self.manager.current = "Register2"
        self.manager.transition.direction = "up"


class Register2(Screen):
    def register(self, username, password, name, phone, company1, car1num, company2, car2num):
        # Implementation for user registration
        # For now, just go back to welcome screen
        self.manager.current = "Welcome"
        self.manager.transition.direction = "down"


class People(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def setPass(self, passenger_type):
        # Implementation to set passenger type
        pass
    
    def clearDest(self):
        # Implementation to clear destination
        pass
    
    def update_texts(self):
        """Update all text elements in the People screen"""
        for child in self.walk():
            if hasattr(child, 'text'):
                if child.text == 'Who are you driving?':
                    child.text = get_text('who_driving')
                elif child.text == 'Back':
                    child.text = get_text('back')


class Cargo(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def setCargo(self, cargo_type):
        # Implementation to set cargo type
        pass
    
    def clearPeople(self):
        # Implementation to clear people selection
        pass
    
    def update_texts(self):
        """Update all text elements in the Cargo screen"""
        for child in self.walk():
            if hasattr(child, 'text'):
                if child.text == 'What kind of cargo are they carrying?':
                    child.text = get_text('what_cargo')
                elif child.text == 'Other':
                    child.text = get_text('other')
                elif child.text == 'Back':
                    child.text = get_text('back')


class FinishTrip(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def endTrip(self):
        # Implementation to end trip
        pass
    
    def clearCargo(self):
        # Implementation to clear cargo selection
        pass
    
    def update_texts(self):
        """Update all text elements in the FinishTrip screen"""
        for child in self.walk():
            if hasattr(child, 'text'):
                if 'Click Complete when you have dropped' in child.text:
                    child.text = get_text('complete_trip')
                elif child.text == 'Complete':
                    child.text = get_text('complete')
                elif child.text == 'Back':
                    child.text = get_text('back')


class TripStats(Screen):
    def on_enter(self):
        """Update texts when entering the screen"""
        self.update_texts()
    
    def clearCurrent(self):
        # Implementation to clear current trip data
        pass
    
    def update_texts(self):
        """Update all text elements in the TripStats screen"""
        for child in self.walk():
            if hasattr(child, 'text'):
                if 'Here are the statistics of your latest trip' in child.text:
                    child.text = get_text('trip_stats')
                elif child.text == 'Destination:':
                    child.text = get_text('destination')
                elif child.text == 'Passengers & Cargo:':
                    child.text = get_text('passengers_cargo')
                elif child.text == 'Distance Driven:':
                    child.text = get_text('distance_driven')
                elif child.text == 'Trip Duration:':
                    child.text = get_text('trip_duration')
                elif child.text == 'Estimated Fuel Used:':
                    child.text = get_text('estimated_fuel')
                elif child.text == 'Start Your Next Trip':
                    child.text = get_text('start_next_trip')
                elif child.text == 'Home':
                    child.text = get_text('home')


class Loading(Screen):
    pass


class WindowManager(ScreenManager):
    pass


# -----------------------------
# MAIN APP
# -----------------------------
class MainApp(App):
    def build(self):
        return kv

    def toggle_language_and_update(self):
        """Toggle language and update all screen texts"""
        toggle_language()
        self.update_all_texts()
    
    def update_all_screen_texts(self):
        """Update all text elements across all screens"""
        # Update all screens that are currently loaded
        for screen_name in kv.screen_names:
            screen = kv.get_screen(screen_name)
            if hasattr(screen, 'update_texts'):
                screen.update_texts()
    
    def update_all_texts(self):
        """Update all text elements across all screens"""
        # Update all screens that are currently loaded
        for screen_name in kv.screen_names:
            screen = kv.get_screen(screen_name)
            self.update_screen_texts(screen, screen_name)
    
    def update_screen_texts(self, screen, screen_name):
        """Update texts for a specific screen"""
        try:
            if screen_name == "Welcome":
                # Update Welcome screen texts
                welcome_label = screen.children[0].children[7]  # Welcome label
                welcome_label.text = get_text('welcome')
                
                username_label = screen.children[0].children[5]  # Username label
                username_label.text = get_text('username')
                
                password_label = screen.children[0].children[4]  # Password label
                password_label.text = get_text('password')
                
                login_button = screen.children[0].children[0]  # Login button
                login_button.text = get_text('login')
                
                register_button = screen.children[0].children[3]  # Register button
                register_button.text = get_text('register_link')
                
            elif screen_name == "Home":
                # Update Home screen texts
                home_label = screen.children[0].children[3]  # Home label
                home_label.text = get_text('home')
                
                start_trip_button = screen.children[0].children[2]  # Start Trip button
                start_trip_button.text = get_text('start_trip')
                
                logout_button = screen.children[0].children[1]  # Log Out button
                logout_button.text = get_text('log_out')
                
                stats_button = screen.children[0].children[0]  # Get Stats button
                stats_button.text = get_text('get_stats')
                
        except (IndexError, AttributeError):
            # If we can't access the widgets directly, skip for now
            pass

    def on_start(self):
        if platform == "android":
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.ACCESS_BACKGROUND_LOCATION,
                Permission.ACCESS_FINE_LOCATION,
                Permission.ACCESS_COARSE_LOCATION
            ])

        # Ensure local DB exists
        localDBCreate()

        # ✅ Ensure cloud DB tables exist
        try:
            DBCreate()
            Logger.info("Cloud DB ready ✅")
        except Exception as e:
            Logger.error(f"Cloud DB error: {e}")

        # Simulate login (remove later)
        localDBLogin('testUser', 'testPassword', 'Test User', '1234567890', 'Company1', '1', 'Company2', '2')

        kv.transition = NoTransition()
        try:
            username = localDBPullAccountData()[0]
            if username != '':
                kv.current = "Home"
            else:
                kv.current = "Welcome"
        except:
            kv.current = "Welcome"
        kv.transition = SlideTransition()


# -----------------------------
# MISSING FUNCTION IMPLEMENTATIONS
# -----------------------------
def DBLogin(username, password):
    # Placeholder for database login function
    return True  # For now, always return True to allow login

def localDBLogOut():
    # Placeholder for local database logout function
    pass

def localDBLogin(username, password, name, phone, company1, comp1num, company2, comp2num):
    # Placeholder for local database login function
    pass

def localDBPullAccountData():
    # Placeholder for pulling account data from local database
    return ['']  # Return empty username to force login screen

# -----------------------------
# LOAD KV FILE
# -----------------------------
kv = Builder.load_file('GalapagosCarTracking.kv')

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == '__main__':
    MainApp().run()
