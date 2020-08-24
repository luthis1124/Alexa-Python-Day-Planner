import subprocess
import sys


def get_percent(perc):
    percent = {
        100: 255,
        95: 242,
        90: 229,
        85: 217,
        80: 204,
        75: 191,
        70: 178,
        65: 166,
        60: 153,
        55: 140,
        50: 127,
        45: 115,
        40: 102,
        35: 89,
        30: 76,
        25: 64,
        20: 51,
        15: 38,
        10: 25,
        5: 12,
        4: 10,
        3: 8,
        2: 5,
        1: 2,
        0: 0
    }
    return percent[int(perc)]


def light_control():
    if sys.argv[1] == "true":
        subprocess.run(["saberlight", "white", "FF:FF:F0:01:24:AF", "255"])
    elif sys.argv[1] == "false":
        subprocess.run(["saberlight", "white", "FF:FF:F0:01:24:AF", "0"])
    else:
        subprocess.run(["saberlight", "white", "FF:FF:F0:01:24:AF", str(get_percent(sys.argv[1]))])


light_control()
