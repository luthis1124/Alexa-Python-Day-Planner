
class wtf:

    def __init__(self):
        self.lights_on = [1, 40]

    def set_initial_conditions(self):
        wtf.lights_on = [1, 40]
        
    def default_daily_tasks(self):
        # self.set_initial_conditions()
        print (f"lights on: {self.lights_on}")

x = wtf()
x.default_daily_tasks()