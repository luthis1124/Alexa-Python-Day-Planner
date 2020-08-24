import sys
from crontab import CronTab

cron = CronTab(user='st')

tasklist = cron.find_command("announcement")

for job in tasklist:
    cron.remove(job)
    cron.write()
