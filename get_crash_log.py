import subprocess, time, sys

ADB = r'C:\Users\npc04\AppData\Local\Android\Sdk\platform-tools\adb.exe'
PACKAGE = 'org.galapagos.gct'

def adb(*args, **kwargs):
    return subprocess.run([ADB] + list(args), capture_output=True, text=True, **kwargs)

print("Clearing logcat...")
adb('logcat', '-c')
adb('shell', 'am', 'force-stop', PACKAGE)
time.sleep(1)
print("Launching app...")
adb('shell', 'am', 'start', '-n', f'{PACKAGE}/org.kivy.android.PythonActivity')
time.sleep(6)

print("Capturing logs...")
result = adb('logcat', '-d', '-v', 'brief')
lines = result.stdout.splitlines()

# Print all python-tagged lines
for line in lines:
    if 'python' in line.lower() or 'traceback' in line.lower() or 'error' in line.lower() or 'exception' in line.lower() or 'syntax' in line.lower():
        print(line)
