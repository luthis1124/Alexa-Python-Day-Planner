import subprocess
import sys
import pty
import os

# vlc rtsp://admin:shouldnotbecomeone@192.168.1.22:554//h264Preview_01_main


def open_camera():
    # subprocess.run(["vlc", "rtsp://admin:shouldnotbecomeone@192.168.1.22:554//h264Preview_01_main"])
    # pty.spawn(["vlc", "--no-audio", "rtsp://admin:shouldnotbecomeone@192.168.1.22:554//h264Preview_01_main"])
    pty.spawn(["bash", "/home/st/scripts/opencamera.sh"])
    # new_env = dict(os.environ)
    # new_env['DISPLAY'] = '0.0'
    #
    # subprocess.run(["vlc", "--no-audio", "rtsp://admin:shouldnotbecomeone@192.168.1.22:554//h264Preview_01_main"],
    #                env=new_env, shell=True)

    # DISPLAY=:0

    with open("/home/st/Projects/Planner/cameralog", 'w') as f:
        
        f.write("line\r\n")
        f.write(sys.argv[2])
        
        # f.write(str(sys.argv))
        f.close()



open_camera()
