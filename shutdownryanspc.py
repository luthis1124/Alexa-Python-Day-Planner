import subprocess
import sys
import pty
import os
import paramiko

# syntax for !bool


def shutdown_pc():

    # pty.spawn(["bash", "/home/st/scripts/shutdownRyansPC.sh"])
    ryan_ip = "192.168.1.24"
    ryan_user = "st"
    ryan_key = "/home/st/.ssh/key"
    ryan_pw = "5tgb^YHN"
    ssh = paramiko.SSHClient()

    # Load SSH host keys.
    ssh.load_system_host_keys()
    # Add SSH host key automatically if needed.
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        # Connect to router using username/password authentication.
        ssh.connect(ryan_ip,
                    username=ryan_user,
                    password=ryan_pw,
                    look_for_keys=False)

        # Run command.
        # ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("echo paramiko2 >> /home/st/test")
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command("sudo shutdown +3")

        output = ssh_stdout.readlines()
        # Close connection.
        ssh.close()

        # # Analyze show ip route output
        # for line in output:
        #     print(line)
        #     # if "0.0.0.0/0" in line:
        #     #     print("Found default route:")
        #     #     print(line)

    except Exception as err:
        print(err)


shutdown_pc()
