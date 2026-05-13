#!/bin/bash
# ============================================================
# push_to_device.sh
# Pushes updated source files to the Android device over ADB.
# Works on non-rooted devices via run-as stdin piping.
#
# Usage:
#   chmod +x push_to_device.sh   (only needed once)
#   ./push_to_device.sh
# ============================================================

export PATH="$PATH:/Users/personal/Library/Android/sdk/platform-tools"

PACKAGE="org.galapagos.gct"
DEVICE_APP_DIR="/data/data/$PACKAGE/files/app"

# Check that a device is connected
if ! adb devices | grep -q "device$"; then
    echo "ERROR: No Android device found. Connect your device and enable USB Debugging."
    exit 1
fi

echo "Device found. Pushing files..."

# Helper: stream a local file directly into the app's private directory via run-as
push_file() {
    local LOCAL_FILE="$1"
    local REMOTE_NAME="$2"
    local DEST="$DEVICE_APP_DIR/$REMOTE_NAME"
    adb shell "run-as $PACKAGE sh -c 'cat > $DEST'" < "$LOCAL_FILE"
    echo "  Pushed $REMOTE_NAME"
}

push_file main.py                            main.py
push_file translations.py                    translations.py
push_file supabase_rest_api.py               supabase_rest_api.py
push_file gps_service.py                     gps_service.py
push_file GalapagosCarTracking_translated.kv GalapagosCarTracking_translated.kv
push_file galapago_logo.png                  galapago_logo.png
push_file lang_icon.png                      lang_icon.png

# Remove stale .pyc files so Kivy re-compiles from the fresh .py sources
echo "  Removing stale .pyc files..."
adb shell "run-as $PACKAGE sh -c 'rm -f $DEVICE_APP_DIR/main.pyc $DEVICE_APP_DIR/translations.pyc $DEVICE_APP_DIR/supabase_rest_api.pyc $DEVICE_APP_DIR/gps_service.pyc'"

echo ""
echo "All files pushed. Restarting app..."
adb shell am force-stop $PACKAGE
sleep 1
adb shell am start -n $PACKAGE/org.kivy.android.PythonActivity

echo ""
echo "Done! App is restarting on device."
