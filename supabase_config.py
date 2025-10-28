"""
Supabase Configuration for Galapagos Car Tracking App
"""
from supabase import create_client, Client
from kivy.logger import Logger

# Supabase credentials
SUPABASE_URL = "https://pldkqqghyolugfecndhy.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsZGtxcWdoeW9sdWdmZWNuZGh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyNDg3NzEsImV4cCI6MjA3NDgyNDc3MX0.LW04ZSGlGD93LfU3YTFxHaFgXDX37I-Mh-zhXzcivCQ"

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    Logger.info("Supabase: Successfully connected to Supabase")
except Exception as e:
    Logger.error(f"Supabase: Failed to connect - {e}")
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
            return True
        return False
    except Exception as e:
        Logger.error(f"Supabase: Connection test failed - {e}")
        return False
