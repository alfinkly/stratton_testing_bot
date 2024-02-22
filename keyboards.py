from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import calendar
import datetime

import callback_router
from config import months
from typing import Optional
from aiogram.filters.callback_data import CallbackData


def main_actions() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [KeyboardButton(text="Подробная информация"), KeyboardButton(text="Контакты")],
            [KeyboardButton(text="Записаться на тест")]
        ]
    )
    return kb


def get_calendar(year, month) -> ReplyKeyboardMarkup:
    caldr = calendar.monthcalendar(year, month)

    today = datetime.datetime.now()
    print(today.day)
    texts = [month-1, f"{months[month]} {year}", month+1]

    if today.month > texts[0] and today.year > year:
        texts[0] = "❌"
    calendar_buttons = []
    for row in range(len(caldr)):
        calendar_buttons.append([])
        for column in range(len(caldr[row])):
            date_num = caldr[row][column]
            if date_num == 0:
                date_num = " "
            elif date_num < today.day:
                date_num = "❌"
            if date_num == " " or date_num == "❌":
                calendar_buttons[row].append(InlineKeyboardButton(text=str(date_num), callback_data="nothing"))
            else:
                calendar_buttons[row].append(InlineKeyboardButton(
                    text=str(date_num),
                    callback_data=callback_router.DateCallbackFactory(action="set_date", day=date_num, month=months[month]).pack()))

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=months[texts[0]], callback_data="nothing"),
             InlineKeyboardButton(text=texts[1], callback_data="nothing"),
             InlineKeyboardButton(text=months[texts[2]], callback_data="nothing")]
        ] +
            calendar_buttons
    )
    return kb