import subprocess
import sys
import os

# Start the evolution run in a detached process with unbuffered output
subprocess.Popen(
    [sys.executable, "-u", "run_evolution.py", "../build"],
    stdout=open("../build/run_logs/v2_restart_bg.log", "a"),
    stderr=subprocess.STDOUT,
    cwd=os.path.dirname(os.path.abspath(__file__)),
    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
)
print("Evolution started in background. Check ../build/run_logs/v2_restart_bg.log")
