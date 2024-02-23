import sqlite3
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import calendar
import datetime
import callback_router
from config import months
from typing import Optional
from aiogram.filters.callback_data import CallbackData


con = sqlite3.connect("database.db")
cursor = con.cursor()

def main_actions() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Подробная информация"), KeyboardButton(text="Контакты")],
            [KeyboardButton(text="Записаться на тест")]
        ]
    )
    return kb


def get_calendar(year, month, message) -> InlineKeyboardMarkup:
    caldr = calendar.monthcalendar(year, month)

    today = datetime.datetime.now()
    texts = [month - 1, f"{months[month]} {year}", month + 1]

    if today.month > texts[0] and today.year > year:
        texts[0] = "❌"
    calendar_buttons = []
    for row in range(len(caldr)):
        calendar_buttons.append([])
        for column in range(len(caldr[row])):
            date_num = caldr[row][column]
            if date_num == 0:
                date_num = " "
            elif date_num < today.day and month <= today.month:
                date_num = "❌"
            if date_num == " " or date_num == "❌":
                calendar_buttons[row].append(InlineKeyboardButton(text=str(date_num), callback_data="nothing"))
            else:
                calendar_buttons[row].append(InlineKeyboardButton(
                    text=str(date_num),
                    callback_data=callback_router.DateCallbackFactory(action="set_date", day=date_num,
                                                                      month=month, year=year).pack()))

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
                            [InlineKeyboardButton(text=months[texts[0]],
                                                  callback_data=callback_router.DateCallbackFactory(action="month",
                                                                                                    day=1,
                                                                                                    year=year,
                                                                                                    month=texts[
                                                                                                        0]).pack()),
                             InlineKeyboardButton(text=texts[1], callback_data="nothing"),
                             InlineKeyboardButton(text=months[texts[2]],
                                                  callback_data=callback_router.DateCallbackFactory(action="month",
                                                                                                    year=year,
                                                                                                    day=1,
                                                                                                    month=texts[
                                                                                                        2]).pack())]
                        ] +
                        calendar_buttons
    )
    cursor.execute(f"SELECT date FROM users_data WHERE user_id = {message.from_user.id}")
    row = cursor.fetchall()
    print(row)
    if row != [] and row[0][0] != None:
        datetime_object = datetime.datetime.strptime(row[0][0], '%Y-%m-%d %H:%M:%S')
        kb = callback_router.galochka_date_db(return_keyboard=kb, db_day=datetime_object.day, db_month=datetime_object.month,
                                              db_year=datetime_object.year)
    return kb


# def get_times(message) -> InlineKeyboardMarkup:
#     from aiogram.types import InlineKeyboardButton
#     import callback_router  # Подключите ваш модуль callback_router
#
#     times = []
#     for hour in range(10, 20):
#         for minute in [0, 3]:
#             if hour == 19 and minute == 3:
#                 break
#             times.append(InlineKeyboardButton(text=f"{hour}:{minute}0",
#                                                    callback_data=callback_router.TimeCallbackFactory(
#                                                        action="times",
#                                                        hour=hour,
#                                                        minute=minute).pack()))
#     true_times = []
#     for i in range(len(times)//3+1):
#         true_times.append([])
#         for j in range(3):
#             if len(times) != 0:
#                 true_times[i].append(times[0])
#                 times.pop(0)
#
#     return_keyboard = InlineKeyboardMarkup(inline_keyboard=true_times)
#     cursor.execute(f"SELECT time FROM users_data WHERE user_id = {message.from_user.id}")
#     row = cursor.fetchall()
#     datetime_object = datetime.datetime.strptime(row[0][0], '%H:%M')
#     return_keyboard = callback_router.galochka_time_db(return_keyboard=return_keyboard, time=row[0][0])
#     return return_keyboard


def get_times() -> InlineKeyboardMarkup:
    print("CALLED 1")

    from aiogram.types import InlineKeyboardButton
    import callback_router  # Подключите ваш модуль callback_router

    times = []
    for hour in range(20, 22):
        for minute in [0, 1, 2, 3, 4, 5]:
            if hour == 22 and minute == 3:
                break
            times.append(InlineKeyboardButton(text=f"{hour}:{minute}0",
                                                   callback_data=callback_router.TimeCallbackFactory(
                                                       action="times",
                                                       hour=hour,
                                                       minute=minute).pack()))
    true_times = []
    for i in range(len(times)//3+1):
        true_times.append([])
        for j in range(3):
            if len(times) != 0:
                true_times[i].append(times[0])
                times.pop(0)

    print(true_times)

    # return_keyboard.button(text=f"{hour}:{minute}", callback_data=callback_router.
    # TimeCallbackFactory(action="times", text=f"{hour}:{minute}"))
    # return_keyboard.adjust(3)
    print(times)

    return_keyboard = InlineKeyboardMarkup(inline_keyboard=true_times)

    print(2)
    return return_keyboard