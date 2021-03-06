import json
import random
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

from operator import itemgetter

from enum import Enum

import vlc

import time

import subprocess
import sys
import pty
import os

class planner:

    # saving 'today's quote'
    # implement going to bed now
    # implement going to sleep now

    class menuCompleter(Completer):
        def __init__(self, menu_items):
            self.menu_items = menu_items
        def get_completions(self, document, complete_event):
            word_before_cursor = document.get_word_before_cursor(WORD=True)
            matches = fuzzyfinder(word_before_cursor, self.menu_items)
            for m in matches:
                yield Completion(m, start_position=-len(word_before_cursor))

    class dayPhase(Enum):

        daystart = "daystart"
        lights_on = "lights_on"
        wake = "wake"
        mid_morning = "mid_morning"
        midday = "midday"
        afternoon = "afternoon"
        dinner = "dinner"
        evening = "evening"
        lights_off = "lights_off"

    class action(Enum):

        announce = "announce"
        play_video = "play_video"
        light_toggle = "light_toggle"
        light_fade = "light_fade"       

    def __init__(self):
        self.path = "/home/st/Projects/Planner/"
        self.filename = "testing.json"

        self.all_tasks = {}
        self.dayPlan = {}
        self.extralist = {}
        self.defaultTasks = {}
        self.extraqueue = {} # all extra tasks
        self.attempedExtraTasks = {}
        self.dayPhases_TOD = {}
        # dayPhase = self.dayPhase()
        
        self.yogaVideos = {}
        

        self.dailylistname = "dailylist"
        self.extralistname = "extralist"
        self.dailycategoryname = "daily"
        self.extracategoryname = "extra"
        self.timecategoryname = "times"
        self.dayPhasesname = "dayPhases"

        self.hour_name = "hour"
        self.minute_name = "minute"
        self.duration_name = "duration"
        self.estimate_name = "estimate"

        # this section should be moved to an init to set day type
        self.early_daystart = [6,1]
        self.late_daystart = [7,1]
        self.task_start = [0,0]

        self.timeset = False

        # set early or late times
        # daystart = early_daystart

        # increment day parts based time since last section
        # lights_on = [5, 40]
        # wake = daystart
        # mid_morning = [wake[0] + 3, 30]
        # midday = [mid_morning[0] + 3, 0]
        # afternoon = [midday[0] + 3, 0]
        # dinner = [afternoon[0] + 2, 0]
        # evening = [dinner[0] + 4, 0]
        # lights_off = [evening[0], 20]

        self.lights_on_TOD = []
        self.wake_TOD = []
        self.mid_morning_TOD = []
        self.midday_TOD = []
        self.afternoon_TOD = []
        self.dinner_TOD = []
        self.evening_TOD = []
        self.lights_off_TOD = []

        self.client = mqtt.Client()
        self.client.connect("localhost", 1883, 60)
        self.cron = CronTab(user='st')

        self.menu_items = ['add daily', 'add extra', 'del d', 'del e', 'publish', 'save', 'load', 'populate', 'list', 'cron', 'x', 'clear', 'default', 'clear cron', 'current task', 'next task']

    def main(self):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M")
        print("Today's date:", dt_string)
        while True:
            try:
                Completer = self.menuCompleter(self.menu_items)
                # Completer.__init__()
                user_input = prompt(u'>', history=FileHistory('history.txt'), completer=Completer)
                # click.echo_via_pager(user_input)
                if 'del d' == user_input:
                    self.delete_daily()
                elif 'del e' == user_input:
                    self.delete_extra()
                elif 'add daily' == user_input:
                    self.add_daily()
                elif 'add extra' == user_input:
                    print("no menu option")
                elif 'default' == user_input:
                    self.default_daily_tasks()
                elif 'publish' == user_input:
                    self.publish()
                elif 'days' == user_input:
                    self.days_left()
                elif 'cron' == user_input:
                    self.list_cron()
                elif 'list' == user_input:
                    self.list_jobs()
                elif 'current task' == user_input:
                    self.getCurrentTask()
                elif 'next task' == user_input:
                    self.getNextTask()
                # elif 'populate' == user_input:
                #     self.sample_populate()
                elif 'save' == user_input:
                    self.save()
                elif 'load' == user_input:
                    self.load()
                elif 'reset' == user_input:
                    self.reset()
                elif 'test' == user_input:
                    self.set_initial_conditions("normal")
                # elif 'say' == user_input:
                #     self.say(user_input)
                # elif 'clear' == user_input:
                #     say(user_input)
                elif 'clear cron' == user_input:
                    self.clear_cron()
                elif 'x' == user_input:
                    # client.publish ("python", "exiting")
                    break
                    # quit()
                    # sys.exit()
                elif 'date' == user_input:
                    print(datetime.now())
                else:
                    print('invalid input')
            except EOFError:
                break

    def set_initial_conditions(self, _variation):
        if _variation == "normal":
            daystart = self.early_daystart
        elif _variation == "startlate":
            daystart = self.late_daystart
        elif _variation == "startnow":
            # TODO make sure this doesn't spill over into the next time phase ie getting up at 9:59
            now = datetime.now()
            daystart = [now.hour, now.minute + 1]
            self.client.publish ("python", "Don't worry, I'll help you get up.")

        # print("yes, we set the initial conditions")

        self.lights_on_TOD = [daystart[0] - 1, 40]
        self.wake_TOD = daystart
        self.mid_morning_TOD = [10,0]
        # self.mid_morning_TOD = [self.wake_TOD[0] + 3, 30]
        self.midday_TOD = [12, 0]
        self.afternoon_TOD = [self.midday_TOD[0] + 3, 0]
        self.dinner_TOD = [self.afternoon_TOD[0] + 2, 0]
        self.evening_TOD = [self.dinner_TOD[0] + 3, 0]
        self.lights_off_TOD = [self.evening_TOD[0], 20]

        self.dayPhases_TOD.clear()
        self.dayPhases_TOD["variation"] = [0, _variation]

        self.dayPhases_TOD[self.dayPhase.daystart.value] = daystart
        self.dayPhases_TOD[self.dayPhase.lights_on.value] = self.lights_on_TOD
        self.dayPhases_TOD[self.dayPhase.wake.value] = self.wake_TOD
        self.dayPhases_TOD[self.dayPhase.mid_morning.value] = self.mid_morning_TOD
        self.dayPhases_TOD[self.dayPhase.midday.value] = self.midday_TOD
        self.dayPhases_TOD[self.dayPhase.afternoon.value] = self.afternoon_TOD
        self.dayPhases_TOD[self.dayPhase.dinner.value] = self.dinner_TOD
        self.dayPhases_TOD[self.dayPhase.evening.value] = self.evening_TOD
        self.dayPhases_TOD[self.dayPhase.lights_off.value] = self.lights_off_TOD

        # print(self.dayPhases_TOD)

        # print (f"lights on: {lights_on}")

        self.timeset = True

        #default 
        # lights_on = [5,40]
        # wake = [6,1]
        # mid_morning = [10,0]
        # midday = [12,0]
        # afternoon = [15,0]
        # dinner = [17,0]
        # evening = [21,0]
        # lights_off = [21,20]

    def populateYogaVideos(self):
        vid1 = {
            "name": "10 min Morning Yoga Stretch ☀️ SUNRISE YOGA | Sarah Beth Yoga",
            "link": "https://www.youtube.com/watch?v=8iDHLhOWFPE",
            "duration": 11
        }
        vid2 = {
            "name": "10 minute Morning Yoga for Beginners",
            "link": "https://www.youtube.com/watch?v=VaoV1PrYft4",
            "duration": 10
        }
        vid3 = {
            "name": "10 min Seated Morning Yoga Stretch for Stiff & Achey Muscles | Sarah Beth Yoga",
            "link": "https://www.youtube.com/watch?v=aLfY0cH9oW4",
            "duration": 12
        }
        vid4 = {
            "name": "15 minute Super Chill Yoga Stretches for Relaxation | Sarah Beth Yoga",
            "link": "https://www.youtube.com/watch?v=LAve8xHkf_M",
            "duration": 16
        }
        vid5 = {
            "name": "15 min Full Body Morning Yoga Flow ☀️FEEL GREAT",
            "link": "https://www.youtube.com/watch?v=OlE7FFX5utg",
            "duration": 18
        }
        vid6 = {
            "name": "15 minute Energizing Morning Yoga Routine | Sarah Beth Yoga",
            "link": "https://www.youtube.com/watch?v=T0_X02wY6YI",
            "duration": 15
        }
        vid7 = {
            "name": "15 minute Morning Yoga Routine | Full Body Yoga Flow",
            "link": "https://www.youtube.com/watch?v=XCIviBT3Txc",
            "duration": 16
        }
    
    def play_video(self, _add_name, _duration):
        cmd = (f'bash /home/st/scripts/play.sh /home/st/Videos/{_add_name}.mp4')
        task = self.cron.new(command=cmd)
        task.hour.on(self.task_start[0])
        task.minute.on(self.task_start[1])
        self.cron.write()

        self.task_start[1] += _duration
        while (self.task_start[1] > 59):
            self.task_start[1] -= 60
            self.task_start[0] += 1

    def play_youtube(self, _name):
        
        cmd = f"/home/st/scripts/video.sh {_name}"
        self.log(cmd)
        subprocess.run(["bash", "/home/st/scripts/video.sh", "https://www.youtube.com/watch?v=aLfY0cH9oW4"])

    def declare_extra_tasks(self):
        #some tasks to publish
                
        announce = self.action.announce.value
        
        self.add_extra_internal(announce, ["add spanish daily practice", 20])
            
        
        self.add_extra_internal(announce, ["do the ali express order.", 20])

        self.add_extra_internal(announce, ["frequent reminders, such as vape and sit up straight", 20])
        self.add_extra_internal(announce, ["washing should be an extra task", 20])
        self.add_extra_internal(announce, ["loop tasks, ie start thing, end thing, ie washing, baking", 20])
        self.add_extra_internal(announce, ["recurring tasks on longer frequency ie vacuum room, shave, washing", 20])
        self.add_extra_internal(announce, ["add task for reading journal", 20])
        self.add_extra_internal(announce, ["check if tasks get completed", 20])
        self.add_extra_internal(announce, ["congratulations message for each task", 20])
        self.add_extra_internal(announce, ["enable better easier flexibility for changing day start times etc", 20])
        self.add_extra_internal(announce, ["late night option", 20])

        self.add_extra_internal(announce, ["600 hours in one year for spanish", 20])
        self.add_extra_internal(announce, ["add fruit to diet", 20])
        self.add_extra_internal(announce, ["add novelty to the tasks", 20])
        self.add_extra_internal(announce, ["todays playlist ( based on weather? )", 20])
        self.add_extra_internal(announce, ["extra tasks currently fill up with read until next task. needs a rewrite", 20])

        self.add_extra_internal(announce, ["alexa, pause my planner", 20])
        self.add_extra_internal(announce, ["lets do some yoga/workout", 20])
        self.add_extra_internal(announce, ["what's my current task / next task", 20])
        self.add_extra_internal(announce, ["reschedule/cancel this task", 20])
        self.add_extra_internal(announce, ["move to a saving/loading framework", 20])
        self.add_extra_internal(announce, ["all tasks go into a single list and that list is published", 20])
        self.add_extra_internal(announce, ["the evening slump, when Ryan is not here. Keep engaged on something, keep busy, stay motivated. further to this, stretching and exercising are still productive.", 20])
        
        
        self.add_extra_internal(announce, ["turn on monitors for yoga", 20])
        self.add_extra_internal(announce, ["ryan's bedtime light routine", 20])
        self.add_extra_internal(announce, ["combine node-red flows", 20])
        self.add_extra_internal(announce, ["make single controller.py for all inputs if you can receive the device as part of args[]", 20])
        self.add_extra_internal(announce, ["list of friends to message", 20])
        self.add_extra_internal(announce, ["fix the videos and extra tasks", 20])
        
        self.add_extra_internal(announce, ["fill and scan your job acceptance", 20])
        self.add_extra_internal(announce, ["alexa, wrap up for the day (late finish)", 20])
        self.add_extra_internal(announce, ["download extra yoga videos for novelty", 20])
        self.add_extra_internal(announce, ["add novelty wherever possible", 20])
        
        self.add_extra_internal(announce, ["get through your emails.", 20])
        self.add_extra_internal(announce, ["incorporate the breath holding practice.", 20])   
        self.add_extra_internal(announce, ["make some bread.", 25])
        
        self.add_extra_internal(announce, ["fix the green drill under the bed.", 60])
        self.add_extra_internal(announce, ["fix the pyrography pen under the bed.", 60])
        self.add_extra_internal(announce, ["try to fix rebeccas blue nokia with the replacement screen.", 20])       
        self.add_extra_internal(announce, ["reminders of daily quote / mindset before meals and throughout the day.", 20])       

    def add_extra_internal(self, _action, _data):
        
        # _data = text, duration

        # dayplan: [ID] = taskattribs
        # taskattribs: action data hour minute duration

        text = _data[0]
        duration = _data[1]
        # extraqueue: [text] = taskattribs
        # taskattribs = action data duration
        taskattribs = {"action": _action, "data": _data, "duration": duration, "done": "false", "day": ""}
        self.extraqueue[text] = taskattribs

    def sanity_check(self, _next_section_start, _name_of_current_section):
        free_hours = _next_section_start[0] - self.task_start[0] # hours difference
        free_minutes = (free_hours * 60) + (_next_section_start[1] - self.task_start[1]) # total minutes difference
        if (free_minutes < 0):
            error_msg = f"error. the {_name_of_current_section} section extends into the next section."
            self.client.publish ("python", error_msg)
            print(error_msg)
            quit()
        
    def getDayName(self, daynum):
        dayString = ""
        if daynum == 0:
            dayString = "Monday"
        if daynum == 1:
            dayString = "Tuesday"
        if daynum == 2:
            dayString = "Wednesday"
        if daynum == 3:
            dayString = "Thursday"
        if daynum == 4:
            dayString = "Friday"
        if daynum == 5:
            dayString = "Saturday"
        if daynum == 6:
            dayString = "Sunday"

        return dayString

    def default_daily_tasks(self):

        # for ease of use, just run default
        self.clear_cron()

        # this line should no longer be needed very soon. tasks should come from the file
        # or the method gets updated so we don't get duplicates.
        # self.declare_extra_tasks()
        self.load()
        # for now, we are resetting the extratasks fields
        for text, attribs in self.extraqueue.items():
            attribs["day"] = ""
            attribs["done"] = "false"
        
        # clear the day plan loaded from the file because duh we are generating it here
        self.dayPlan.clear()
        #testing confirmed, loading from file for extra tasks is 100%
        
        self.task_start = [0,0]

        if self.timeset == False:
            self.set_initial_conditions("normal")
            # set to early start if not already set

        
        # pre morning -----------------------------------------------------------------------------

        phase = self.dayPhase.lights_on.value

        self.task_start[0] = self.lights_on_TOD[0]
        self.task_start[1] = self.lights_on_TOD[1]

        # lights don't need the sanity check

        self.light(1, 5)
        self.light(2, 4)
        self.light(3, 4)
        self.light(4, 4)
        self.light(5, 3)
        self.light(10, 4) #6am
        self.light(15, 4)
        self.light(20, 3)
        self.light(40, 3)
        self.light(60, 3)
        self.light(80, 3)
        self.light(100, 0) #620am
        
        # wake -----------------------------------------------------------------------------
        self.task_start[0] = self.wake_TOD[0]
        self.task_start[1] = self.wake_TOD[1]

        d0 = date.today()
        d1 = date(2076, 7, 23)
        delta = d1 - d0

        phase = self.dayPhase.wake.value
        announce = self.action.announce.value
        video = self.action.play_video.value

        now = datetime.now()
        
        welcomeMessage = f"Welcome to {self.getDayName(now.day)}. You will never live this day again."
        
        self.add_daily_internal(announce, [welcomeMessage, 1], phase)
        self.add_daily_internal(announce, [("You have " + str(delta.days) + " days left to live."), 1], phase)
        self.add_daily_internal(announce, ["you are insignificant. but your actions mean everything.", 1], phase)
        self.add_daily_internal(announce, ["now is the most important part of the day. . Win the morning and you win the day.", 1], phase)
        self.add_daily_internal(announce, ["its time to get up. Yoga will start soon. lay out the mat and enter childs pose.", 1], phase)  

        # play video: action [name, duration] phase
        self.add_daily_internal(video, ["morning", 16], phase)

        self.add_daily_internal(announce, [(f"Here is todays quote to meditate on. {self.stoicQuotes()}"), 3], phase)
        self.add_daily_internal(announce, ["go boil the jug and prepare your breakfast.", 4], phase)
        self.add_daily_internal(announce, ["its time for your cold shower. dont be a wimp.", 20], phase)
        self.add_daily_internal(announce, ["you should be getting dressed and making your bed by now.", 5], phase)
        self.add_daily_internal(announce, ["its breakfasttime.", 25], phase)
        self.add_daily_internal(announce, ["clean your teeth and then the kitchen", 20], phase)
        self.add_daily_internal(announce, ["now clean your room.", 10], phase)
        self.add_daily_internal(announce, ["message your grandfather and your parents.", 40], phase)
        

        # -----------------------------------------------------------------------------

        # sanity check
        self.sanity_check(self.mid_morning_TOD, "morning")
        # extra tasks section
        nextphase_TOD = self.mid_morning_TOD
        self.schedule_extra(nextphase_TOD, phase)
        
        # ------------------------------------ mid morning -----------------------------------------
        self.task_start[0] = self.mid_morning_TOD[0]
        self.task_start[1] = self.mid_morning_TOD[1]

        phase = self.dayPhase.mid_morning.value

        self.add_daily_internal(announce, ["it's time for a break. Todays snack is eggs on toast, followed by fruit.", 20], phase)
        self.add_daily_internal(announce, ["plan for dinner.", 20], phase)
        self.add_daily_internal(announce, ["reading time.", 20], phase)

        # -----------------------------------------------------------------------------

        # sanity check
        self.sanity_check(self.midday_TOD, "mid morning")
        # extra tasks section
        nextphase_TOD = self.midday_TOD
        self.schedule_extra(nextphase_TOD, phase)

        # ------------------------------------- midday ----------------------------------------
        self.task_start[0] = self.midday_TOD[0]
        self.task_start[1] = self.midday_TOD[1]

        phase = self.dayPhase.midday.value
        
        self.add_daily_internal(announce, ["its lunch time. lunch will be a tuna sandwich. Don't forget a piece of fruit.", 20], phase)

        # -----------------------------------------------------------------------------

        # sanity check
        self.sanity_check(self.afternoon_TOD, "midday")
        # extra tasks section
        nextphase_TOD = self.afternoon_TOD
        self.schedule_extra(nextphase_TOD, phase)

        # ------------------------------------- afternoon ----------------------------------------
        self.task_start[0] = self.afternoon_TOD[0]
        self.task_start[1] = self.afternoon_TOD[1]

        phase = self.dayPhase.afternoon.value

        # -----------------------------------------------------------------------------

        # sanity check
        self.sanity_check(self.dinner_TOD, "afternoon")
        # extra tasks section
        nextphase_TOD = self.dinner_TOD
        self.schedule_extra(nextphase_TOD, phase)

        # ------------------------------------- dinner ----------------------------------------
        self.task_start[0] = self.dinner_TOD[0]
        self.task_start[1] = self.dinner_TOD[1]

        phase = self.dayPhase.dinner.value

        self.add_daily_internal(announce, ["it's time to prepare and eat dinner.", 90], phase)
        self.add_daily_internal(announce, ["with dinner done, check your plans for tomorrow. its saturday.", 120], phase)
        

        # -----------------------------------------------------------------------------

        # ------------------------------------ evening -----------------------------------------
        self.task_start[0] = self.evening_TOD[0]
        self.task_start[1] = self.evening_TOD[1]

        phase = self.dayPhase.evening.value

        self.add_daily_internal(announce, ["well done, clean your teeth and you may read.", 30], phase)
        self.add_daily_internal(announce, ["its time to wrap up for the day.", 2], phase)
        self.add_daily_internal(announce, ["its time to reflect on your day.", 5], phase)
        self.add_daily_internal(announce, ["now consider how insignificant you are.", 5], phase)
        self.add_daily_internal(announce, ["Write in the journal.", 10], phase)
        self.add_daily_internal(announce, ["prepare space for yoga. make sure volume is appropriate for your morning routine.", 15], phase)

        # play video: action [name, duration] phase
        self.add_daily_internal(video, ["evening", 15], phase)

        self.add_daily_internal(announce, ["you are done now. pack up and clean your room. Make sure you have space for yoga tomorrow morning.", 5], phase)
        self.add_daily_internal(announce, ["fill your drink bottle.", 3], phase)
        self.add_daily_internal(announce, ["now get into bed you little shit.", 4], phase)
        self.add_daily_internal(announce, ["well done today. You had a cold shower, were on time for each task, cleaned the kitchen, worked on the planner, kept in contact with your friends and family, did the washing, cleaned your room, planned for dinner, prepared for and had a good interview, ate well, exercised, and took control of your life.", 3], phase)
        self.add_daily_internal(announce, ["goodnight, look forward to tomorrow.", 1], phase)

        # -----------------------------------------------------------------------------

        #evening lights start at 9pm
        phase = self.dayPhase.lights_off.value


        self.task_start[0] = self.lights_off_TOD[0]
        self.task_start[1] = self.lights_off_TOD[1]
        self.light(95, 5)
        self.light(80, 5)
        self.light(75, 5)
        
        self.light(60, 5)
        self.light(40, 5)
        self.light(20, 5) 
        
        self.light(5, 1)
        self.light(4, 1)
        self.light(3, 1)
        self.light(2, 1)
        self.light(1, 1)
        self.light(0, 1)

        self.publish()

        self.all_tasks.clear()
        
        self.all_tasks.update({self.extracategoryname: self.extraqueue})
        self.all_tasks.update({self.dailycategoryname: self.dayPlan})
        # self.all_tasks.update({self.dayPhasesname: self.dayPhases_TOD})

        # print(self.all_tasks)
        # for ID, attribs in self.dayPlan.items():
        #     print(attribs["data"])
        
    def add_daily(self):
        add_name = prompt('reminder text: ')
        add_hours = prompt('at hour: ')
        add_minutes = prompt('at minute: ')
        taskattribs = {self.hour_name: add_hours, self.minute_name: add_minutes}
        
        self.dayPlan[add_name] = taskattribs

        self.all_tasks.update({self.dailycategoryname: self.dayPlan})

        print("Don't forget to SAVE!! ..and publish when ready")
        self.client.publish ("python", "task created and ready to publish")

    def light(self, _level, _duration):

        cmd = f'python /home/st/pythonProjects/alexaVolume/venv/lightControllerMain.py {_level}'
        task = self.cron.new(command=cmd)
        task.hour.on(self.task_start[0])
        task.minute.on(self.task_start[1])
        self.cron.write() 

        self.task_start[1] += _duration
        while (self.task_start[1] > 59):
            self.task_start[1] -= 60
            self.task_start[0] += 1

    def schedule_extra(self, _end_of_extra_time, _dayPhase):

        total_hours = _end_of_extra_time[0] - self.task_start[0]
        total_minutes = _end_of_extra_time[1] - self.task_start[1] + (total_hours * 60)
        #total minutes is what we have to fit extra tasks into
        
        #we should add tasks in, until we can't add any more, and then add reading time
        #but then for the next extra task time block, how do we know which tasks have been added?
        #It must be a queue system, so tasks get chucked out of extralist[] and into attempted[]?
        #fuck it, that will work for now. 

        now = datetime.now()
        
        for text, taskattribs in self.extraqueue.items():
            # extraqueue: [text] = taskattribs
            # taskattribs = action data duration
            # taskattribs = {"action": _action, "data": _data, "duration": duration}

            duration = taskattribs["duration"]
            action = taskattribs["action"]
            data = taskattribs["data"]
            done = taskattribs["done"]
            day = taskattribs["day"]

            if (day != now.day and done == "false"):

                if total_minutes > duration:
                    total_minutes -= duration

                    if action == self.action.announce.value:
                        duration = data[1]

                        extra_taskattribs = {"action": action, "data": data, "hour": self.task_start[0], "minute": self.task_start[1], 
                            "duration": duration, "phase": _dayPhase}
                        
                        ID = f"announce{self.task_start[0]}{self.task_start[1]}"
                        self.dayPlan[ID] = extra_taskattribs

                        # now update the extra tasks queue to mark as scheduled
                        self.extraqueue[text]["day"] = now.day
                        
                        self.task_start[1] += duration
                        while (self.task_start[1] > 59):
                            self.task_start[1] -= 60
                            self.task_start[0] += 1
                        
                    elif action == self.action.play_video.value:
                        duration = data[1]

                        self.task_start[1] += duration
                        while (self.task_start[1] > 59):
                            self.task_start[1] -= 60
                            self.task_start[0] += 1
                
                else: # if total minutes remaining is less than the duration of the next task

                    duration = total_minutes
                    data[0] = "you get to read until the next task"
                    data[1] = duration
                    
                    taskattribs = {"action": self.action.announce.value, "data": data, "hour": self.task_start[0], "minute": self.task_start[1], "duration": duration, "phase": _dayPhase}
                    
                    ID = f"announce{self.task_start[0]}{self.task_start[1]}"
                    self.dayPlan[ID] = taskattribs
                    break

    def add_daily_internal(self, _action, _data, _dayPhase):
        # this method only adds to the dayplan json with the time to start the task

        # dayplan: [ID] = taskattribs
        # taskattribs: action data hour minute duration

        # TODO add phase to taskattribs
        duration = 0
        if _action == self.action.announce.value:
            # announce: action [text, duration] phase
            # text = _data[0]
            duration = _data[1]
            if duration <= 0:
                duration = 1
            
            taskattribs = {"action": _action, "data": _data, "hour": self.task_start[0], "minute": self.task_start[1], "duration": duration, "phase": _dayPhase}
            ID = f"announce{self.task_start[0]}{self.task_start[1]}"
            self.dayPlan[ID] = taskattribs
            # self.defaultTasks[text] = taskattribs

            self.task_start[1] += duration
            while (self.task_start[1] > 59):
                self.task_start[1] -= 60
                self.task_start[0] += 1

        elif _action == self.action.play_video.value:
            # play video: action [name, duration] phase
            # _add_name, _duration
            # name = _data[0]
            duration = _data[1]
            if duration <= 0:
                duration = 1

            taskattribs = {"action": _action, "data": _data, "hour": self.task_start[0], "minute": self.task_start[1], "duration": duration, "phase": _dayPhase}
            ID = f"play_video{self.task_start[0]}{self.task_start[1]}"
            self.dayPlan[ID] = taskattribs

            self.task_start[1] += duration
            while (self.task_start[1] > 59):
                self.task_start[1] -= 60
                self.task_start[0] += 1

        elif _action == self.action.light_toggle.value:
            # light_toggle: ???
            x = True
            # lights act independently of task_start and other tasks
        elif _action == self.action.light_fade.value:
            # light_fade: ???

            # add to the dayplan list
            taskattribs = {"action": _action, "data": _data, "hour": self.task_start[0], "minute": self.task_start[1], "duration": duration, "phase": _dayPhase}
            # lights act independently of task_start and other tasks

    def add_weekend_task(self):
        return

    def days_left(self):
        d0 = date.today()
        d1 = date(2076, 7, 24)
        delta = d1 - d0
        print(delta.days)
        self.client.publish ("python", "Welcome to today. You have " + str(delta.days) + " days left to live.")

    def publish(self):
        
        # self.client.publish ("python", "publishing tasks")

        # publish method depends on action type            

        # print("publishing")
        for ID, attribs in self.dayPlan.items():
            # taskattribs: action data hour minute duration
            
            time_hour = attribs[self.hour_name]
            time_minute = attribs[self.minute_name]
            data = attribs["data"]
            action = attribs["action"]
            duration = attribs[self.duration_name]

            cmd = ""
            
            # print(f"ID {ID} {action} {str(self.action.announce)} {self.action.announce.value}")            

            if action == self.action.announce.value:
                # announce: action [text, duration] phase
                announcement = data[0]
                if duration > 1:
                    cmd = f'source /home/st/Projects/Planner/.venv/bin/activate ; python /home/st/Projects/Planner/announcements.py "{announcement} you have {duration} minutes"'
                elif duration == 1:
                    cmd = f'source /home/st/Projects/Planner/.venv/bin/activate ; python /home/st/Projects/Planner/announcements.py "{announcement}"'    

            elif action == self.action.play_video.value:
                # play video: action [name, duration] phase
                name = data[0]

                # cmd = (f'bash /home/st/scripts/monitoron.sh ; bash /home/st/scripts/play.sh /home/st/Videos/{name}.mp4')

            elif action == self.action.light_toggle.value:
                x = True
            elif action == self.action.light_fade.value:
                x = True

            task = self.cron.new(command=cmd,comment=ID)
            task.hour.on(time_hour)
            task.minute.on(time_minute)
            self.cron.write()

        # dailylist.clear()

    def list_cron(self):
        for job in self.cron:
            print(job)

    def list_jobs(self):
        print(f"jobs in {self.dailycategoryname}")
        for ID, attribs in self.dayPlan.items():
            print("task: ", ID)
            for key in attribs:
                print(key + ":", attribs[key])
        print(f"jobs in {self.extracategoryname}")
        for ID, attribs in self.extraqueue.items():
            print("task: ", ID)
            for key in attribs:
                print(key + ":", attribs[key])

    def markTaskDone(self):
        taskText = self.getCurrentTaskInternal()
        for ID, attribs in self.extraqueue.items():
            if (taskText == ID):
                self.extraqueue[taskText]["done"] = "true"

        self.client.publish ("python", "well done on completing your task!")

    def getCurrentTask(self):
        say = f"your current task is {self.getCurrentTaskInternal()}"
        self.client.publish ("python", say)

    def getCurrentTaskInternal(self):
        # TODO on the minute of starting, current task reports the previous task
        # this happens in if (len(tasks) == 1):

        now = datetime.now()
        hour = now.hour
        minute = now.minute

        tasks = []
        tasks_this_hour = []
        tasks_previous_hours = []

        

        textID = ""

        if self.dayPlan:

            for ID, attribs in self.dayPlan.items():
                # taskattribs = {"action": _action, "data": _data, "hour": self.task_start[0], "minute": self.task_start[1], "duration": duration, "phase": _dayPhase}
                task_hour = attribs["hour"]
                task_minute = attribs["minute"]
                if(task_hour == hour):
                    tasks_this_hour.append((ID, task_hour, task_minute))
                if(task_hour < hour):
                    tasks_previous_hours.append((ID, task_hour, task_minute))

            # print("tasks to check, this hour:")
            # print(tasks_this_hour)
            # print("tasks previous hours:")
            # print(tasks_previous_hours)

            for attribs in tasks_this_hour:
                if(attribs[2] <= minute):
                    tasks.append(attribs)
            
            if (len(tasks) == 1):
                # print("len tasks == 1")

                ID = tasks[0][0]
                # print (f"id is {tasks[0][0]}")
                attribs = self.dayPlan[ID]
                data = attribs["data"]
                duration = attribs["duration"]
                # print (f"current task is: {data[0]} for {duration} minutes")
                # textID = "len tasks is 1" + data[0]
                textID = data[0]
                # say = f"your current task is {data[0]}"
                # self.client.publish ("python", say)

            if (len(tasks) > 1):
                # (ID, task_hour, task_minute)

                # print("len tasks > 1")
                # maybe not using itemgetter?
                # tasks.sort(key=itemgetter(2)) 

                tasks = sorted(tasks, key=lambda hour: hour[1])
                # print (tasks[-1])
                            
                ID = tasks[-1][0]
                # print (f"id is {tasks[0][0]}")
                attribs = self.dayPlan[ID]
                data = attribs["data"]
                duration = attribs["duration"]
                # print (f"current task is: {data[0]} for {duration} minutes")
                # textID = "len tasks is more than 1" + data[0]
                textID = data[0]
                # say = f"your current task is {data[0]}"
                # self.client.publish ("python", say)


            if (len(tasks) == 0):
                # pick the task that has highest hours and minutes
                # print("tasks == 0")
                # print(tasks_previous_hours)
                tasks_previous_hours = sorted(tasks_previous_hours, key=lambda hour: hour[1])

                hour_to_match = tasks_previous_hours[-1][1]
                tasks = []
                for task in tasks_previous_hours:
                    if(task[1] == hour_to_match):
                        tasks.append(task)
                
                tasks_single_hour_sort_by_minute = sorted(tasks, key=lambda minute: minute[2])

                ID = tasks_single_hour_sort_by_minute[-1][0]
                # print (f"id is {tasks[0][0]}")
                attribs = self.dayPlan[ID]
                data = attribs["data"]
                duration = attribs["duration"]
                # print (f"current task is: {data[0]} for {duration} minutes")
                # textID = "len tasks is 0" + data[0]
                textID = data[0]
                # say = f"your current task is {data[0]}"
                # self.client.publish ("python", say)
                    
        else:
            # print("day plan is empty")
            # self.client.publish ("python", "day plan is empty")
            textID = "day plan is empty"
        # current task is 7 15
        # time is 8 05
        # task in list is at 8 40
        # task in list is at 8 50
        return textID

    def getNextTask(self):
        say = f"your next task is {self.getNextTaskInternal()}"
        self.client.publish ("python", say)

    def getNextTaskInternal(self):
         # TODO on the minute of starting, current task reports the previous task
        # this happens in if (len(tasks) == 1):

        now = datetime.now()
        hour = now.hour
        minute = now.minute

        tasks = []
        tasks_this_hour = []
        tasks_previous_hours = []

        

        textID = ""

        if self.dayPlan:

            for ID, attribs in self.dayPlan.items():
                # taskattribs = {"action": _action, "data": _data, "hour": self.task_start[0], "minute": self.task_start[1], "duration": duration, "phase": _dayPhase}
                task_hour = attribs["hour"]
                task_minute = attribs["minute"]
                if(task_hour == hour):
                    tasks_this_hour.append((ID, task_hour, task_minute))
                if(task_hour > hour):
                    tasks_previous_hours.append((ID, task_hour, task_minute))

            # print("tasks to check, this hour:")
            # print(tasks_this_hour)
            # print("tasks previous hours:")
            # print(tasks_previous_hours)

            for attribs in tasks_this_hour:
                if(attribs[2] >= minute):
                    tasks.append(attribs)
            
            if (len(tasks) == 1):
                # print("len tasks == 1")

                ID = tasks[0][0]
                # print (f"id is {tasks[0][0]}")
                attribs = self.dayPlan[ID]
                data = attribs["data"]
                duration = attribs["duration"]
                # print (f"current task is: {data[0]} for {duration} minutes")
                # textID = "len tasks is 1" + data[0]
                textID = data[0]
                # say = f"your current task is {data[0]}"
                # self.client.publish ("python", say)

            if (len(tasks) > 1):
                # (ID, task_hour, task_minute)

                # print("len tasks > 1")
                # maybe not using itemgetter?
                # tasks.sort(key=itemgetter(2)) 

                tasks = sorted(tasks, key=lambda hour: hour[1], reverse=True)
                # print (tasks[-1])
                            
                ID = tasks[-1][0]
                # print (f"id is {tasks[0][0]}")
                attribs = self.dayPlan[ID]
                data = attribs["data"]
                duration = attribs["duration"]
                # print (f"current task is: {data[0]} for {duration} minutes")
                # textID = "len tasks is more than 1" + data[0]
                textID = data[0]

                # say = f"your current task is {data[0]}"
                # self.client.publish ("python", say)


            if (len(tasks) == 0):
                # pick the task that has highest hours and minutes
                # print("tasks == 0")
                # print(tasks_previous_hours)
                tasks_previous_hours = sorted(tasks_previous_hours, key=lambda hour: hour[1], reverse=True)

                hour_to_match = tasks_previous_hours[-1][1]
                tasks = []
                for task in tasks_previous_hours:
                    if(task[1] == hour_to_match):
                        tasks.append(task)
                
                tasks_single_hour_sort_by_minute = sorted(tasks, key=lambda minute: minute[2], reverse=True)

                ID = tasks_single_hour_sort_by_minute[-1][0]
                # print (f"id is {tasks[0][0]}")
                attribs = self.dayPlan[ID]
                data = attribs["data"]
                duration = attribs["duration"]
                # print (f"current task is: {data[0]} for {duration} minutes")
                # textID = "len tasks is 0" + data[0]
                textID = data[0]

                # say = f"your current task is {data[0]}"
                # self.client.publish ("python", say)
                    
        else:
            # print("day plan is empty")
            # self.client.publish ("python", "day plan is empty")
            textID = "day plan is empty"
        # current task is 7 15
        # time is 8 05
        # task in list is at 8 40
        # task in list is at 8 50
        if textID == "":
            textID = "task is empty"
        return textID

    def delete_daily(self):
        print(f"jobs in {self.dailycategoryname}")
        for ID, attribs in self.dayPlan.items():
            print("task: ", ID)
        del_task = prompt('task to delete: ')
        del self.dayPlan[del_task]

    def delete_extra(self):
        print(f"jobs in {self.extracategoryname}")
        for ID, attribs in self.extralist.items():
            print("task: ", ID)
        del_task = prompt('task to delete: ')
        del self.dayPlan[del_task]

    def save(self):
        self.all_tasks.clear()
        self.all_tasks.update({self.extracategoryname: self.extraqueue})
        self.all_tasks.update({self.dailycategoryname: self.dayPlan})
        self.all_tasks.update({self.timecategoryname: self.dayPhases_TOD})
        name = self.path + self.filename
        with open(name, 'w') as f:
            json.dump(self.all_tasks, f, indent = 3)
        # print(self.all_tasks)
        # self.client.publish ("python", "saved")
        f.close()

    def log(self, _text):
        with open("/home/st/Projects/Planner/log", 'a') as f:
            f.write(_text)
            f.write("\r\n")
            
        # print(self.all_tasks)
        # self.client.publish ("python", "saved")
        f.close()

    def load(self):
        # self.client.publish ("python", "loading")
        # time.sleep(3)
        try:
            name = self.path + self.filename
            f = open(name)
            tasks_from_file = json.load(f)
            f.close()
        except Exception as e:
            err = "had error " + str(e)
            print (err)
            self.client.publish ("python", "couldn't load the file")
            # time.sleep(3)

        # # time.sleep(3)
        # if tasks_from_file:
        #     # self.client.publish ("python", "opened")
        #     # time.sleep(2)
        # else:
        #     self.client.publish ("python", "heres the problem you fuck")
        #     time.sleep(2)

        self.all_tasks.update(tasks_from_file)
        
        dailycheck = self.all_tasks.get(self.dailycategoryname)
        extracheck = self.all_tasks.get(self.extracategoryname)
        timecheck = self.all_tasks.get(self.timecategoryname)

        if dailycheck:
            self.dayPlan.update(self.all_tasks[self.dailycategoryname])
            # self.client.publish ("python", "day plan is planned")
            # time.sleep(2)
        # else:
            # self.client.publish ("python", "can't find daily")
            # time.sleep(2)
        if extracheck:
            self.extraqueue.update(self.all_tasks[self.extracategoryname])

        if timecheck:
            self.lights_on_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.lights_on.value] 
            self.wake_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.wake.value]
            self.mid_morning_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.mid_morning.value]
            self.midday_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.midday.value]
            self.afternoon_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.afternoon.value]
            self.dinner_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.dinner.value]
            self.evening_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.evening.value]
            self.lights_off_TOD = self.all_tasks[self.timecategoryname][self.dayPhase.lights_off.value]

        # self.list_jobs()
        
        # self.client.publish ("python", "loaded")

    def clear(self):
        self.all_tasks.clear()
        self.dayPlan.clear()
        self.extralist.clear()

    def clear_cron(self):
        self.cron.remove_all()
        self.cron.write()

    def reset(self):   
        self.clear()
        now = datetime.now()
        dt_string = now.strftime("%Y%m%d%H%M")
        os.rename(self.filename, dt_string + self.filename + ".bak")
        
        
        self.client.publish ("python", "reset")

    def testAnnounce(self):
        # client.publish ("python", "scheduling test")
        # text = "yay yay"

        # cmd = (f' mplayer /home/st/Videos/morning.mp4')
        # cmd = ('python /home/st/pythonProjects/alexaVolume/venv/lightControllerMain.py 2')
        # task = cron.new(command=cmd)
        # task.minute.every(1)
        # cron.write()

        # task = cron.new(command='python /home/st/pythonProjects/alexaVolume/venv/lightControllerMain.py 4')
        # task.hour.on(19)
        # task.minute.on(44)
        # cron.write() 
        # task.run()
        # source /home/st/Projects/Planner/.venv/bin/activate

        # self.task_start = [7,42]
        # play_video("morning", 16)

        # task = self.cron.new(command='bash /home/st/scripts/play.sh /home/st/Videos/morning.mp4')
        # task.hour.on(8)
        # task.minute.on(25)
        # self.cron.write() 
        # task.run()
        return

    def stoicQuotes(self):
        
        quotes = [
            "Every day is a dying day. Get back to basics. You're here.",
            "You don't own anything. Appreciate what is around you. It's only there by good fortune.",
            "Stop overindulging. Be ascetic today. Make sacrifices today for indulgences tomorrow.",
            "Stay present. Now is all that exists.",
            "Be disciplined. For one day, stick to the schedule completely. Be militant.",
            "You are the only one you can count on. Today, make tomorrow better.",
            "Remember how good it feels to be working out. Make the time today.",
            "Guide your actions with your emotions. Emote yourself rather than using logic or willpower.",
            "Find a new way to look at your daily tasks. Make it novel. What character are you playing today?",
            "It's hard to play a beautiful melody. It's hard to play a beautiful life.",
            "Why are you excited to do this task? Look for motivation first before taking any actions.",
            "Take the time to appreciate the progress you have made. Each time you do something, compare yourself with your past self. You are doing great.",
            "You have nothing to apologise for. You are in control. Your word is law. Trust yourself. Act for yourself.",
            "What is this days meaning and purpose? What is the lesson you learn today?",
            "If it is endurable, then endure it. Stop complaining.",
            "every day, every action, you are building up credit. What kind of return will you receive? health or ruin?",
            "every time you make a good choice, praise yourself for it. Feel good when you do good."
        ]
        
        daily_quote = quotes[(random.randint(0, len(quotes) - 1))]
        
        return daily_quote

# ----------------------------------------

Planner = planner()

try:
    sys.argv[1]
except IndexError:
    Planner.main()
else:
    
    if(sys.argv[1] == "normal"):
        # client.publish ("python", "started daily planner.")
        Planner.clear_cron()
        Planner.set_initial_conditions("normal")
        Planner.default_daily_tasks()
        Planner.save()
    elif(sys.argv[1] == "stop"):
        Planner.clear_cron()
        Planner.client.publish ("python", "cleared cron tasks.")
    elif(sys.argv[1] == "startlate"):
        Planner.clear_cron()
        Planner.set_initial_conditions("startlate")
        Planner.default_daily_tasks()
        Planner.save()
    elif(sys.argv[1] == "startnow"):
        Planner.clear_cron()
        Planner.set_initial_conditions("startnow")
        Planner.default_daily_tasks()
        Planner.save()
    elif(sys.argv[1] == "yoga"):
        Planner.log("yoga")
        Planner.play_youtube("https://www.youtube.com/watch?v=aLfY0cH9oW4")
    elif(sys.argv[1] == "endNow"):
        x = True
    elif(sys.argv[1] == "nextTask"):
        Planner.load()
        Planner.getNextTask()
    elif(sys.argv[1] == "skipToNextTask"):
        x = True
    elif(sys.argv[1] == "currentTask"):
        
        # Planner.set_initial_conditions("normal")
        # Planner.default_daily_tasks()
        Planner.load()
        Planner.getCurrentTask()
    elif(sys.argv[1] == "markDone"):
        # Planner.set_initial_conditions("normal")
        # Planner.default_daily_tasks()
        Planner.load()
        Planner.markTaskDone()
        Planner.save()

        #add this in
