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
        endpoint: API endpoint (e.g., 'UserData', 'TrackingData')
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

def upload_tracking_data(tripID, company, carnum, destination, passengers, cargo, gpslon, gpslat, time):
    """Upload tracking data point"""
    try:
        data = {
            "tripID": tripID,
            "company": company,
            "carnum": carnum,
            "destinationXstatus": destination,
            "passengersXtotalTime": str(passengers),
            "cargoXtotalDist": str(cargo),
            "gpslonXworkingFuel": str(gpslon),
            "gpslat": str(gpslat),
            "time": str(time)
        }
        insert('TrackingData', data)
    except Exception as e:
        Logger.error(f"upload_tracking_data failed: {e}")
        raise

def get_day_stats(username, date):
    """Get daily statistics - uses advanced query"""
    try:
        dayID = f"{username}{date}"
        
        # Get all trips that end with 'End Trip' for the given day
        # Using like filter for tripID
        url = f"{SUPABASE_URL}/rest/v1/TrackingData"
        params = {
            'select': 'passengersXtotalTime,cargoXtotalDist,gpslonXworkingFuel,time',
            'destinationXstatus': 'eq.End Trip',
            'tripID': f'like.{dayID}*'
        }
        
        headers = {
            'apikey': SUPABASE_KEY,
            'Authorization': f'Bearer {SUPABASE_KEY}',
            'Content-Type': 'application/json'
        }
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        full_url = f"{url}?{query_string}"
        
        req = urllib.request.Request(full_url, headers=headers)
        with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
            trips = json.loads(response.read().decode('utf-8'))
        
        # Get trip start data
        params2 = {
            'select': 'time',
            'destinationXstatus': 'eq.Start Trip',
            'tripID': f'like.{dayID}*',
            'limit': '1'
        }
        
        query_string2 = '&'.join([f"{k}={v}" for k, v in params2.items()])
        full_url2 = f"{url}?{query_string2}"
        
        req2 = urllib.request.Request(full_url2, headers=headers)
        with urllib.request.urlopen(req2, timeout=10, context=ssl_context) as response:
            start_data = json.loads(response.read().decode('utf-8'))
        
        return {
            'trips': trips,
            'start_time': start_data[0]['time'] if start_data else None
        }
        
    except Exception as e:
        Logger.error(f"get_day_stats failed: {e}")
        raise
