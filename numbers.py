from datetime import datetime

num = [10,20]
print (num[0])
print (num[1])


now = datetime.now()
print (now)
dt_string = now.strftime("%d/%m/%Y %H:%M")
print (dt_string)
print (datetime.hour)