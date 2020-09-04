import subprocess
import sys


def any_action():
    trigger = int(sys.argv[1])
    if(trigger == 1): # test action
        subprocess.run(["saberlight", "white", "FF:FF:F0:01:24:AF", "50"])
    elif(trigger == 2): # start planner
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "normal"])
    elif(trigger == 3): # stop planner
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "stop"])
    elif(trigger == 4): # start planner with late start
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "startlate"])
    elif(trigger == 5): #
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "startnow"])
    elif(trigger == 6): # run a yoga video
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "yoga"])
    elif(trigger == 7): # what's my task
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "currentTask"])
    elif(trigger == 8): # mark task done
        subprocess.Popen(["/home/st/Projects/Planner/.venv/bin/python", "/home/st/Projects/Planner/planner.py", "markDone"])

any_action()
