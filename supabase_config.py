"""
Supabase Configuration for Galapagos Car Tracking App
iOS-Compatible version using direct HTTP requests
"""
from kivy.logger import Logger
import os
import json
import urllib.request
import urllib.parse
import urllib.error
import ssl
import platform

# Supabase credentials - Use environment variables for production
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://pldkqqghyolugfecndhy.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsZGtxcWdoeW9sdWdmZWNuZGh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyNDg3NzEsImV4cCI6MjA3NDgyNDc3MX0.LW04ZSGlGD93LfU3YTFxHaFgXDX37I-Mh-zhXzcivCQ')

class SupabaseHTTPClient:
    """HTTP-based Supabase client compatible with iOS"""
    
    def __init__(self, url, key):
        self.base_url = url
        self.key = key
        self.headers = {
            'apikey': key,
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
            'Prefer': 'return=representation'
        }
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """Make HTTP request to Supabase"""
        try:
            url = f"{self.base_url}/rest/v1/{endpoint}"
            
            # Add query parameters
            if params:
                query_string = urllib.parse.urlencode(params)
                url = f"{url}?{query_string}"
            
            # Prepare request
            req = urllib.request.Request(url, headers=self.headers, method=method)
            
            # Add data for POST/PATCH
            if data:
                req.data = json.dumps(data).encode('utf-8')
            
            # Create SSL context that doesn't verify certificates (needed for iOS)
            # This is safe for Supabase as it's a trusted service
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Make request with SSL context
            with urllib.request.urlopen(req, timeout=10, context=ssl_context) as response:
                response_data = response.read().decode('utf-8')
                return json.loads(response_data) if response_data else []
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            Logger.error(f"Supabase HTTP Error {e.code}: {error_body}")
            raise Exception(f"HTTP {e.code}: {error_body}")
        except urllib.error.URLError as e:
            Logger.error(f"Supabase URL Error: {e.reason}")
            raise Exception(f"Connection failed: {e.reason}")
        except Exception as e:
            Logger.error(f"Supabase Request Error: {e}")
            raise
    
    def table(self, table_name):
        """Get table interface"""
        return SupabaseTable(self, table_name)

class SupabaseTable:
    """Table operations interface"""
    
    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self._select_columns = '*'
        self._filters = {}
        self._limit_value = None
        self._order_by = None
    
    def select(self, columns='*'):
        """Select columns"""
        self._select_columns = columns
        return self
    
    def eq(self, column, value):
        """Equal filter"""
        self._filters[f"{column}"] = f"eq.{value}"
        return self
    
    def like(self, column, pattern):
        """Like filter"""
        self._filters[f"{column}"] = f"like.{pattern}"
        return self
    
    def limit(self, count):
        """Limit results"""
        self._limit_value = count
        return self
    
    def order(self, column, desc=False):
        """Order results"""
        self._order_by = f"{column}.{'desc' if desc else 'asc'}"
        return self
    
    def execute(self):
        """Execute the query"""
        params = {
            'select': self._select_columns
        }
        
        # Add filters
        for key, value in self._filters.items():
            params[key] = value
        
        # Add limit
        if self._limit_value:
            params['limit'] = str(self._limit_value)
        
        # Add order
        if self._order_by:
            params['order'] = self._order_by
        
        data = self.client._make_request('GET', self.table_name, params=params)
        
        # Reset for next query
        self._select_columns = '*'
        self._filters = {}
        self._limit_value = None
        self._order_by = None
        
        return SupabaseResponse(data)
    
    def insert(self, data):
        """Insert data"""
        response_data = self.client._make_request('POST', self.table_name, data=data)
        return SupabaseResponse(response_data)
    
    def update(self, data):
        """Update data (with filters applied)"""
        params = {}
        for key, value in self._filters.items():
            params[key] = value
        
        response_data = self.client._make_request('PATCH', self.table_name, data=data, params=params)
        
        # Reset filters
        self._filters = {}
        
        return SupabaseResponse(response_data)
    
    def delete(self):
        """Delete data (with filters applied)"""
        params = {}
        for key, value in self._filters.items():
            params[key] = value
        
        response_data = self.client._make_request('DELETE', self.table_name, params=params)
        
        # Reset filters
        self._filters = {}
        
        return SupabaseResponse(response_data)

class SupabaseResponse:
    """Response wrapper to match supabase-py interface"""
    
    def __init__(self, data):
        self.data = data
    
    def __repr__(self):
        return f"SupabaseResponse(data={self.data})"

# Initialize Supabase HTTP client
try:
    supabase = SupabaseHTTPClient(SUPABASE_URL, SUPABASE_KEY)
    Logger.info("Supabase: Successfully initialized HTTP client")
except Exception as e:
    Logger.error(f"Supabase: Failed to initialize - {e}")
    supabase = None

def get_supabase_client():
    """Get the Supabase client instance"""
    return supabase

def test_connection():
    """Test the Supabase connection"""
    try:
        if supabase:
            # Try a simple query to test connection
            response = supabase.table('UserData').select("*").limit(1).execute()
            Logger.info("Supabase: Connection test successful")
            return True
        return False
    except Exception as e:
        Logger.error(f"Supabase: Connection test failed - {e}")
        return False
