#!/usr/bin/env python3
"""
iOS Build Script for Galapagos Car Tracking App
This script automates the iOS build process using kivy-ios
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configuration
APP_NAME = "GCT"
APP_BUNDLE_ID = "org.galapagos.gct"
APP_VERSION = "0.1"
KIVY_IOS_DIR = "kivy-ios"
REQUIREMENTS_FILE = "ios_requirements.txt"

def run_command(command, cwd=None):
    """Run a shell command and handle errors"""
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, cwd=cwd, 
                              capture_output=True, text=True)
        print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error output: {e.stderr}")
        sys.exit(1)

def check_prerequisites():
    """Check if required tools are installed"""
    print("Checking prerequisites...")
    
    # Check if Xcode is installed
    try:
        run_command("xcode-select --print-path")
        print("✓ Xcode found")
    except:
        print("✗ Xcode not found. Please install Xcode from the App Store.")
        sys.exit(1)
    
    # Check if Python 3 is available
    try:
        run_command("python3 --version")
        print("✓ Python 3 found")
    except:
        print("✗ Python 3 not found. Please install Python 3.")
        sys.exit(1)

def setup_kivy_ios():
    """Clone and setup kivy-ios if not already present"""
    print("Setting up kivy-ios...")
    
    if not os.path.exists(KIVY_IOS_DIR):
        print("Cloning kivy-ios...")
        run_command(f"git clone https://github.com/kivy/kivy-ios.git {KIVY_IOS_DIR}")
    else:
        print("kivy-ios already exists, updating...")
        run_command("git pull", cwd=KIVY_IOS_DIR)
    
    # Install kivy-ios requirements
    print("Installing kivy-ios requirements...")
    run_command(f"pip3 install -r {KIVY_IOS_DIR}/requirements.txt")

def build_requirements():
    """Build the required packages for iOS"""
    print("Building requirements for iOS...")
    
    # Read requirements from file
    if os.path.exists(REQUIREMENTS_FILE):
        with open(REQUIREMENTS_FILE, 'r') as f:
            requirements = [line.strip() for line in f.readlines() 
                          if line.strip() and not line.startswith('#')]
    else:
        # Default requirements if file doesn't exist
        requirements = ['python3', 'kivy', 'kivymd', 'sqlite3', 'plyer']
    
    # Build each requirement
    for req in requirements:
        print(f"Building {req}...")
        run_command(f"./toolchain.py build {req}", cwd=KIVY_IOS_DIR)

def create_xcode_project():
    """Create the Xcode project"""
    print("Creating Xcode project...")
    
    # Create the Xcode project
    cmd = f"./toolchain.py create {APP_NAME} ."
    run_command(cmd, cwd=KIVY_IOS_DIR)
    
    print(f"Xcode project created: {KIVY_IOS_DIR}/{APP_NAME}-ios")

def copy_app_files():
    """Copy application files to the iOS project"""
    print("Copying application files...")
    
    ios_project_dir = f"{KIVY_IOS_DIR}/{APP_NAME}-ios"
    
    # Copy main.py
    shutil.copy2("main.py", ios_project_dir)
    
    # Copy .kv file
    shutil.copy2("GalapagosCarTracking.kv", ios_project_dir)
    
    # Copy any image assets
    assets_dir = f"{ios_project_dir}/assets"
    os.makedirs(assets_dir, exist_ok=True)
    
    # Copy image files
    image_extensions = ['.png', '.jpg', '.jpeg', '.gif']
    for file in os.listdir('.'):
        if any(file.lower().endswith(ext) for ext in image_extensions):
            shutil.copy2(file, assets_dir)
            print(f"Copied asset: {file}")

def update_info_plist():
    """Update the Info.plist file with app-specific settings"""
    print("Updating Info.plist...")
    
    info_plist_path = f"{KIVY_IOS_DIR}/{APP_NAME}-ios/{APP_NAME}-Info.plist"
    
    # Note: This is a basic update. For more complex plist modifications,
    # you might want to use the plistlib module
    plist_updates = f"""
    <!-- Add location permissions -->
    <key>NSLocationWhenInUseUsageDescription</key>
    <string>This app needs location access to track car routes.</string>
    <key>NSLocationAlwaysAndWhenInUseUsageDescription</key>
    <string>This app needs location access to track car routes.</string>
    <key>NSLocationAlwaysUsageDescription</key>
    <string>This app needs location access to track car routes.</string>
    
    <!-- App Transport Security -->
    <key>NSAppTransportSecurity</key>
    <dict>
        <key>NSAllowsArbitraryLoads</key>
        <true/>
    </dict>
    """
    
    print("Please manually add the following to your Info.plist file:")
    print(plist_updates)

def main():
    """Main build process"""
    print("Starting iOS build process for Galapagos Car Tracking...")
    
    # Check prerequisites
    check_prerequisites()
    
    # Setup kivy-ios
    setup_kivy_ios()
    
    # Build requirements
    build_requirements()
    
    # Create Xcode project
    create_xcode_project()
    
    # Copy app files
    copy_app_files()
    
    # Update Info.plist
    update_info_plist()
    
    print("\n" + "="*50)
    print("iOS BUILD COMPLETE!")
    print("="*50)
    print(f"Your Xcode project is located at: {KIVY_IOS_DIR}/{APP_NAME}-ios")
    print("\nNext steps:")
    print("1. Open the Xcode project")
    print("2. Configure your Apple Developer account")
    print("3. Set up code signing")
    print("4. Build and run on your device")
    print("\nIMPORTANT NOTES:")
    print("- MySQL connectivity won't work on iOS")
    print("- Consider implementing a REST API for database operations")
    print("- Test GPS functionality on a real device")

if __name__ == "__main__":
    main()
