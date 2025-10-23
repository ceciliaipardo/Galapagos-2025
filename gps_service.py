from kivy.logger import Logger
from jnius import autoclass
from time import sleep

# Android GPS service implementation
PythonService = autoclass('org.kivy.android.PythonService')
PythonService.mService.setAutoRestartService(True)

Logger.info('GPS Service: Service started')

while True:
    Logger.info('GPS Service: Running...')
    sleep(60)  # Keep service alive, check every 60 seconds
