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

# ── Locate ADB ──────────────────────────────────────────────
# Try common SDK locations so this works on any machine.
# If adb is already on your PATH (e.g. you set ANDROID_HOME),
# the first check will succeed immediately.
if ! command -v adb &>/dev/null; then
    for candidate in \
        "$ANDROID_HOME/platform-tools/adb" \
        "$ANDROID_SDK_ROOT/platform-tools/adb" \
        "$HOME/Library/Android/sdk/platform-tools/adb" \
        "$HOME/Android/Sdk/platform-tools/adb" \
        "/usr/local/lib/android/sdk/platform-tools/adb"
    do
        if [ -x "$candidate" ]; then
            export PATH="$PATH:$(dirname "$candidate")"
            break
        fi
    done
fi

if ! command -v adb &>/dev/null; then
    echo "ERROR: adb not found. Install Android SDK platform-tools and ensure"
    echo "       adb is on your PATH (or set ANDROID_HOME / ANDROID_SDK_ROOT)."
    exit 1
fi

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
