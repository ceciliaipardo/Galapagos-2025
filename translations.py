# Translation system for Galapagos Car Tracking App
# Contains all text strings in English and Spanish

class Translations:
    def __init__(self):
        self.current_language = 'es'  # Default to Spanish
        
        self.texts = {
            'en': {
                # Welcome Screen
                'welcome': 'Welcome!',
                'username': 'Username:',
                'password': 'Password:',
                'login': 'Log In',
                'register_link': "Don't have an account? Register Here",
                'invalid_credentials': 'Invalid Username or Password',
                'connection_required_login': 'Connection Required to Log In',
                
                # Home Screen
                'home': 'Home',
                'start_trip': 'Start Trip',
                'log_out': 'Log Out',
                'get_stats': 'Get Stats',
                
                # Registration Screens
                'fill_out_following': 'Please Fill Out the following:',
                'complete_registration': 'Complete your Registration:',
                'name': 'Name:',
                'phone_number': 'Phone Number:',
                'car_company': 'Company 1:',
                'car_number': 'Car Number 1:',
                'check_another_company': 'Check this Box if you Drive for Another Company:',
                'second_car_company': 'Company 2:',
                'second_car_number': 'Car Number 2:',
                'company_1': 'Company 1',
                'company_2': 'Company 2',
                'next': 'Next',
                'back': 'Back',
                'done': 'Done',
                'username_exists': 'This username is already in use. Please choose another username.',
                'phone_exists': 'This phone number is already in use',
                'username_invalid': 'Username Invalid',
                'phone_invalid': 'Phone Number Invalid',
                'connection_required_register': 'Connection Required to Register New Account',
                
                # Statistics Screen
                'statistics_today': 'Statistics for Today',
                'number_of_trips': 'Number of Trips',
                'miles_driven': 'Miles Driven',
                'estimated_gas': 'Estimated Total Gas Usage',
                'total_time': 'Total Driving Time',
                'time_between': 'Time Spent Between Trips',
                'back_to_home': 'Back to Home',
                'no_data_available': 'No Data Available',
                'connection_required': 'Connection Required',
                'trips': 'Trips',
                'miles': 'Miles',
                'gallons': 'Gallons',
                'hours_minutes_seconds': '{} Hours, {} Minutes, {} Seconds',
                
                # Start Trip Screen
                'which_car': 'Which car are you using?',
                
                # Destination Screen
                'where_going': 'Where are you going?',
                'the_highlands': 'Highlands',
                'puerto_ayora': 'Puerto Ayora',
                'airport': 'Airport',
                'other': 'Other',
                
                # People Screen
                'who_driving': 'Who are you driving?',
                'students': 'Student',
                'tourist': 'Tourist',
                'locals': 'Local',
                
                # Passenger Count Screen
                'passenger_count': 'Number of Passengers?',
                '1_passenger': '1',
                '2_passengers': '2',
                '3_passengers': '3',
                '4_passengers': '4',
                '5_plus_passengers': '5+',
                
                # Cargo Screen
                'what_cargo': 'What kind of cargo are they carrying?',
                'luggage': 'Luggage',
                'work_equipment': 'Work Equipment',
                'food_goods': 'Food and Goods',
                'misc_cargo': 'Varied Load',
                
                # Finish Trip Screen
                'click_complete': 'Click Complete when you have dropped \n       your passenger and cargo off',
                'complete': 'Complete',
                
                # Trip Stats Screen
                'trip_statistics': 'Here are the statistics of your latest trip',
                'destination': 'Destination:',
                'passengers_cargo': 'Passengers & Cargo:',
                'distance_driven': 'Distance Driven:',
                'trip_duration': 'Trip Duration:',
                'estimated_fuel': 'Estimated Fuel Used:',
                'start_next_trip': 'Start Your Next Trip',
                'trip_too_short': 'Trip Too Short',
                
                # General
                'language': 'Language',
                'english': 'English',
                'spanish': 'Español'
            },
            'es': {
                # Welcome Screen
                'welcome': '¡Bienvenido!',
                'username': 'Usuario:',
                'password': 'Contraseña:',
                'login': 'Iniciar Sesión',
                'register_link': "¿No tienes cuenta? Regístrate Aquí",
                'invalid_credentials': 'Usuario o Contraseña Inválidos',
                'connection_required_login': 'Se Requiere Conexión para Iniciar Sesión',
                
                # Home Screen
                'home': 'Inicio',
                'start_trip': 'Iniciar Viaje',
                'log_out': 'Cerrar Sesión',
                'get_stats': 'Ver Estadísticas',
                
                # Registration Screens
                'fill_out_following': 'Por favor complete lo siguiente:',
                'complete_registration': 'Complete su Registro:',
                'name': 'Nombre:',
                'phone_number': 'Número de Teléfono:',
                'car_company': 'Compañía 1:',
                'car_number': 'Número de Auto 1:',
                'check_another_company': 'Marque esta casilla si maneja para otra compañía:',
                'second_car_company': 'Compañía 2:',
                'second_car_number': 'Número de Auto 2:',
                'company_1': 'Compañía 1',
                'company_2': 'Compañía 2',
                'next': 'Siguiente',
                'back': 'Atrás',
                'done': 'Listo',
                'username_exists': 'Este nombre de usuario ya está en uso. Por favor elija otro.',
                'phone_exists': 'Este número de teléfono ya está en uso',
                'username_invalid': 'Usuario Inválido',
                'phone_invalid': 'Número de Teléfono Inválido',
                'connection_required_register': 'Se Requiere Conexión para Registrar Nueva Cuenta',
                
                # Statistics Screen
                'statistics_today': 'Estadísticas de Hoy',
                'number_of_trips': 'Número de Viajes',
                'miles_driven': 'Millas Conducidas',
                'estimated_gas': 'Uso Total Estimado de Gasolina',
                'total_time': 'Tiempo Total de Conducción',
                'time_between': 'Tiempo Entre Viajes',
                'back_to_home': 'Volver al Inicio',
                'no_data_available': 'No Hay Datos Disponibles',
                'connection_required': 'Se Requiere Conexión',
                'trips': 'Viajes',
                'miles': 'Millas',
                'gallons': 'Galones',
                'hours_minutes_seconds': '{} Horas, {} Minutos, {} Segundos',
                
                # Start Trip Screen
                'which_car': '¿Qué auto está usando?',
                
                # Destination Screen
                'where_going': '¿A dónde va?',
                'the_highlands': 'Tierras Altas',
                'puerto_ayora': 'Puerto Ayora',
                'airport': 'Aeropuerto',
                'other': 'Otro',
                
                # People Screen
                'who_driving': '¿A quién está transportando?',
                'students': 'Estudiante',
                'tourist': 'Turista',
                'locals': 'Local',
                
                # Passenger Count Screen
                'passenger_count': '¿Número de Pasajeros?',
                '1_passenger': '1',
                '2_passengers': '2',
                '3_passengers': '3',
                '4_passengers': '4',
                '5_plus_passengers': '5+',
                
                # Cargo Screen
                'what_cargo': '¿Qué tipo de carga llevan?',
                'luggage': 'Equipaje',
                'work_equipment': 'Equipo de Trabajo',
                'food_goods': 'Comida y Productos',
                'misc_cargo': 'Carga Variada',
                
                # Finish Trip Screen
                'click_complete': 'Haga clic en Completar cuando haya dejado \n       a su pasajero y carga',
                'complete': 'Completar',
                
                # Trip Stats Screen
                'trip_statistics': 'Aquí están las estadísticas de su último viaje',
                'destination': 'Destino:',
                'passengers_cargo': 'Pasajeros y Carga:',
                'distance_driven': 'Distancia Conducida:',
                'trip_duration': 'Duración del Viaje:',
                'estimated_fuel': 'Combustible Estimado Usado:',
                'start_next_trip': 'Iniciar su Próximo Viaje',
                'trip_too_short': 'Viaje Muy Corto',
                
                # General
                'language': 'Idioma',
                'english': 'English',
                'spanish': 'Español'
            }
        }
    
    def get_text(self, key):
        """Get translated text for the current language"""
        return self.texts[self.current_language].get(key, key)
    
    def set_language(self, language):
        """Set the current language (en or es)"""
        if language in self.texts:
            self.current_language = language
    
    def get_current_language(self):
        """Get the current language"""
        return self.current_language
    
    def toggle_language(self):
        """Toggle between English and Spanish"""
        self.current_language = 'es' if self.current_language == 'en' else 'en'

# Global translation instance
translator = Translations()
