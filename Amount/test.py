import datetime

start_date = datetime.date.today()
seven_day_dates = [start_date + datetime.timedelta(days=i) for i in range(7)]
print(seven_day_dates)
