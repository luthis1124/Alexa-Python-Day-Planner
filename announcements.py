import paho.mqtt.client as mqtt
import sys
# from crontab import CronTab

client = mqtt.Client()
client.connect("localhost", 1883, 60)
# cron = CronTab(user='st')

def announce():
    client.publish ("python", sys.argv[1])
    # task = cron.find_command("announcement")
    # cron.remove(task)
    # cron.write()


announce()