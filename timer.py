import time
import subprocess


while True:

    print("Starting synchronization...")

    subprocess.run([
        r".\venv\Scripts\python.exe",
        "manage.py",
        "sync_data"
    ])

    print("Starting cleanup...")

    subprocess.run([
        r".\venv\Scripts\python.exe",
        "manage.py",
        "cleanup_data"
    ])

    print("Waiting 2 minutes...")

    time.sleep(2 * 60)