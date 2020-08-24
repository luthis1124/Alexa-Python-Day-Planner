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

import sys

# [AO OSS] audio_setup: Can't open audio device /dev/dsp: No such file or directory
# [AO_ALSA] alsa-lib: confmisc.c:1281:(snd_func_refer) Unable to find definition 'defaults.pcm.tstamp_type'
# [AO_ALSA] alsa-lib: conf.c:4743:(_snd_config_evaluate) function snd_func_refer returned error: No such file or directory
# [AO_ALSA] alsa-lib: conf.c:5231:(snd_config_expand) Evaluate error: No such file or directory
# [AO_ALSA] alsa-lib: pcm.c:2660:(snd_pcm_open_noupdate) Unknown PCM dmix:MID
# [AO_ALSA] Playback open error: No such file or directory

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
attempedExtraTasks = {}

dailylistname = "dailylist"
extralistname = "extralist"
dailycategoryname = "daily"
extracategoryname = "extra"

hour_name = "hour"
minute_name = "minutes"
duration_name = "duration"
estimate_name = "estimate"

# this section should be moved to an init to set day type
early_daystart = [6,1]
late_daystart = [7,1]

# set early or late times
daystart = early_daystart

# increment day parts based time since last section
lights_on = [daystart[0] - 1, 40]
wake = daystart
mid_morning = [wake[0] + 3, 30]
midday = [mid_morning[0] + 3, 0]
afternoon = [midday[0] + 3, 0]
dinner = [afternoon[0] + 2, 0]
evening = [dinner[0] + 4, 0]
lights_off = [evening[0], 20]

#default 
# lights_on = [5,40]
# wake = [6,1]
# mid_morning = [10,0]
# midday = [12,0]
# afternoon = [15,0]
# dinner = [17,0]
# evening = [21,0]
# lights_off = [21,20]


client = mqtt.Client()
client.connect("localhost", 1883, 60)
cron = CronTab(user='st')

menu_items = ['add daily', 'add extra', 'del d', 'del e', 'publish', 'save', 'load', 'populate', 'list', 'cron', 'x', 'clear', 'default', 'clear cron']

class menuCompleter(Completer):
    def get_completions(self, document, complete_event):
        word_before_cursor = document.get_word_before_cursor(WORD=True)
        matches = fuzzyfinder(word_before_cursor, menu_items)
        for m in matches:
            yield Completion(m, start_position=-len(word_before_cursor))


def sample_populate():

    dailytask1name = "dailytask1"
    dailytask2name = "dailytask2"
    
    dailytask1attribs = {"time": "x", "date": "y", "lol": "z"}
    dailytask2attribs = {"time": "x2", "date": "y2", "lol": "z2"}

    dailylist[dailytask1name] = dailytask1attribs
    dailylist[dailytask2name] = dailytask2attribs

    all_tasks.update({dailycategoryname: dailylist})

    return    

def main():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    print("Today's date:", dt_string)
    while True:
        try:
            user_input = prompt(u'>', history=FileHistory('history.txt'),completer=menuCompleter())
            # click.echo_via_pager(user_input)
            if 'del d' == user_input:
                delete_daily()
            elif 'del e' == user_input:
                delete_extra()
            elif 'add daily' == user_input:
                add_daily()
            elif 'add extra' == user_input:
                add_extra()
            elif 'default' == user_input:
                default_daily_tasks()
            elif 'publish' == user_input:
                publish()
            elif 'days' == user_input:
                days_left()
            elif 'cron' == user_input:
                list_cron()
            elif 'list' == user_input:
                list_jobs()
            elif 'populate' == user_input:
                sample_populate()
            elif 'save' == user_input:
                save()
            elif 'load' == user_input:
                load()
            elif 'reset' == user_input:
                reset()
            elif 'test' == user_input:
                testAnnounce()
            elif 'say' == user_input:
                say(user_input)
            elif 'clear' == user_input:
                say(user_input)
            elif 'clear cron' == user_input:
                clear_cron()
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

def say(text):
    # not done yet
    client.publish ("python", text)

def add_extra():
    add_name = prompt('name: ')
    add_hours = prompt('at hour: ')
    add_minutes = prompt('at minute: ')
    add_estimate = prompt('half hour blocks estimated: ')

    taskattribs = {hour_name: add_hours, minute_name: add_minutes, estimate_name: add_estimate}
    
    extralist[add_name] = taskattribs

    all_tasks.update({extracategoryname: extralist})

    client.publish ("python", "added extra task")

def play_video(add_name, duration, task_start):
    cmd = (f'bash /home/st/scripts/play.sh /home/st/Videos/{add_name}.mp4')
    task = cron.new(command=cmd)
    task.hour.on(task_start[0])
    task.minute.on(task_start[1])
    cron.write()

    task_start[1] += duration
    while (task_start[1] > 59):
        task_start[1] -= 60
        task_start[0] += 1

def declare_extra_tasks():
    #some tasks to publish
    add_extra_internal("compile some stoic quotes.", 15)
    # add_extra_internal("clean and then vacuum your room", 20)
    
    add_extra_internal("remind rebecca to post package.", 1)
    add_extra_internal("do the ali express order.", 20)
    
    add_extra_internal("get through your emails.", 20)
    
    add_extra_internal("transcribe your notes on the green slips.", 20)
    add_extra_internal("upload your code to github.", 20)
    
    add_extra_internal("fix the green drill under the bed.", 60)
    add_extra_internal("fix the pyrography pen under the bed.", 60)
    add_extra_internal("try to fix rebeccas blue nokia with the replacement screen.", 20)
    

def add_extra_internal(add_name, duration):
   
    extralist[add_name] = duration

def sanity_check(task_start, next_section_start, name_of_current_section):
    free_hours = next_section_start[0] - task_start[0] # hours difference
    free_minutes = (free_hours * 60) + (next_section_start[1] - task_start[1]) # total minutes difference
    if (free_minutes < 0):
        error_msg = f"error. the {name_of_current_section} section extends into the next section."
        client.publish ("python", error_msg)
        print(error_msg)
        quit()
    
def default_daily_tasks():

    # for ease of use, just run default
    clear_cron()

    declare_extra_tasks()
    
    task_start = [0,0]

    # pre morning -----------------------------------------------------------------------------
    task_start[0] = lights_on[0]
    task_start[1] = lights_on[1]

    # lights don't need the sanity check

    light(1, 5, task_start)
    light(2, 4, task_start)
    light(3, 4, task_start)
    light(4, 4, task_start)
    light(5, 3, task_start)
    light(10, 4, task_start) #6am
    light(15, 4, task_start)
    light(20, 3, task_start)
    light(40, 3, task_start)
    light(60, 3, task_start)
    light(80, 3, task_start)
    light(100, 0, task_start) #620am
    
    # morning -----------------------------------------------------------------------------
    task_start[0] = wake[0]
    task_start[1] = wake[1]

    d0 = date.today()
    d1 = date(2076, 7, 23)
    delta = d1 - d0
    add_daily_internal("Welcome to today. You have " + str(delta.days) + " days left to live.", 1, task_start)
    add_daily_internal("you are insignificant. but your actions mean everything.", 1, task_start)
    add_daily_internal("now is the most important part of the day. Win the morning and you win the day.", 1, task_start)
    add_daily_internal("its time to get up. Yoga will start soon. lay out the mat and entire childs pose.", 1, task_start)  
    play_video("morning", 16, task_start)
    
    # frequent reminders, such as vape and sit up straight
    # washing should be an extra task
    # loop tasks, ie start thing, end thing, ie washing, baking
    # recurring tasks on longer frequency ie vacuum room, shave, washing
    # add task for reading journal
    # check if tasks get completed
    # congratulations message for each task
    # enable better easier flexibility for changing day start times etc
    # late night option

    add_daily_internal("go boil the jug and prepare your breakfast.", 4, task_start)
    add_daily_internal("its time for your cold shower. dont be a wimp.", 20, task_start)
    add_daily_internal("you should be getting dressed and making your bed by now.", 5, task_start)
    add_daily_internal("its breakfasttime.", 25, task_start)
    add_daily_internal("clean your teeth and then the kitchen", 20, task_start)
    add_daily_internal("now clean your room.", 10, task_start)

    add_daily_internal("message your grandfather and your parents.", 40, task_start)
    
    

    # -----------------------------------------------------------------------------

    # sanity check
    sanity_check(task_start, mid_morning, "morning")
    # extra tasks section
    publish_extra(task_start, mid_morning)
    
    # ------------------------------------ mid morning -----------------------------------------
    task_start[0] = mid_morning[0]
    task_start[1] = mid_morning[1]

    add_daily_internal("it's time for a break. Todays snack is eggs on toast.", 20, task_start)
    add_daily_internal("plan for dinner.", 20, task_start)
    add_daily_internal("reading time.", 20, task_start)

    # -----------------------------------------------------------------------------

    # sanity check
    sanity_check(task_start, midday, "mid morning")
    # extra tasks section
    publish_extra(task_start, midday)

    # ------------------------------------- midday ----------------------------------------
    task_start[0] = midday[0]
    task_start[1] = midday[1]
    add_daily_internal("its lunch time. lunch will be a tuna sandwich.", 20, task_start)
    

    # -----------------------------------------------------------------------------

    # sanity check
    sanity_check(task_start, afternoon, "midday")
    # extra tasks section
    publish_extra(task_start, afternoon)

    # ------------------------------------- afternoon ----------------------------------------
    task_start[0] = afternoon[0]
    task_start[1] = afternoon[1]
    add_daily_internal("now it's time to work on the planner. you need to change the tasks as required for tomorrow.", 1, task_start)

    # -----------------------------------------------------------------------------

    # sanity check
    sanity_check(task_start, dinner, "afternoon")
    # extra tasks section
    publish_extra(task_start, dinner)

    # ------------------------------------- dinner ----------------------------------------
    task_start[0] = dinner[0]
    task_start[1] = dinner[1]
    add_daily_internal("it's time to prepare and eat dinner.", 90, task_start)
    add_daily_internal("with dinner done, check your plans for tomorrow. its saturday.", 120, task_start)
    

    # -----------------------------------------------------------------------------

    # ------------------------------------ evening -----------------------------------------
    task_start[0] = evening[0]
    task_start[1] = evening[1]
    add_daily_internal("well done, clean your teeth and you may read.", 30, task_start)
    add_daily_internal("its time to wrap up for the day.", 2, task_start)
    add_daily_internal("its time to reflect on your day.", 5, task_start)
    add_daily_internal("now consider how insignificant you are.", 5, task_start)
    add_daily_internal("Write in the journal.", 10, task_start)
    add_daily_internal("prepare space for yoga. make sure volume is appropriate for your morning routine.", 15, task_start)

    play_video("evening", 15, task_start)

    add_daily_internal("you are done now. pack up and clean your room. Make sure you have space for yoga tomorrow morning.", 5, task_start)
    add_daily_internal("fill your drink bottle.", 3, task_start)
    add_daily_internal("now get into bed you little shit.", 4, task_start)
    add_daily_internal("well done today. You had a cold shower, were on time for each task, cleaned the kitchen, worked on the planner, kept in contact with your friends and family, did the washing, cleaned your room, planned for dinner, prepared for and had a good interview, ate well, exercised, and took control of your life.", 3, task_start)
    add_daily_internal("goodnight, look forward to tomorrow.", 1, task_start)

    # -----------------------------------------------------------------------------

    #evening lights start at 9pm
    task_start[0] = lights_off[0]
    task_start[1] = lights_off[1]
    light(95, 5, task_start)
    light(80, 5, task_start)
    light(75, 5, task_start)
    
    light(60, 5, task_start)
    light(40, 5, task_start)
    light(20, 5, task_start) 
    
    light(5, 1, task_start)
    light(4, 1, task_start)
    light(3, 1, task_start)
    light(2, 1, task_start)
    light(1, 1, task_start)
    light(0, 1, task_start)

    publish()

    all_tasks.clear()
    
    all_tasks.update({extracategoryname: extralist})
    all_tasks.update({dailycategoryname: dailylist})
    
def add_daily():
    add_name = prompt('reminder text: ')
    add_hours = prompt('at hour: ')
    add_minutes = prompt('at minute: ')
    taskattribs = {hour_name: add_hours, minute_name: add_minutes}
    
    dailylist[add_name] = taskattribs

    all_tasks.update({dailycategoryname: dailylist})

    print("Don't forget to SAVE!! ..and publish when ready")
    client.publish ("python", "task created and ready to publish")

def light(level, duration, task_start):

    cmd = f'python /home/st/pythonProjects/alexaVolume/venv/lightControllerMain.py {level}'
    task = cron.new(command=cmd)
    task.hour.on(task_start[0])
    task.minute.on(task_start[1])
    cron.write() 

    task_start[1] += duration
    while (task_start[1] > 59):
        task_start[1] -= 60
        task_start[0] += 1

    return

def publish_extra(start_of_extra_time, end_of_extra_time):

    total_hours = end_of_extra_time[0] - start_of_extra_time[0]
    total_minutes = end_of_extra_time[1] - start_of_extra_time[1] + (total_hours * 60)
    #total minutes is what we have to fit extra tasks into
    
    #we should add tasks in, until we can't add any more, and then add reading time
    #but then for the next extra task time block, how do we know which tasks have been added?
    #It must be a queue system, so tasks get chucked out of extralist[] and into attempted[]?
    #fuck it, that will work for now. 

    for job, duration in extralist.items():

        #do we have time for the job?
        if total_minutes > duration:
            total_minutes -= duration

            cmd = f'source /home/st/Projects/Planner/.venv/bin/activate ; python /home/st/Projects/Planner/announcements.py "{job} you have {duration} minutes"'
            task = cron.new(command=cmd)
            task.hour.on(start_of_extra_time[0])
            task.minute.on(start_of_extra_time[1])
            cron.write()

            # increase start time to account for job duration
            start_of_extra_time[1] += duration
            while (start_of_extra_time[1] > 59):
                start_of_extra_time[0] += 1
                start_of_extra_time[1] -= 60

            # add job to tracker
            attempedExtraTasks[job] = duration
        else:
            cmd = f'source /home/st/Projects/Planner/.venv/bin/activate ; python /home/st/Projects/Planner/announcements.py "you get to read until the next task"'
            task = cron.new(command=cmd)
            task.hour.on(start_of_extra_time[0])
            task.minute.on(start_of_extra_time[1])
            cron.write()

    # this to make sure we remove jobs from possibly being schedueled (make this better, duplicate the list or something before starting)
    for job, duration in attempedExtraTasks.items():
        #at the end, we want to remove the job from the list
        print(f"removing {job}")
        extralist.pop(job, None)

def add_daily_internal(add_name, duration, task_start):

    taskattribs = {hour_name: task_start[0], minute_name: task_start[1], duration_name: duration}
    dailylist[add_name] = taskattribs

    task_start[1] += duration
    while (task_start[1] > 59):
        task_start[1] -= 60
        task_start[0] += 1

def add_weekend_task():
    return

def days_left():
    d0 = date.today()
    d1 = date(2076, 7, 24)
    delta = d1 - d0
    print(delta.days)
    client.publish ("python", "Welcome to today. You have " + str(delta.days) + " days left to live.")

def publish():
    # CLEARS ALL TASKS, NEEDS TO BE RUN AFTER EACH SEGMENT
    # SHOULD BE FINE
    # IT'S NOT FINE, COMMENTED OUT THE REMOVE ALL
    client.publish ("python", "publishing tasks")
    # cron.remove_all()
    # cron.write()
        
    #daily tasks
    for job, attribs in dailylist.items():
        add_name = job
        add_hours = attribs[hour_name]
        add_minutes = attribs[minute_name]
        _duration = attribs[duration_name]
        
        cmd = f'source /home/st/Projects/Planner/.venv/bin/activate ; python /home/st/Projects/Planner/announcements.py "{add_name} you have {_duration} minutes"'
        task = cron.new(command=cmd)
        task.hour.on(add_hours)
        task.minute.on(add_minutes)
        cron.write()

    # dailylist.clear()

def list_cron():
    for job in cron:
        print(job)

def list_jobs():
    print(f"jobs in {dailycategoryname}")
    for job, attribs in dailylist.items():
        print("task: ", job)
        for key in attribs:
            print(key + ":", attribs[key])
    print(f"jobs in {extracategoryname}")
    for job, attribs in extralist.items():
        print("task: ", job)
        for key in attribs:
            print(key + ":", attribs[key])

def delete_daily():
    print(f"jobs in {dailycategoryname}")
    for job, attribs in dailylist.items():
        print("task: ", job)
    del_task = prompt('task to delete: ')
    del dailylist[del_task]

def delete_extra():
    print(f"jobs in {extracategoryname}")
    for job, attribs in extralist.items():
        print("task: ", job)
    del_task = prompt('task to delete: ')
    del dailylist[del_task]

def save():
    with open(filename, 'w') as f:
        json.dump(all_tasks, f)
    print(all_tasks)
    client.publish ("python", "saved")
    f.close()

def load():
    f = open(filename)
    tasks_from_file = json.load(f)
    f.close()

    all_tasks.update(tasks_from_file)
    
    dailycheck = all_tasks.get(dailycategoryname)
    extracheck = all_tasks.get(extracategoryname)
    if dailycheck:
        dailylist.update(all_tasks[dailycategoryname])
    if extracheck:
        extralist.update(all_tasks[extracategoryname])

    list_jobs()
    
    client.publish ("python", "loaded")

def clear():
    all_tasks.clear()
    dailylist.clear()
    extralist.clear()

def clear_cron():
    cron.remove_all()
    cron.write()
    

def reset():   
    clear()
    now = datetime.now()
    dt_string = now.strftime("%Y%m%d%H%M")
    os.rename(filename, dt_string + filename + ".bak")
    
    
    client.publish ("python", "reset")

def testAnnounce():
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

    # task_start = [7,42]
    # play_video("morning", 16, task_start)

    task = cron.new(command='bash /home/st/scripts/play.sh /home/st/Videos/morning.mp4')
    task.hour.on(8)
    task.minute.on(25)
    cron.write() 
    # task.run()
    return

# ----------------------------------------

try:
    sys.argv[1]
except IndexError:
    main()
else:
    if(sys.argv[1] == "start"):
        # client.publish ("python", "started daily planner.")
        clear_cron()
        default_daily_tasks()
    elif(sys.argv[1] == "stop"):
        clear_cron()
        client.publish ("python", "cleared cron tasks.")
