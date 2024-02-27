import calendar
import datetime
import sqlite3

from aiogram import types
from aiogram.types import CallbackQuery

con = sqlite3.connect("database.db")
cursor = con.cursor()


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
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


def galochka_time_change(callback, callback_data, return_keyboard, time):
    for row in range(len(callback.message.reply_markup.inline_keyboard)):
        for data in range(len(callback.message.reply_markup.inline_keyboard[row])):
            if callback.message.reply_markup.inline_keyboard[row][data].text == "✅":
                time = f"{return_keyboard.inline_keyboard[row][data].callback_data.split(':')[-2]}:" \
                       f"{return_keyboard.inline_keyboard[row][data].callback_data.split(':')[-1]}0"
                return_keyboard.inline_keyboard[row][data].text = time

            if callback.message.reply_markup.inline_keyboard[row][data].text == time:
                # if callback.message.reply_markup.inline_keyboard[row][data].text ==\
                #     f"{callback_data.hour}:{callback_data.minute}0":
                print("Время изменено на", callback.message.reply_markup.inline_keyboard[row][data].text, callback_data.hour,
                      callback_data.minute)
                user_config = (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id)
                cursor.execute("UPDATE users_data SET time=? WHERE user_id=?", user_config)
                con.commit()
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


def galochka_time_db(return_keyboard, callback):
    cursor.execute(f"SELECT time FROM users_data WHERE user_id={callback.from_user.id}")
    db_row = cursor.fetchall()
    if db_row[0][0] is not None:
        time = db_row[0][0]
    else:
        return return_keyboard
    print("time from db equals - " + time)
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


def exist_datetime(user_id) -> bool:
    cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {user_id}")
    row = cursor.fetchall()
    try:
        if row[0][0] is not None and row[0][1] is not None:
            print("exist datetime on db - True")
            return True
    except Exception:
        print()
    print("exist datetime on db- False")
    return False


async def send_testing_message(callback: CallbackQuery, go_to=False):
    cursor.execute(f"SELECT test_status FROM users_data WHERE user_id = {callback.from_user.id}")
    print("testsing message")
    if go_to:
        cursor.execute("UPDATE users_data SET test_status=? WHERE user_id=?", (4, callback.from_user.id))
        con.commit()
        return
    else:
        status = cursor.fetchall()[0][0]

    next_status = 1
    match status:
        case 1:
            await callback.message.answer(text="Ваше тестирование началось. Задание: {Задание}")  # todo заменить
            next_status = 2
        case 2:
            await callback.message.answer(
                text="Ваше тестирование закончится через 10 минут, успейте отправить результаты"
                     " в виде видео до 30 секунд ")
            next_status = 3
        case 3:
            await callback.message.answer(text="Ваше тестирование окончено")
            next_status = 4
    cursor.execute("UPDATE users_data SET test_status=? WHERE user_id=?", (next_status, callback.from_user.id))
    con.commit()