import subprocess
import sys
import pty
import os

# syntax for !bool


def toggle_monitors():
    filename = "/home/st/logfile"

    # command = "amixer" + "set", "Master", sys.argv[1] + "%"

    if len(sys.argv) < 2:
        sys.argv.append("durr")

    # sys.argv[0] = False
    # subprocess.run(["echo", "start", ">", "/dev/pts/5"])
    # pty.spawn(["echo", "start2", ">", "/dev/pts/5"])
    # subprocess.run(["echo", str(sys.argv[0]), ">", "/dev/pts/5"])

    filename = "/home/st/logfile"
    # with open(filename, 'a') as f:
    #     f.write(str(sys.argv[1]))
    #     f.write("\r\n")

    if sys.argv[1] == "true":

        pty.spawn(["bash", "/home/st/scripts/monitoron.sh"])

        # monitor = subprocess.run(["xset", "dpms", "force", "on"], stderr=subprocess.STDOUT)
        # # subprocess.run(["echo", str(sys.argv[0]), ">", "/dev/pts/5"])
        # print("on: " + str(monitor.stdout) + str(monitor.returncode))
        with open(filename, 'a') as f:
            f.write("on: ")
            # + str(monitor.stdout) + str(monitor.returncode))
            f.write("\r\n")

    if sys.argv[1] == "false":
        # monitor = subprocess.run(["xset", "dpms", "force", "off"], stderr=subprocess.STDOUT)
        # print("off: " + str(monitor.stdout) + str(monitor.returncode))
        with open(filename, 'a') as f:
            f.write("off: ")
            # + str(monitor.stdout) + str(monitor.returncode))
            f.write("\r\n")
        subprocess.run(["bash", "/home/st/scripts/monitoroff.sh"])


toggle_monitors()
