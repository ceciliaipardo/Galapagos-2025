#!/bin/bash
# ============================================================
# push_to_device.sh
# Pushes updated source files to the Android device over ADB.
# Run this instead of rebuilding after every code change.
#
# Usage:
#   chmod +x push_to_device.sh   (only needed once)
#   ./push_to_device.sh
# ============================================================

PACKAGE="org.galapagos.gct"
DEVICE_APP_DIR="/data/data/$PACKAGE/files/app"

# Check that a device is connected
if ! adb devices | grep -q "device$"; then
    echo "ERROR: No Android device found. Connect your device and enable USB Debugging."
    exit 1
fi

echo "Device found. Pushing files..."

# --- Python source files ---
adb push main.py                        $DEVICE_APP_DIR/main.py
adb push translations.py                $DEVICE_APP_DIR/translations.py
adb push supabase_rest_api.py           $DEVICE_APP_DIR/supabase_rest_api.py
adb push gps_service.py                 $DEVICE_APP_DIR/gps_service.py

# --- KV layout file ---
adb push GalapagosCarTracking_translated.kv $DEVICE_APP_DIR/GalapagosCarTracking_translated.kv

# --- Fonts ---
adb push CaviarDreams.ttf               $DEVICE_APP_DIR/CaviarDreams.ttf
adb push CaviarDreams_Bold.ttf          $DEVICE_APP_DIR/CaviarDreams_Bold.ttf
adb push CaviarDreams_Italic.ttf        $DEVICE_APP_DIR/CaviarDreams_Italic.ttf
adb push CaviarDreams_BoldItalic.ttf    $DEVICE_APP_DIR/CaviarDreams_BoldItalic.ttf

echo ""
echo "All files pushed. Restarting app..."

# Force-stop the app
adb shell am force-stop $PACKAGE

# Small pause to let the OS fully close it
sleep 1

# Relaunch the app
adb shell am start -n $PACKAGE/org.kivy.android.PythonActivity

echo ""
echo "Done! App is restarting on device."
