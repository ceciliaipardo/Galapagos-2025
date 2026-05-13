import subprocess, os, sys, time, base64
os.chdir(os.path.dirname(os.path.abspath(__file__)))

PACKAGE = 'org.galapagos.gct'
DEST = f'/data/data/{PACKAGE}/files/app'

# Text files: piped safely via stdin (ASCII/UTF-8, no binary issues)
TEXT_FILES = [
    'main.py', 'translations.py', 'supabase_rest_api.py',
    'gps_service.py', 'GalapagosCarTracking_translated.kv',
]
# Binary files: must go via base64 to avoid LF/CRLF corruption in adb pipe
BINARY_FILES = [
    'galapago_logo.png', 'lang_icon.png',
]

def adb(*args, input=None):
    return subprocess.run(['adb'] + list(args),
                          input=input, capture_output=True)

def push_text(f):
    with open(f, 'rb') as fh:
        data = fh.read()
    proc = adb('shell', f'run-as {PACKAGE} sh -c "cat > {DEST}/{f}"', input=data)
    return proc.returncode == 0, proc.stderr

def push_binary(f):
    """Push a binary file by encoding it as base64 chunks, then decoding on device."""
    with open(f, 'rb') as fh:
        data = fh.read()
    b64 = base64.b64encode(data).decode('ascii')

    # Delete stale copy first so we start fresh
    adb('shell', f'run-as {PACKAGE} rm -f {DEST}/{f}')

    # Write base64 in lines of 76 chars directly into a temp file via cat>
    # Each chunk is small enough for the adb pipe to handle correctly as ASCII
    CHUNK = 65536  # 64 KB of base64 text per call (~48 KB binary)
    tmp = f'/data/data/{PACKAGE}/files/app/_tmp_b64'
    adb('shell', f'run-as {PACKAGE} rm -f {tmp}')

    for i in range(0, len(b64), CHUNK):
        chunk = b64[i:i+CHUNK]
        chunk_bytes = chunk.encode('ascii')
        proc = adb('shell', f'run-as {PACKAGE} sh -c "cat >> {tmp}"', input=chunk_bytes)
        if proc.returncode != 0:
            return False, proc.stderr

    # Decode on device
    proc = adb('shell',
               f'run-as {PACKAGE} sh -c "base64 -d {tmp} > {DEST}/{f} && rm -f {tmp}"')
    return proc.returncode == 0, proc.stderr

# --- Push text files ---
for f in TEXT_FILES:
    ok, err = push_text(f)
    status = "OK" if ok else f"FAIL: {err[:80]}"
    print(f'  {f}: {status}')

# --- Push binary files ---
for f in BINARY_FILES:
    ok, err = push_binary(f)
    status = "OK" if ok else f"FAIL: {err[:80]}"
    print(f'  {f}: {status}')

# Verify binary sizes
print('\nVerifying binary files:')
for f in BINARY_FILES:
    local_size = os.path.getsize(f)
    proc = adb('shell', f'run-as {PACKAGE} wc -c {DEST}/{f}')
    device_size = proc.stdout.decode().split()[0] if proc.stdout else '?'
    match = '✓' if str(local_size) == str(device_size) else '✗ MISMATCH'
    print(f'  {f}: local={local_size} device={device_size} {match}')

# Clear cached pyc files
adb('shell', f'run-as {PACKAGE} sh -c '
    f'"rm -f {DEST}/main.pyc {DEST}/translations.pyc '
    f'{DEST}/supabase_rest_api.pyc {DEST}/gps_service.pyc"')

adb('shell', 'am', 'force-stop', PACKAGE)
time.sleep(1)
adb('shell', 'am', 'start', '-n', f'{PACKAGE}/org.kivy.android.PythonActivity')

print('\nDone! App restarting.')
