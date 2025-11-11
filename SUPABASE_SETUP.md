# Supabase Integration Setup for iOS

This guide explains how your GalapaGo iOS app connects to Supabase and how to configure it for production.

## Current Architecture

Your app uses a **hybrid storage approach**:

1. **Local SQLite Database** (always available on the phone)
   - Stores user account data locally
   - Stores trip data temporarily
   - Works offline

2. **Supabase Cloud Database** (via REST API)
   - Syncs data when online
   - Provides backup and cloud storage
   - Enables data access from multiple devices

## How It Works

```
iPhone App (main_ios.py)
    ↓
    ├─→ Local SQLite (offline mode)
    └─→ REST API Server (online mode)
           ↓
           Supabase Database
```

Your app **currently runs in LOCAL MODE** (`USE_LOCAL_ONLY = True`), which means:
- ✅ All data is stored locally on the phone
- ✅ App works offline
- ❌ Data is NOT synced to Supabase
- ❌ Data is NOT backed up to the cloud

## Switching to Supabase (Production Mode)

### Step 1: Deploy Your API Server

Your API server (`api_server.py`) acts as a bridge between the iOS app and Supabase.

**Option A: Deploy to Railway (Recommended)**
```bash
# 1. Visit https://railway.app and sign up
# 2. Click "New Project" → "Deploy from GitHub repo"
# 3. Select your Galapagos-2025 repository
# 4. Railway auto-detects Python and deploys api_server.py
# 5. Copy your deployment URL (e.g., https://galapago-api-production.railway.app)
```

**Option B: Deploy to Render**
```bash
# 1. Visit https://render.com and sign up
# 2. Create "New Web Service" from GitHub
# 3. Configure:
#    - Build Command: pip install -r api_requirements.txt
#    - Start Command: gunicorn api_server:app
# 4. Copy your service URL
```

### Step 2: Test Your API

Once deployed, verify it's working:

```bash
# Replace with your actual API URL
curl https://your-api-url.railway.app/api/health
```

Expected response:
```json
{"status": "healthy", "database": "connected"}
```

### Step 3: Update iOS App Configuration

Open `main_ios.py` and update these lines (around line 36-37):

```python
# BEFORE (Local Mode)
API_BASE_URL = "https://your-api-server.com/api"
USE_LOCAL_ONLY = True

# AFTER (Production Mode with Supabase)
API_BASE_URL = "https://your-api-url.railway.app/api"  # Your actual URL
USE_LOCAL_ONLY = False
```

**Important:** Make sure to include `/api` at the end of the URL!

### Step 4: Rebuild iOS App

Since you changed the configuration, you need to rebuild:

**Method 1: Rebuild with Python script**
```bash
cd "/Users/SheeeeeeeeeeeesH/Desktop/ECE_Capstone/Python/Galapagos-2025"
python ios_build.py
```

**Method 2: Rebuild in Xcode**
```bash
# 1. Open your project
open "/Users/SheeeeeeeeeeeesH/Desktop/ECE_Capstone/Python/Galapagos-2025/kivy-ios/galapago-ios/galapago.xcodeproj"

# 2. In Xcode:
#    - Product → Clean Build Folder
#    - Product → Build
```

### Step 5: Test on Your Phone

1. **Install the rebuilt app** on your iPhone
2. **Test Registration:**
   - Create a new account
   - Check Supabase dashboard to verify user was created
   - Dashboard: https://supabase.com → Your Project → Table Editor → UserData

3. **Test Login:**
   - Log in with the account you just created
   - Should work with cloud data

4. **Test Trip Tracking:**
   - Start a trip
   - Drive around
   - End the trip
   - Check Supabase → TrackingData table for GPS points

## How Data Syncing Works

### Registration (Online Mode)
1. User fills out registration form
2. App sends data to API server
3. API server stores in Supabase UserData table
4. User info also cached locally for offline access

### Login (Online Mode)
1. User enters username/password
2. App sends to API server
3. API server checks Supabase
4. If valid, user data cached locally
5. Can use app offline after initial login

### Trip Tracking (Hybrid Mode)
1. GPS data is **always saved locally first**
2. When trip ends:
   - If online: Data syncs to Supabase immediately
   - If offline: Data queued locally
3. Next time online: Queued data syncs automatically

This ensures **no data loss** even with poor connectivity!

## Monitoring Your Setup

### Check if App is in Production Mode

In Xcode console or app logs, look for:
- `"Using API connection instead of direct MySQL"` - Good!
- `"API requests disabled - using local storage only"` - Still in local mode

### View Supabase Data

1. Go to https://supabase.com
2. Select your project
3. Click "Table Editor"
4. View tables:
   - **UserData**: Registered users
   - **TrackingData**: GPS tracking points

### Check API Health

Visit your API health endpoint in a browser:
```
https://your-api-url.railway.app/api/health
```

Should show: `{"status":"healthy","database":"connected"}`

## Troubleshooting

### Problem: "Connection Required to Log In"

**Cause:** App can't reach API server

**Solutions:**
1. Verify API is deployed and running
2. Check API_BASE_URL in main_ios.py
3. Ensure phone has internet connection
4. Test API health endpoint in browser

### Problem: Data Not Appearing in Supabase

**Cause:** App still in local mode

**Solutions:**
1. Check `USE_LOCAL_ONLY = False` in main_ios.py
2. Rebuild the iOS app
3. Reinstall on phone

### Problem: API Returns Errors

**Cause:** API server issue or Supabase credentials

**Solutions:**
1. Check API server logs (Railway/Render dashboard)
2. Verify Supabase credentials in api_server.py
3. Test Supabase connection in Supabase dashboard

## Configuration Reference

### main_ios.py Settings

```python
# Local Mode (offline only, no Supabase)
API_BASE_URL = "https://your-api-server.com/api"
USE_LOCAL_ONLY = True

# Production Mode (syncs with Supabase)
API_BASE_URL = "https://galapago-api.railway.app/api"
USE_LOCAL_ONLY = False
```

### API Endpoints Used

The app makes requests to these endpoints:

- `GET /api/health` - Check API status
- `GET /api/users/check/{username}` - Check if username exists
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - Login user
- `POST /api/tracking/upload` - Upload GPS tracking point
- `GET /api/stats/day/{username}/{date}` - Get daily statistics

## Security Considerations

### Current Setup (Development)
- Uses Supabase anon key (safe for client apps)
- No API authentication
- Suitable for development/testing

### For Production (Recommended)
1. **Add API Key Authentication**
   - Protect API endpoints with API keys
   - Store API key securely in iOS app

2. **Use HTTPS**
   - Railway/Render provide HTTPS automatically
   - Never use HTTP in production

3. **Environment Variables**
   - Store Supabase credentials as env vars in Railway/Render
   - Don't commit credentials to Git

## Summary

Your GalapaGo app is ready for Supabase integration! Here's the checklist:

- [x] API server created (`api_server.py`)
- [x] iOS app configured for API connectivity (`main_ios.py`)
- [x] iOS requirements updated with `requests` library
- [ ] Deploy API server to Railway/Render
- [ ] Update `main_ios.py` with actual API URL
- [ ] Set `USE_LOCAL_ONLY = False`
- [ ] Rebuild iOS app
- [ ] Test registration, login, and tracking
- [ ] Verify data appears in Supabase

Once you complete the unchecked items, your app will sync data to Supabase!
