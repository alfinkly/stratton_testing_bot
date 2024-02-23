import calendar
import datetime
from aiogram import Router, F, types
from aiogram.filters.callback_data import CallbackData
import keyboards
from config import months
import sqlite3

router = Router()
con = sqlite3.connect("database.db")
cursor = con.cursor()


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
    for row in range(len(callback.message.reply_markup.inline_keyboard)):
        for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
            # if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
            #     return_keyboard.inline_keyboard[row][data].text = str(caldr[row-1][data])

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


@router.callback_query(TimeCallbackFactory.filter(F.action == "times"))
async def times(callback: types.CallbackQuery, callback_data: TimeCallbackFactory):
    print("CALLED 2")
    return_keyboard = keyboards.get_times()
    # for row in range(len(callback.message.reply_markup.inline_keyboard)):
    #     for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
    #         # if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
    #         #     return_keyboard.inline_keyboard[row][data].text = str(caldr[row-1][data])
    #
    #         if callback.message.reply_markup.inline_keyboard[row][data].text == f"{callback_data.hour}:{callback_data.minute}0":
    #             print("Edited", callback.message.reply_markup.inline_keyboard[row][data].text, callback_data.hour,
    #                   callback_data.minute)
    #             user_config = (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id)
    #             cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", user_config)
    #             con.commit()
    #             return_keyboard.inline_keyboard[row][data].text = "✅"

    galochka_time_change(callback, callback_data, return_keyboard, f"{callback_data.hour}:{callback_data.minute}0")
    await callback.message.edit_reply_markup(reply_markup=return_keyboard)
    await callback.answer()
    # except Exception:
    #     print("eroro")

