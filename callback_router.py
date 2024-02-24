import calendar
import datetime

import aiogram
import pytz
from aiogram import Router, F, types
from aiogram.enums import ContentType
from aiogram.filters.callback_data import CallbackData

import config
import keyboards
import routers
from config import months
import sqlite3
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pytz import utc
from aiogram.types import InlineKeyboardMarkup

from factories import *
from methods import galochka_date_change, send_testing_message

router = Router()
con = sqlite3.connect("database.db")
cursor = con.cursor()
test_status = 1

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
    return_keyboard = galochka_date_change(callback=callback, callback_data=callback_data,
                                           return_keyboard=return_keyboard)
    try:
        await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        await callback.message.edit_text(text=f"Вы выбрали дату: {callback_data.year}-{callback_data.month}"
                                              f"-{callback_data.day}")
    except Exception:
        print("Keyboard not modified")
    await callback.message.answer(f"Выберите удобное время", reply_markup=keyboards.get_times(callback))
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
    print("Тут я работаю")
    return_keyboard = keyboards.get_times(callback)
    for row in range(len(callback.message.reply_markup.inline_keyboard)):
        for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
            # if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
            #     return_keyboard.inline_keyboard[row][data].text = str(caldr[row-1][data])

            if callback.message.reply_markup.inline_keyboard[row] \
                    [data].text == f"{callback_data.hour}:{callback_data.minute}0":
                print("Edited", callback.message.reply_markup.inline_keyboard[row][data].text, callback_data.hour,
                      callback_data.minute)
                cursor.execute("UPDATE users_data SET time=? WHERE user_id=?",
                               (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id))
                con.commit()
                cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {callback.from_user.id}")
                row_db = cursor.fetchall()
                print(row_db)
                if row_db != [] and row_db[0][0] is not None and row_db[0][1] is not None:
                    date_to = datetime.datetime.strptime(row_db[0][0].split(" ")[0] + " " + row_db[0][1] +
                                                         ":00", '%Y-%m-%d %H:%M:%S')
                else:
                    print("No datetime in database")
                    return callback.message.answer(text="Произошла ошибка")
                if config.DEV_MODE:
                    date_to = datetime.datetime.now() + datetime.timedelta(seconds=3)
                scheduler = AsyncIOScheduler(timezone="Asia/Almaty")
                try:
                    scheduler.remove_all_jobs()
                    scheduler.shutdown()
                except:
                    print("schedulers shutdown error")
                    scheduler.add_job(schedule_start_from_db, trigger='date', run_date=date_to,
                                      kwargs={"callback": callback, "date": date_to})
                    scheduler.add_job(schedule_not_end_but_end_from_db, trigger='date',
                                      run_date=str(date_to + config.exam_times["send_notification"]),
                                      kwargs={"callback": callback})
                    scheduler.add_job(schedule_end_from_db, trigger='date', run_date=str(date_to +
                                                                                         config.exam_times["duration"]),
                                      kwargs={"callback": callback})
                    correct_time = f"{callback_data.hour}:{callback_data.minute}0"
                    # correct_time = f"20:24"
                    user_config = (correct_time, callback.from_user.id)
                    cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", user_config)
                    con.commit()
                    scheduler.start()

                return_keyboard.inline_keyboard[row][data].text = "✅"
    try:
        await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        await callback.message.edit_text(text=f"Вы выбрали время: {callback_data.hour}:{callback_data.minute}0")
    except Exception:
        print("keyboard not modified")
    cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {callback.from_user.id}")
    row_db = cursor.fetchall()
    await callback.answer()
    await callback.message.answer(text=f"Ваше тестирование запланировано на: {row_db[0][0].split(' ')[0]}"
                                       f" {row_db[0][1]}. В указанное время я отправлю вам задание. На его выполнение "
                                       f"у вас будет 4 часа. Результаты тестирования можно отправить в виде "
                                       f"видео до 30 секунд",
                                  reply_markup=keyboards.main_actions(remove_exam=
                                                                      routers.exist_datetime(callback.from_user.id)))


@router.callback_query(IsCompleteCallbackFactory.filter(F.action == "isComplete"))
async def times(callback: types.CallbackQuery, callback_data: TimeCallbackFactory):
    if callback_data.from_who == 0:
        if callback_data.is_complete == 0:
            await callback.message.edit_text(text=f"Тестирование продолжается")
        elif callback_data.is_complete == 1:
            await callback.message.edit_text(text=f"Вы досрочно закончили тестирование")
            await send_testing_message(callback, go_to=3)
        await callback.send_copy(config.checker_id, reply_keyboard=keyboards.keyboard_is_exam_complete(from_who=1))
        await callback.(config.checker_id, reply_keyboard=keyboards.keyboard_is_exam_complete(from_who=1))
    elif callback_data.from_who == 1:
        if callback_data.is_complete == 0:
            await callback.message.edit_text(text=f"Тестирование продолжается")
        elif callback_data.is_complete == 1:
            await callback.message.edit_text(text=f"Вы досрочно закончили тестирование")
            await send_testing_message(callback, go_to=3)
    await callback.answer()