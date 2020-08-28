import subprocess
import sys


def any_action():
    trigger = int(sys.argv[1])
    if(trigger == 1): # test action
        subprocess.run(["saberlight", "white", "FF:FF:F0:01:24:AF", "50"])
    elif(trigger == 2): # start planner
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "start"])
    elif(trigger == 3): # stop planner
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "stop"])
    elif(trigger == 4): # start planner with late start
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "late"])
    elif(trigger == 5): # reply with the next task on the list
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "startNow"])


any_action()
