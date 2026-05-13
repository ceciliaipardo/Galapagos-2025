"""
Background service that keeps the app process alive during a trip.
The actual GPS is managed by _start_android_gps() in the main activity
on a HandlerThread with a WakeLock. This service's job is simply to
prevent Android from killing the process when the screen turns off.
"""
from kivy.logger import Logger
from time import sleep

try:
    from jnius import autoclass
    PythonService = autoclass('org.kivy.android.PythonService')
    service = PythonService.mService

    # Auto-restart if Android kills the service
    service.setAutoRestartService(True)

    # Promote to a Foreground Service so Android won't kill it
    # (requires FOREGROUND_SERVICE permission in manifest)
    try:
        NotificationBuilder = autoclass('android.app.Notification$Builder')
        NotificationManager = autoclass('android.app.NotificationManager')
        Context = autoclass('android.content.Context')
        nm = service.getSystemService(Context.NOTIFICATION_SERVICE)

        # Create notification channel (required on Android 8+)
        try:
            NotificationChannel = autoclass('android.app.NotificationChannel')
            channel = NotificationChannel(
                'gps_channel', 'GPS Tracking',
                NotificationManager.IMPORTANCE_LOW)
            nm.createNotificationChannel(channel)
        except Exception:
            pass  # Pre-Oreo devices don't need channels

        builder = NotificationBuilder(service, 'gps_channel')
        builder.setSmallIcon(service.getApplicationInfo().icon)
        builder.setContentTitle('GalapaGo')
        builder.setContentText('Trip tracking active')
        builder.setOngoing(True)
        notification = builder.build()
        service.startForeground(1, notification)
        Logger.info('GPS Service: running as foreground service')
    except Exception as e:
        Logger.warning(f'GPS Service: could not start as foreground ({e}), continuing anyway')

except Exception as e:
    Logger.error(f'GPS Service: init error: {e}')

Logger.info('GPS Service: started — keeping process alive')

# Keep the service alive with a heartbeat
while True:
    Logger.info('GPS Service: heartbeat')
    sleep(30)
