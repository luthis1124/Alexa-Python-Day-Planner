import json
import calendar
from datetime import date
from datetime import datetime
from prompt_toolkit import prompt
from prompt_toolkit.history import FileHistory
from crontab import CronTab
import paho.mqtt.client as mqtt
import os
from prompt_toolkit.completion import Completer, Completion
import click
from fuzzyfinder import fuzzyfinder
# import sys

# first, plan the day
# set up half hour blocks
# set wake and bed time
# set and load default schedule to json
# set up daily stoic quote
# 'next thing' variable
# output to alexa
# console to add events to calendar, then saved to json extratasks.json


"""
alltasks    dict
            dailycategoryname   dailylistname
                                dailytask1      dailytask1name
                                                key value, key value
                                dailytask2      dailytask2name
                                                key value, key value
            extracategoryname   extralistname
                                extratask1      extratask1name
                                                key value, key value
                                extratask2      extratask2name
                                                key value, key value
"""

"""
all{daily{task1{name, date, time}, task2{}}, extra}
"""


path = "/home/st/Projects/Planner"
filename = "testing.json"

all_tasks = {}
dailylist = {}
extralist = {}

dailylistname = "dailylist"
extralistname = "extralist"
dailycategoryname = "daily"
extracategoryname = "extra"

hour = "hour"
minute = "minutes"
estimate = "estimate"


client = mqtt.Client()
client.connect("localhost", 1883, 60)

cron = CronTab(user='st')

menu_items = ['add daily', 'add extra', 'del d', 'del e', 'add extra', 'publish', 'save', 'load', 'populate', 'list', 'cron', 'x']

class menuCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        matches = fuzzyfinder(word_before_cursor, menu_items)
        for m in matches:
            yield Completion(m, start_position=-len(word_before_cursor))
    
    # def fuckoff(self, x):
    #     quit()

def main():
    while True:
        user_input = prompt(u'>', completer=menuCompleter())
        # click.echo_via_pager(user_input)
        if 'x' == user_input:
            # client.publish ("python", "exiting")
            # break
            del user_input
            quit()
            # sys.exit()

main()