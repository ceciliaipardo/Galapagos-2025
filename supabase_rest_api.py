"""
Supabase REST API wrapper for Android compatibility
Uses only standard HTTP requests - no special dependencies needed
"""
import json
import urllib.request
import urllib.error
import ssl
from kivy.logger import Logger

# Create SSL context that doesn't verify certificates (for development)
# This fixes the "CERTIFICATE_VERIFY_FAILED" error on macOS
try:
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
except:
    ssl_context = None

# Supabase credentials
SUPABASE_URL = "https://pldkqqghyolugfecndhy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsZGtxcWdoeW9sdWdmZWNuZGh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyNDg3NzEsImV4cCI6MjA3NDgyNDc3MX0.LW04ZSGlGD93LfU3YTFxHaFgXDX37I-Mh-zhXzcivCQ"

def make_request(endpoint, method='GET', data=None, params=None):
    """
    Make HTTP request to Supabase REST API
    
    Args:
        endpoint: API endpoint (e.g., 'UserData', 'TripData')
        method: HTTP method ('GET', 'POST', 'PATCH', 'DELETE')
        data: JSON data for POST/PATCH requests
        params: Query parameters as dict
    
    Returns:
        Response data as dict or list
    """
    try:
        # Build URL
        url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
        
        # Add query parameters
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            url = f"{url}?{query_string}"
        
        # Prepare headers
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
        
        # Prepare request
        if data:
            json_data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=json_data, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)
        
        # Make request with SSL context to avoid certificate errors
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            response_data = response.read().decode('utf-8')
            if response_data:
                return json.loads(response_data)
            return []
            
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        Logger.error(f"Supabase HTTP Error {e.code}: {error_body}")
        raise Exception(f"HTTP Error {e.code}: {error_body}")
    except urllib.error.URLError as e:
        Logger.error(f"Supabase URL Error: {e.reason}")
        raise Exception(f"Connection Error: {e.reason}")
    except Exception as e:
        Logger.error(f"Supabase Request Error: {e}")
        raise

def select(table, columns='*', filters=None, limit=None):
    """
    SELECT query
    
    Args:
        table: Table name
        columns: Columns to select (default '*')
        filters: Dict of column:value pairs for filtering
        limit: Max number of rows
    
    Returns:
        List of matching rows
    """
    params = {'select': columns}
    
    # Add filters
    if filters:
        for col, val in filters.items():
            params[col] = f"eq.{val}"
    
    # Add limit
    if limit:
        params['limit'] = str(limit)
    
    return make_request(table, method='GET', params=params)

def insert(table, data):
    """
    INSERT query
    
    Args:
        table: Table name
        data: Dict or list of dicts to insert
    
    Returns:
        Inserted data
    """
    if not isinstance(data, list):
        data = [data]
    
    return make_request(table, method='POST', data=data)

def update(table, data, filters):
    """
    UPDATE query
    
    Args:
        table: Table name
        data: Dict of columns to update
        filters: Dict of column:value pairs for WHERE clause
    
    Returns:
        Updated data
    """
    params = {}
    for col, val in filters.items():
        params[col] = f"eq.{val}"
    
    return make_request(table, method='PATCH', data=data, params=params)

def delete(table, filters):
    """
    DELETE query
    
    Args:
        table: Table name
        filters: Dict of column:value pairs for WHERE clause
    
    Returns:
        Deleted data
    """
    params = {}
    for col, val in filters.items():
        params[col] = f"eq.{val}"
    
    return make_request(table, method='DELETE', params=params)

def test_connection():
    """Test the Supabase connection"""
    try:
        # Try a simple query
        result = select('UserData', limit=1)
        Logger.info("Supabase: Connection test successful")
        return True
    except Exception as e:
        Logger.error(f"Supabase: Connection test failed - {e}")
        return False

# Compatibility functions for existing code
def check_username_exists(username):
    """Check if username exists"""
    try:
        result = select('UserData', columns='username', filters={'username': username})
        return len(result) > 0
    except Exception as e:
        Logger.error(f"check_username_exists failed: {e}")
        raise

def check_phone_exists(phone):
    """Check if phone exists"""
    try:
        result = select('UserData', columns='phone', filters={'phone': phone})
        return len(result) > 0
    except Exception as e:
        Logger.error(f"check_phone_exists failed: {e}")
        raise

def register_user(username, password, name, phone, company1, comp1num, company2, comp2num):
    """Register new user"""
    try:
        data = {
            "username": username,
            "password": password,
            "name": name,
            "phone": phone,
            "company1": company1,
            "comp1num": comp1num,
            "company2": company2,
            "comp2num": comp2num
        }
        insert('UserData', data)
        Logger.info(f"User registered successfully: {username}")
    except Exception as e:
        Logger.error(f"register_user failed: {e}")
        raise

def login_user(username, password):
    """Login user"""
    try:
        result = select('UserData', filters={'username': username, 'password': password})
        return result[0] if len(result) > 0 else None
    except Exception as e:
        Logger.error(f"login_user failed: {e}")
        return None

def get_user_data(username):
    """Get user data"""
    try:
        result = select('UserData', filters={'username': username})
        return result[0] if len(result) > 0 else None
    except Exception as e:
        Logger.error(f"get_user_data failed: {e}")
        return None

def upload_trip_summary(trip_id, username, company, car_number, destination, passenger_type, 
                       passenger_count, cargo_type, distance_km, duration_seconds, 
                       fuel_gallons, start_time, end_time, starting_point):
    """Upload complete trip summary to TripData table"""
    try:
        data = {
            "trip_id": trip_id,
            "username": username,
            "company": company,
            "car_number": car_number,
            "destination": destination,
            "passenger_type": passenger_type,
            "passenger_count": passenger_count,
            "cargo_type": cargo_type,
            "distance_km": float(distance_km) if distance_km else 0.0,
            "duration_seconds": int(duration_seconds) if duration_seconds else 0,
            "fuel_gallons": float(fuel_gallons) if fuel_gallons else 0.0,
            "start_time": start_time,
            "end_time": end_time,
            "starting_point": starting_point
        }
        Logger.info(f"=== UPLOADING TRIP TO TRIPDATA ===")
        Logger.info(f"Data being sent: {data}")
        print(f"\n=== UPLOADING TO TRIPDATA TABLE ===")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        result = insert('TripData', data)
        Logger.info(f"Trip summary uploaded successfully: {trip_id}")
        Logger.info(f"Server response: {result}")
        print(f"Upload successful! Response: {result}\n")
        return result
    except Exception as e:
        Logger.error(f"upload_trip_summary failed: {e}")
        print(f"ERROR uploading trip: {e}")
        raise

def upload_tracking_data(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    """Legacy function - kept for compatibility with local DB tracking"""
    # This function is now only used for local database tracking
    # Actual trip data is uploaded via upload_trip_summary at the end of the trip
    pass

def get_day_stats(username, date):
    """Get daily statistics from TripData table - uses new schema"""
    try:
        # Query trips for the given username and date
        # date format should be YYYYMMDD
        from datetime import datetime
        try:
            # Convert date from YYYYMMDD to YYYY-MM-DD format for comparison
            date_obj = datetime.strptime(date, '%Y%m%d')
            date_str = date_obj.strftime('%Y-%m-%d')
        except:
            date_str = date
        
        url = f"{SUPABASE_URL}/rest/v1/TripData"
        
        # Get all trips for the user on this date
        # Use 'and' operator for date range
        query_string = f"select=distance_km,duration_seconds,fuel_gallons,start_time,end_time&username=eq.{username}&start_time=gte.{date_str}T00:00:00&start_time=lt.{date_str}T23:59:59"
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        full_url = f"{url}?{query_string}"
        
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            trips = json.loads(response.read().decode('utf-8'))
        
        return {
            'trips': trips,
            'start_time': trips[0]['start_time'] if trips else None
        }
        
    except Exception as e:
        Logger.error(f"get_day_stats failed: {e}")
        raise

def get_individual_trips(username, date=None):
    """Get individual trip details - all trips or for a specific day"""
    try:
        from datetime import datetime
        
        url = f"{SUPABASE_URL}/rest/v1/TripData"
        
        if date:
            # Get trips for specific date
            try:
                # Convert date from YYYYMMDD to YYYY-MM-DD format for comparison
                date_obj = datetime.strptime(date, '%Y%m%d')
                date_str = date_obj.strftime('%Y-%m-%d')
            except:
                date_str = date
            
            # Get all trip details for the user on this date, ordered by start_time descending (most recent first)
            query_string = f"select=*&username=eq.{username}&start_time=gte.{date_str}T00:00:00&start_time=lt.{date_str}T23:59:59&order=start_time.desc"
        else:
            # Get ALL trips for the user, ordered by start_time descending (most recent first)
            query_string = f"select=*&username=eq.{username}&order=start_time.desc"
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        full_url = f"{url}?{query_string}"
        
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            trips = json.loads(response.read().decode('utf-8'))
        
        return trips
        
    except Exception as e:
        Logger.error(f"get_individual_trips failed: {e}")
        raise
