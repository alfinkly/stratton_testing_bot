import calendar
import datetime
import logging

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

from data.variables import months, env
from database.models import User
from services.telegram.misc.callbacks import DateCallback, TimeCallback, IsCompleteCallback
from services.telegram.misc.enums import TestStatus, Sender


class Keyboards:
    """
    TODO Заменить подклассами
    """

    @staticmethod
    def send_phone():
        return ReplyKeyboardMarkup(resize_keyboard=True,
                                   one_time_keyboard=True,
                                   keyboard=[[
                                       KeyboardButton(text='Поделиться номером телефона', request_contact=True)
                                   ]])

    @staticmethod
    def home(user: User, add_remove_exam=False) -> ReplyKeyboardMarkup:
        keyboard = [
            [
                KeyboardButton(text="Главная"),
                KeyboardButton(text="Подробная информация"),
                KeyboardButton(text="Контакты")
            ],
            []
        ]
        if user.test_status is TestStatus.waiting or TestStatus.on_home:
            keyboard[1].append(KeyboardButton(text="Записаться на тестирование"))
        if add_remove_exam and user.test_status is TestStatus.waiting:
            keyboard[1].append(KeyboardButton(text="Отменить тестирование"))
        if True:
            keyboard.append([KeyboardButton(text="/start"), KeyboardButton(text="/remake")])
        markup = ReplyKeyboardMarkup(
            resize_keyboard=True,
            keyboard=keyboard
        )
        return markup

    @staticmethod
    def get_calendar(year, month) -> InlineKeyboardMarkup:
        today = datetime.datetime.now()
        caldr = calendar.monthcalendar(year, month)
        open_days = today + datetime.timedelta(days=7)
        header = [InlineKeyboardButton(text="❌", callback_data="nothing"),
                  f"{months[month]} {year}",
                  InlineKeyboardButton(text="❌", callback_data="nothing")]
        if open_days.month != today.month and today.year == open_days.year:
            logging.info(f"{open_days.month} < {month}")
            if open_days.month < month:
                header[0] = InlineKeyboardButton(text=months[month - 1],
                                                 callback_data=DateCallback(action="month",
                                                                            day=1,
                                                                            year=year,
                                                                            month=month - 1).pack())
            elif open_days.month > month:
                header[2] = InlineKeyboardButton(text=months[month + 1],
                                                 callback_data=DateCallback(action="month",
                                                                            day=1,
                                                                            year=year,
                                                                            month=month + 1).pack())
            elif open_days.month > today.month:
                header[0] = InlineKeyboardButton(text=months[month - 1],
                                                 callback_data=DateCallback(action="month",
                                                                            day=1,
                                                                            year=year,
                                                                            month=month - 1).pack())
        calendar_buttons = []
        for row in range(len(caldr)):
            calendar_buttons.append([])
            for column in range(len(caldr[row])):
                date_num = caldr[row][column]
                if date_num == 0:
                    date_num = " "
                elif not (
                        today.timetuple().tm_yday <= datetime.datetime(year, month, date_num).timetuple().tm_yday <
                        today.timetuple().tm_yday + 7) or (date_num == today.day and today.hour == 23):
                    date_num = "❌"
                if date_num == " " or date_num == "❌":
                    calendar_buttons[row].append(InlineKeyboardButton(text=str(date_num), callback_data="nothing"))
                else:
                    calendar_buttons[row].append(InlineKeyboardButton(
                        text=str(date_num),
                        callback_data=DateCallback(action="set_date", day=date_num,
                                                   month=month, year=year).pack()))

        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                                [header[0],
                                 InlineKeyboardButton(text=header[1], callback_data="nothing"),
                                 header[2]]
                            ] + calendar_buttons
        )
        return kb

    @staticmethod
    def get_times(date: datetime.datetime) -> InlineKeyboardMarkup:
        times_buttons = []
        today = datetime.datetime.now()
        current_hour = 0
        if date.year == today.year and date.month == today.month and date.day == today.day:
            current_hour = today.hour
        for hour in range(current_hour + 1, 24):
            times_buttons.append(
                InlineKeyboardButton(
                    text=f"{hour}:00",
                    callback_data=TimeCallback(action="times", hour=hour, minute=0).pack()
                )
            )

        keyboard = [
            times_buttons[i:i + 3] for i in range(0, len(times_buttons), 3)
        ]
        keyboard.append([InlineKeyboardButton(text="Назад  ◀️", callback_data="back_to_date")])
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    @staticmethod
    def is_test_complete(from_who, sender) -> InlineKeyboardMarkup:
        texts = []
        if from_who is Sender.user:
            texts = ["Отправить тестирование", "Не отправлять"]
        elif from_who is Sender.admin:
            texts = ["Принять тестирование", "Отклонить тестирование"]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=texts[0], callback_data=IsCompleteCallback(action="isComplete",
                                                                                  is_complete=1,
                                                                                  from_who=from_who,
                                                                                  sender=sender).pack())],
            [InlineKeyboardButton(text=texts[1], callback_data=IsCompleteCallback(action="isComplete",
                                                                                  is_complete=0,
                                                                                  from_who=from_who,
                                                                                  sender=sender).pack())]
        ])
        return keyboard

    @staticmethod
    def on_task():
        return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Приступить к тестированию",
                                                                           callback_data="on_task")]])

    @staticmethod
    def invite_to_group():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Войти в группу", url=env.invite_to_group)]
        ])