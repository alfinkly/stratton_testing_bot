import datetime

TOKEN = "6996615436:AAGTIPQZk-ASHPX6K7ocN8La2vHq3E7EUA8"

months = {1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь", 7: "Июль",
          8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}

checker_id = 992654384

exam_times = {"duration": datetime.timedelta(hours=4), "send_notification": datetime.timedelta(hours=3, minutes=50)}

DEV_MODE = True

if DEV_MODE:
    exam_times = {"duration": datetime.timedelta(minutes=1), "send_notification": datetime.timedelta(seconds=15)}
    checker_id = 992654384