import calendar
import datetime

import pytz
from aiogram import Router, F, types
from aiogram.enums import ContentType
from aiogram.filters.callback_data import CallbackData
import keyboards
from config import months
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc

router = Router()
con = sqlite3.connect("database.db")
cursor = con.cursor()
sheduler = AsyncIOScheduler(timezone="Asia/Almaty")

class DateCallbackFactory(CallbackData, prefix='fabnum'):
    action: str
    day: int = None
    month: int = None
    year: int = None


class TimeCallbackFactory(CallbackData, prefix='nago'):
    action: str
    hour: int = None
    minute: int = None


def galochka_date_change(callback, callback_data, return_keyboard):
    print("galochka_date_change")
    return_keyboard = return_keyboard
    caldr = calendar.monthcalendar(callback_data.year, callback_data.month)
    for row in range(len(callback.message.reply_markup.inline_keyboard)):
        for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
            if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
                return_keyboard.inline_keyboard[row][data].text = str(caldr[row - 1][data])
            if callback.message.reply_markup.inline_keyboard[row][data].text == str(callback_data.day):
                user_config = (datetime.datetime(year=callback_data.year,
                                                 month=callback_data.month,
                                                 day=callback_data.day),
                               callback.from_user.id)
                cursor.execute("UPDATE users_data SET date=? WHERE user_id=?", user_config)
                con.commit()
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


def galochka_date_db(return_keyboard, db_day, db_month, db_year):
    print("galochka_date_db")
    return_keyboard = return_keyboard
    # caldr = calendar.monthcalendar(db_year, db_month)
    for row in range(len(return_keyboard.inline_keyboard)):
        for data in range(len(return_keyboard.inline_keyboard[row])):
            if return_keyboard.inline_keyboard[row][data].text == str(db_day) and \
               return_keyboard.inline_keyboard[row][data].callback_data.split(":")[-1] == str(db_year) and \
               return_keyboard.inline_keyboard[row][data].callback_data.split(":")[-2] == str(db_month):
                print("<E>E>E>E>E>>E", return_keyboard.inline_keyboard[row][data].callback_data.split(":")[-1])
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


def galochka_time_change(callback, callback_data, return_keyboard, time):
    print("galochka_time_change")
    for row in range(len(callback.message.reply_markup.inline_keyboard)):
        for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
            if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
                time = f"{return_keyboard.inline_keyboard[row][data].callback_data.split(':')[-2]}:" \
                       f"{return_keyboard.inline_keyboard[row][data].callback_data.split(':')[-1]}0"
                return_keyboard.inline_keyboard[row][data].text = time

            if callback.message.reply_markup.inline_keyboard[row][data].text == time:
                # if callback.message.reply_markup.inline_keyboard[row][data].text ==\
                #     f"{callback_data.hour}:{callback_data.minute}0":
                print("Edited", callback.message.reply_markup.inline_keyboard[row][data].text, callback_data.hour,
                      callback_data.minute)
                user_config = (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id)
                cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", user_config)
                con.commit()
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


def galochka_time_db(return_keyboard, time):
    print("galochka_time_db")
    for row in range(len(return_keyboard.inline_keyboard)):
        for data in range(len(return_keyboard.inline_keyboard[row])):
            if return_keyboard.inline_keyboard[row][data].text == "✅":
                time = f"{return_keyboard.inline_keyboard[row][data].callback_data.split(':')[-2]}:" \
                       f"{return_keyboard.inline_keyboard[row][data].callback_data.split(':')[-1]}0"
                return_keyboard.inline_keyboard[row][data].text = time
            if return_keyboard.inline_keyboard[row][data].text == time:
                print("Edited", return_keyboard.inline_keyboard[row][data].text,
                      # callback_data.hour,
                      # callback_data.minute
                      )
                # user_config = (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id)
                # cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", user_config)
                # con.commit()
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


@router.callback_query(DateCallbackFactory.filter(F.action == "set_date"))
async def send_random_value(callback: types.CallbackQuery, callback_data: DateCallbackFactory):
    return_keyboard = callback.message.reply_markup
    # caldr = calendar.monthcalendar(callback_data.year, callback_data.month)
    # for row in range(len(callback.message.reply_markup.inline_keyboard)):
    #     for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
    #         if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
    #             return_keyboard.inline_keyboard[row][data].text = str(caldr[row-1][data])
    #         if callback.message.reply_markup.inline_keyboard[row][data].text == str(callback_data.day):
    #             user_config = (datetime.datetime(year=callback_data.year,
    #                                              month=callback_data.month,
    #                                              day=callback_data.day),
    #                            callback.from_user.id)
    #             cursor.execute("UPDATE users_data SET date=? WHERE user_id=?", user_config)
    #             con.commit()
    #             return_keyboard.inline_keyboard[row][data].text = "✅"
    return_keyboard = galochka_date_change(callback=callback, callback_data=callback_data, return_keyboard=return_keyboard)
    #
    # try:
    await callback.message.edit_reply_markup(reply_markup=return_keyboard)
    await callback.message.answer(f"Вы записаны на {months[callback_data.month]} {callback_data.day}",
                                  reply_markup=keyboards.get_times())
    # except Exception:
    #     print("Eroreeeeed 1")
    await callback.answer()


@router.callback_query(F.data == "nothing")
async def nothing(callback: types.CallbackQuery):
    await callback.answer()


@router.callback_query(DateCallbackFactory.filter(F.action == "month"))
async def month(callback: types.CallbackQuery, callback_data: DateCallbackFactory):
    try:
        await callback.message.edit_reply_markup(reply_markup=keyboards.get_calendar(year=callback_data.year,
                                                                                     month=callback_data.month,
                                                                                     message=callback))
    except Exception:
        print("erorr")
    await callback.answer()


# @router.callback_query(TimeCallbackFactory.filter(F.action == "times"))
# async def times(callback: types.CallbackQuery, callback_data: TimeCallbackFactory):
#     return_keyboard = callback.message.reply_markup
#     # for row in range(len(callback.message.reply_markup.inline_keyboard)):
#     #     for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
#     #         # if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
#     #         #     return_keyboard.inline_keyboard[row][data].text = str(caldr[row-1][data])
#     #
#     #         if callback.message.reply_markup.inline_keyboard[row][data].text == f"{callback_data.hour}:{callback_data.minute}0":
#     #             print("Edited", callback.message.reply_markup.inline_keyboard[row][data].text, callback_data.hour,
#     #                   callback_data.minute)
#     #             user_config = (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id)
#     #             cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", user_config)
#     #             con.commit()
#     #             return_keyboard.inline_keyboard[row][data].text = "✅"
#     cursor.execute(f"SELECT time FROM users_data WHERE user_id = {callback.from_user.id}")
#     row = cursor.fetchall()
#     return_keyboard = galochka_time_change(callback, callback_data, return_keyboard, row[0][0])
#     try:
#         await callback.message.edit_reply_markup(reply_markup=return_keyboard)
#         await callback.answer()
#     except Exception:
#         print("eroro")

@router.callback_query(TimeCallbackFactory.filter(F.action == "times"))
async def times(callback: types.CallbackQuery, callback_data: TimeCallbackFactory):
    print("CALLED 2")
    return_keyboard = keyboards.get_times()
    for row in range(len(callback.message.reply_markup.inline_keyboard)):
        for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
            # if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
            #     return_keyboard.inline_keyboard[row][data].text = str(caldr[row-1][data])

            if callback.message.reply_markup.inline_keyboard[row][data].text == f"{callback_data.hour}:{callback_data.minute}0":
                print("Edited", callback.message.reply_markup.inline_keyboard[row][data].text, callback_data.hour,
                      callback_data.minute)
                cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id))
                con.commit()
                cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {callback.from_user.id}")
                row_db = cursor.fetchall()
                if row_db != [] and row_db[0][0] != None and row_db[0][1] != None:
                    date_to = datetime.datetime.strptime(row_db[0][0].split(" ")[0] + " " + row_db[0][1] +
                                                                 ":00", '%Y-%m-%d %H:%M:%S')

                # date_to = datetime.datetime(year=2024, month=2, day=23, hour=20, minute=24)#todo ПОМЕНЯЙ
                sheduler.remove_all_jobs()
                sheduler.shutdown()
                sheduler.add_job(schedule_start_from_db, trigger='date', run_date=date_to,
                                 kwargs={"callback": callback, "date": date_to})
                sheduler.add_job(schedule_not_end_but_end_from_db, trigger='date',
                                 run_date=str(date_to + datetime.timedelta(minutes=1)), kwargs={"callback": callback})
                sheduler.add_job(schedule_end_from_db, trigger='date', run_date=str(date_to +
                                           datetime.timedelta(minutes=3)),
                                           kwargs={"callback": callback})
                correct_time = f"{callback_data.hour}:{callback_data.minute}0"
                # correct_time = f"20:24"
                user_config = (correct_time, callback.from_user.id)
                cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", user_config)
                con.commit()
                sheduler.start()
                return_keyboard.inline_keyboard[row][data].text = "✅"

    await callback.message.edit_reply_markup(reply_markup=return_keyboard)
    await callback.answer()


async def schedule_start_from_db(callback: types.CallbackQuery, date):
    await callback.message.answer(text="Ваш тест начался в " + str(date.hour) + ":" + str(date.minute))


async def schedule_not_end_but_end_from_db(callback: types.CallbackQuery):
    await callback.message.answer(text="Ваш тест закончится через 2 минуты, успейте отправить результаты в виде "
                                       "видео до 30 секунд ")


async def schedule_end_from_db(callback: types.CallbackQuery):
    await callback.message.answer(text="Ваш тест окончен")


@router.message(F.video)
async def anii(message: types.Message):
    cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {message.from_user.id}")
    row_db = cursor.fetchall()
    date_to = datetime.datetime.strptime(row_db[0][0].split(" ")[0] + " " + row_db[0][1] +
                                         ":00", '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    print(now < date_to)
    print(date_to)
    print(date_to + datetime.timedelta(minutes=3))
    if message.video.duration > 30:
        await message.reply("Извините, видео должно быть не более 30 секунд.")

    if date_to < now < date_to + datetime.timedelta(minutes=3):
        await message.answer("Отправляю проверяющему!")
        await message.send_copy(992654384)
    else:
        await message.answer("Вы отправили видео не в срок!")


async def rerun_shedulers():
