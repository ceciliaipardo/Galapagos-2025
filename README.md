# GalápaGo – Android App

Kivy/Python-for-Android taxi tracking app for the Galápagos Islands.  
Drivers log trips (destination, passengers, cargo, GPS distance) which are uploaded to a Supabase backend.

---

## Quick-push to device (day-to-day development)

This is the fast workflow for pushing Python source changes to a device that **already has the app installed**.  
No build required — changes are live in ~10 seconds.

### Prerequisites
| Requirement | Notes |
|---|---|
| Android SDK **platform-tools** | Provides `adb`. Install via Android Studio → SDK Manager, or download standalone from [developer.android.com](https://developer.android.com/tools/releases/platform-tools). |
| `adb` on your PATH **or** `ANDROID_HOME` / `ANDROID_SDK_ROOT` set | The script auto-detects common install locations. |
| App already installed on device | See *First-time build* below if not yet installed. |
| USB Debugging enabled on device | Settings → Developer Options → USB Debugging. |

### Steps

```bash
# 1. Clone the repo (skip if already done)
git clone https://github.com/ceciliaipardo/Galapagos-2025.git
cd Galapagos-2025

# 2. Make the script executable (only needed once)
chmod +x push_to_device.sh

# 3. Connect your Android device via USB, then push
./push_to_device.sh
```

The script will:
- Copy `main.py`, `translations.py`, `supabase_rest_api.py`, `gps_service.py`, `GalapagosCarTracking_translated.kv`, `galapago_logo.png`, `lang_icon.png` to the device
- Delete stale `.pyc` files so Kivy picks up the new sources
- Force-stop and relaunch the app automatically

---

## First-time build (full APK)

A full build is only needed once per device, or after changing `buildozer.spec` / native dependencies.

### Prerequisites
- Linux or macOS (WSL2 works on Windows)
- Python 3.10+
- [Buildozer](https://buildozer.readthedocs.io/en/latest/installation.html)

```bash
# Install buildozer
pip install buildozer

# Build a debug APK and deploy directly to a connected device
buildozer android debug deploy run
```

The resulting APK will also be in `bin/`. Install it manually with:

```bash
adb install bin/*.apk
```

---

## Project structure

```
Galapagos-2025/
├── main.py                          # Main app logic (Kivy screens, SQLite, GPS)
├── gps_service.py                   # Background GPS Android service
├── supabase_rest_api.py             # Supabase REST client (no SDK dependency)
├── translations.py                  # English / Spanish string table
├── GalapagosCarTracking_translated.kv  # Kivy UI layout
├── buildozer.spec                   # Android build configuration
├── push_to_device.sh                # Fast source-push script (see above)
├── galapago_logo.png                # App logo asset
└── lang_icon.png                    # Language toggle button icon
```

---

## Device info (tested on)

- Samsung SM-A525F (Galaxy A52), Android 12, arm64
- Package: `org.galapagos.gct`
