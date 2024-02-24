import sqlite3
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
import calendar
import datetime
import callback_router
import config
import routers
from config import months
from typing import Optional
from aiogram.filters.callback_data import CallbackData

from factories import *
from methods import *

con = sqlite3.connect("database.db")
cursor = con.cursor()


def main_actions(remove_exam=False) -> ReplyKeyboardMarkup:
    keyboard = [
        [KeyboardButton(text="Подробная информация"), KeyboardButton(text="Контакты")],
        [KeyboardButton(text="Записаться на тест")]
    ]
    if remove_exam:
        keyboard[1].append(KeyboardButton(text="Отменить тестирование"))
    if config.DEV_MODE:
        keyboard.append([KeyboardButton(text="/start"), KeyboardButton(text="/remake")])
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=keyboard
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
                    callback_data=DateCallbackFactory(action="set_date", day=date_num,
                                                      month=month, year=year).pack()))

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
                            [InlineKeyboardButton(text=months[texts[0]],
                                                  callback_data=DateCallbackFactory(action="month",
                                                                                    day=1,
                                                                                    year=year,
                                                                                    month=texts[
                                                                                        0]).pack()),
                             InlineKeyboardButton(text=texts[1], callback_data="nothing"),
                             InlineKeyboardButton(text=months[texts[2]],
                                                  callback_data=DateCallbackFactory(action="month",
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
    if row != [] and row[0][0] is not None:
        datetime_object = datetime.datetime.strptime(row[0][0], '%Y-%m-%d %H:%M:%S')
        kb = galochka_date_db(return_keyboard=kb, db_day=datetime_object.day,
                              db_month=datetime_object.month,
                              db_year=datetime_object.year)
    return kb


def get_times(callback) -> InlineKeyboardMarkup:
    times = []
    start_time = 0
    print("Я работаю?")
    cursor.execute(f"SELECT date FROM users_data WHERE user_id={callback.from_user.id}")
    select = cursor.fetchall()[0][0]
    print("selectel - ", select)
    db_day = datetime.datetime.strptime(select, '%Y-%m-%d %H:%M:%S')
    today = datetime.datetime.today()
    if today.year == db_day.year and today.month == db_day.month and today.day == db_day.day:
        start_time = (today + datetime.timedelta(hours=1)).hour
    for hour in range(start_time, 24):
        times.append(InlineKeyboardButton(text=f"{hour}:00",
                                          callback_data=TimeCallbackFactory(
                                              action="times",
                                              hour=hour,
                                              minute=0).pack()))
    true_times = []
    for i in range(len(times) // 3 + 1):
        true_times.append([])
        for j in range(3):
            if len(times) != 0:
                true_times[i].append(times[0])
                times.pop(0)
    return_keyboard = InlineKeyboardMarkup(inline_keyboard=true_times)
    galochka_time_db(return_keyboard, callback)
    return return_keyboard


def keyboard_is_exam_complete(from_who) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=IsCompleteCallbackFactory(action="isComplete",
                                                                                 is_complete=1,
                                                                                 from_who=from_who).pack()),
         InlineKeyboardButton(text="Нет", callback_data=IsCompleteCallbackFactory(action="isComplete",
                                                                                  is_complete=0,
                                                                                 from_who=from_who).pack())]
    ])
    return keyboard



