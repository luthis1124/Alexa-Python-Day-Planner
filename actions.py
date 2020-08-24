import subprocess
import sys


def any_action():
    trigger = int(sys.argv[1])
    if(trigger == 1):
        subprocess.run(["saberlight", "white", "FF:FF:F0:01:24:AF", "50"])
    elif(trigger == 2):
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "start"])
    elif(trigger == 3):
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "stop"])


any_action()
