
from datetime import date
from datetime import datetime

# print(str(datetime.today()))


d0 = date.today()
d1 = date(2086, 7, 24)
delta = d1 - d0
print(delta.days)
