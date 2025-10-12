import time
import os
import sys

COUNT=0
while True:
    # Run your Django management command
    exit_code = os.system(f"{sys.executable} manage.py auto_escalate_tickets")

    # Print status for debugging
    print("Executed auto_escalate_tickets with exit code:", exit_code)
    print(COUNT, " times run successfully.")

    # Wait 2 minutes (120 seconds)
    COUNT += 1
    time.sleep(10)
