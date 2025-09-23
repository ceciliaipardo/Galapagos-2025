# Galapagos Car Tracking App

## How to Run the App

### Method 1: Using the Batch File (Recommended)
Simply double-click on `run_app.bat` to start the application.

### Method 2: Using Command Line
1. Open Command Prompt or PowerShell
2. Navigate to the app directory
3. Run: `py main.py` (NOT `python main.py`)

**Important**: Use `py` instead of `python` on Windows. The `python` command may not be available depending on your Python installation method.

### Method 3: From PowerShell/Terminal
```
.\run_app.bat
```

## Features
- Car tracking for taxi services in the Galapagos Islands
- Bilingual support (English/Spanish)
- GPS tracking and trip statistics
- Local SQLite database with MySQL server sync capability
- Multiple company/car support per driver

## Requirements
- Python 3.7+
- Kivy framework
- KivyMD
- Plyer (for GPS functionality)
- SQLite (included with Python)
- MySQL connector (optional, for server sync)

## Troubleshooting
If the app doesn't start:
1. Make sure Python is installed
2. Try running `py --version` to verify Python installation
3. Check that all dependencies are installed
4. Run the batch file as administrator if needed

## Notes
- GPS functionality works best on mobile devices
- The app includes test data for demonstration purposes
- MySQL server connection is optional - the app works with local SQLite database
