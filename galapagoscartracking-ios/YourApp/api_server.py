"""
REST API Server for Galapagos Car Tracking App
Connects iOS app to Supabase database
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from supabase import create_client, Client
from datetime import datetime, timedelta
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Supabase credentials - Use environment variables for production, fallback to defaults for local development
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://pldkqqghyolugfecndhy.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBsZGtxcWdoeW9sdWdmZWNuZGh5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTkyNDg3NzEsImV4cCI6MjA3NDgyNDc3MX0.LW04ZSGlGD93LfU3YTFxHaFgXDX37I-Mh-zhXzcivCQ')

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test connection
        supabase.table('UserData').select("*").limit(1).execute()
        return jsonify({'status': 'healthy', 'database': 'connected'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/users/check/<username>', methods=['GET'])
def check_username(username):
    """Check if username exists"""
    try:
        response = supabase.table('UserData').select("*").eq('username', username).execute()
        exists = len(response.data) > 0
        return jsonify({'exists': exists}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/check-phone/<phone>', methods=['GET'])
def check_phone(phone):
    """Check if phone number exists"""
    try:
        response = supabase.table('UserData').select("*").eq('phone', phone).execute()
        exists = len(response.data) > 0
        return jsonify({'exists': exists}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/register', methods=['POST'])
def register_user():
    """Register a new user"""
    try:
        data = request.json
        user_data = {
            'username': data['username'],
            'password': data['password'],
            'name': data['name'],
            'phone': data['phone'],
            'company1': data['company1'],
            'comp1num': data['comp1num'],
            'company2': data.get('company2', ''),
            'comp2num': data.get('comp2num', '')
        }
        
        response = supabase.table('UserData').insert(user_data).execute()
        return jsonify({'success': True, 'user': response.data[0]}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/users/login', methods=['POST'])
def login_user():
    """Login user"""
    try:
        data = request.json
        username = data['username']
        password = data['password']
        
        response = supabase.table('UserData').select("*").eq('username', username).eq('password', password).execute()
        
        if len(response.data) > 0:
            return jsonify({'success': True, 'user': response.data[0]}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tracking/upload', methods=['POST'])
def upload_tracking_data():
    """Upload tracking data point"""
    try:
        data = request.json
        tracking_data = {
            'tripID': data['tripID'],
            'company': data['company'],
            'carnum': data['carnum'],
            'destination': data['destination'],
            'passengers': data['passengers'],
            'cargo': data['cargo'],
            'gpslon': float(data['gpslon']),
            'gpslat': float(data['gpslat']),
            'time': data['time']
        }
        
        response = supabase.table('TrackingData').insert(tracking_data).execute()
        return jsonify({'success': True, 'data': response.data[0]}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats/day/<username>/<date>', methods=['GET'])
def get_day_stats(username, date):
    """Get statistics for a specific day"""
    try:
        day_id = f"{username}{date}"
        
        # Get all end trip records for the day
        response = supabase.table('TrackingData').select("*").like('tripID', f'%{day_id}%').eq('destination', 'End Trip').execute()
        
        num_trips = len(response.data)
        total_dist = 0
        total_fuel = 0
        total_time_seconds = 0
        end_time = None
        
        for trip in response.data:
            total_dist += float(trip.get('cargo', 0))  # cargo field stores total distance
            total_fuel += float(trip.get('gpslon', 0))  # gpslon field stores total fuel
            
            # Parse time from passengers field (stores total time)
            time_str = trip.get('passengers', '00:00:00.000000')
            try:
                t = datetime.strptime(time_str, '%H:%M:%S.%f')
                total_time_seconds += t.hour * 3600 + t.minute * 60 + t.second
            except:
                pass
            
            if trip.get('time'):
                try:
                    end_time = datetime.strptime(trip['time'], '%Y-%m-%d %H:%M:%S.%f')
                except:
                    pass
        
        # Calculate idle time
        idle_time_seconds = 0
        if num_trips > 0 and end_time:
            # Get first start trip of the day
            start_response = supabase.table('TrackingData').select("*").like('tripID', f'%{day_id}%').eq('destination', 'Start Trip').order('time').limit(1).execute()
            
            if len(start_response.data) > 0:
                try:
                    start_time = datetime.strptime(start_response.data[0]['time'], '%Y-%m-%d %H:%M:%S.%f')
                    total_day_seconds = (end_time - start_time).total_seconds()
                    idle_time_seconds = total_day_seconds - total_time_seconds
                except:
                    pass
        
        return jsonify({
            'numTrips': num_trips,
            'totalDist': round(total_dist, 3),
            'totalFuel': round(total_fuel, 3),
            'totalTime': int(total_time_seconds),
            'idleTime': int(idle_time_seconds)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users', methods=['GET'])
def get_all_users():
    """Get all users (for debugging)"""
    try:
        response = supabase.table('UserData').select("*").execute()
        return jsonify({'users': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tracking', methods=['GET'])
def get_all_tracking():
    """Get all tracking data (for debugging)"""
    try:
        response = supabase.table('TrackingData').select("*").limit(100).execute()
        return jsonify({'tracking': response.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/users/clear', methods=['POST'])
def clear_users():
    """Clear all users (for testing)"""
    try:
        # Delete all records
        supabase.table('UserData').delete().neq('username', '').execute()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/tracking/clear', methods=['POST'])
def clear_tracking():
    """Clear all tracking data (for testing)"""
    try:
        # Delete all records
        supabase.table('TrackingData').delete().neq('tripID', '').execute()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/delete', methods=['POST'])
def delete_database():
    """Delete all data (for testing)"""
    try:
        supabase.table('UserData').delete().neq('username', '').execute()
        supabase.table('TrackingData').delete().neq('tripID', '').execute()
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
