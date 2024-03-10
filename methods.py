import calendar
import datetime
import logging
import coloredlogs
import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import config
import keyboards
from config import con

# cursor = con.cursor(buffered=True)
coloredlogs.install()


def galochka_date_change(callback, callback_data, return_keyboard):
    cursor = con.cursor(buffered=True)
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
                cursor.execute("UPDATE users_data SET date=%s WHERE user_id=%s", user_config)
                con.commit()
                cursor.close()
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
                print("Время изменено на", callback.message.reply_markup.inline_keyboard[row][data].text,
                      callback_data.hour,
                      callback_data.minute)
                user_config = (f"{callback_data.hour}:{callback_data.minute}0", callback.from_user.id)
                cursor = con.cursor(buffered=True)
                cursor.execute("UPDATE users_data SET time=%s WHERE user_id=%s", user_config)
                con.commit()
                cursor.close()
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


def galochka_time_db(return_keyboard, callback):
    cursor = con.cursor(buffered=True)
    cursor.execute(f"SELECT time FROM users_data WHERE user_id={callback.from_user.id}")
    db_row = cursor.fetchall()
    cursor.close()
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
                # cursor.execute("UPDATE users_data SET time=%s WHERE user_id=%s", user_config)
                # con.commit()
                return_keyboard.inline_keyboard[row][data].text = "✅"
    return return_keyboard


def exist_datetime(user_id) -> bool:
    cursor = con.cursor(buffered=True)
    cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {user_id}")
    row = cursor.fetchall()
    cursor.close()
    try:
        if row[0][0] is not None and row[0][1] is not None:
            return True
    except Exception:
        logging.warning("Нет даты и времени в базе данных")
    return False


async def send_testing_message_bot(user_id=None, bot=None, username=None, to_complete=False, run_date=None,
                                   test_status=None):
    cursor = con.cursor(buffered=True)
    cursor.execute(f"SELECT test_status, run_date FROM users_data WHERE user_id = {user_id}")
    test_status_db, run_date_db = cursor.fetchone()
    print(test_status_db, run_date_db)
    if to_complete:
        cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s", (6, user_id))
        con.commit()
        return
    if run_date_db is not None:
        run_date_db = datetime.datetime.strptime(run_date_db, "%Y-%m-%d %H:%M:%S")
        if run_date < run_date_db:
            return
    if test_status is not None:
        if test_status_db == test_status - 1:
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s",
                           (test_status, user_id))
            con.commit()
        elif test_status_db in [2, 3] and test_status == 4:
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s",
                           (test_status, user_id))
            con.commit()
        else:
            return
    cursor.close()
    match test_status:
        case 2:
            await bot.send_message(chat_id=int(user_id), text="Ваше тестирование началось, успехов!\n\n"
                                                              "Время на выполнение: 4 часа\n"
                                                              "Задание будет на проверке когда вы отправите видео ✅\n\n"
                                                              f"Задание: {config.task}\n\n"
                                                              "Результат выслать в формате:\n"
                                                              "- видео работы кода до 30 секунд;\n"
                                                              "- ссылка на запущенного бота.",
                                   reply_markup=keyboards.main_actions(user_id=user_id, username=username))
            await bot.send_message(chat_id=int(user_id), text="Нажмите на кнопку когда приступите к тестированию",
                                   reply_markup=keyboards.on_task)
        case 3:
            await bot.send_message(chat_id=int(user_id), text="У Вас есть 10 минут, чтобы отправить результаты!",
                                   reply_markup=keyboards.main_actions(user_id=user_id,
                                                                       username=username))
        case 5:
            await bot.send_message(chat_id=int(user_id), text="Ваше тестирование не выполнено"
                                                              f"\nПо вопросам пересдачи пишите  ✍️"
                                                              f"\n@strattonautomation",
                                   reply_markup=keyboards.main_actions(user_id=user_id,
                                                                       username=username))


async def send_testing_message_callback(callback=None, to_complete=False, run_date=None, test_status=None):
    cursor = con.cursor(buffered=True)
    cursor.execute(f"SELECT test_status, run_date FROM users_data WHERE user_id = {callback.from_user.id}")
    if to_complete:
        cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s", (6, callback.from_user.id))
        con.commit()
        return
    test_status_db, run_date_db = cursor.fetchone()
    if run_date_db is not None:  # если не нулевой, то превратить в объект datetime
        run_date_db = datetime.datetime.strptime(run_date_db, "%Y-%m-%d %H:%M:%S")
        if run_date < run_date_db:
            return
    if test_status is not None:
        if test_status_db == test_status - 1:
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s",
                           (test_status, callback.from_user.id))
            con.commit()
        elif test_status_db in [2, 3] and test_status == 4:
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s",
                           (test_status, callback.from_user.id))
            con.commit()
        else:
            return
    cursor.close()
    match test_status:
        case 2:
            await callback.message.answer(text="Ваше тестирование началось, успехов!\n\n"
                                               "Время на выполнение: 4 часа\n"
                                               "Задание будет на проверке когда вы отправите видео или ссылку "
                                               "и нажмете кнопку \"Отправить тестирование\" ✅\n\n"
                                               f"Задание: {config.task}\n\n"
                                               "Результат выслать в формате:\n"
                                               "- видео работы кода до 40 секунд и размером не более 10МБ;\n"
                                               "- ссылка на запущенного бота.",
                                          reply_markup=keyboards.main_actions(user_id=callback.from_user.id,
                                                                              username=callback.from_user.username))
            await callback.message.answer(text="Нажмите на кнопку когда приступите к тестированию",
                                          reply_markup=keyboards.on_task)
        case 3:
            await callback.message.answer(text="У Вас есть 10 минут, чтобы отправить результаты!",
                                          reply_markup=keyboards.main_actions(user_id=callback.from_user.id,
                                                                              username=callback.from_user.username))
        case 5:
            await callback.message.answer(text="Ваше тестирование не выполнено"
                                               f"\nПо вопросам пересдачи пишите  ✍️"
                                               f"\n@strattonautomation",
                                          reply_markup=keyboards.main_actions(user_id=callback.from_user.id,
                                                                              username=callback.from_user.username))


async def send_testing_message_m(message=None, to_complete=False, run_date=None, test_status=None):
    cursor = con.cursor(buffered=True)
    cursor.execute(f"SELECT test_status, run_date FROM users_data WHERE user_id = {message.from_user.id}")
    if to_complete:
        cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s",
                       (6, message.from_user.id))
        con.commit()
        logging.warning("test_message_not_1")
        return
    test_status_db, run_date_db = cursor.fetchone()
    if run_date_db is not None:
        run_date_db = datetime.datetime.strptime(run_date_db, "%Y-%m-%d %H:%M:%S")
        if run_date < run_date_db:
            logging.warning("test_message_not_2")
            return
    if test_status is not None:
        if test_status_db == test_status - 1:
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s",
                           (test_status, message.from_user.id))
            con.commit()
        elif test_status_db in [2, 3] and test_status == 5:
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s",
                           (test_status, message.from_user.id))
            con.commit()
        else:
            logging.warning("test_message_not_3")
            return
    cursor.close()
    match test_status:
        case 2:
            await message.answer(text="Ваше тестирование началось, успехов!\n\n"
                                      "Время на выполнение: 4 часа\n"
                                      "Задание будет на проверке когда вы отправите видео ✅\n\n"
                                      f"Задание: {config.task}\n\n"
                                      "Результат выслать в формате:\n"
                                      "- видео работы кода до 30 секунд;\n"
                                      "- ссылка на запущенного бота.",
                                 reply_markup=keyboards.main_actions(user_id=message.from_user.id,
                                                                     username=message.from_user.username))
            await message.answer(text="Нажмите на кнопку когда приступите к тестированию",
                                 reply_markup=keyboards.on_task)
        case 3:
            await message.answer(
                text="У Вас есть 10 минут, чтобы отправить результаты!",
                reply_markup=keyboards.main_actions(user_id=message.from_user.id,
                                                    username=message.from_user.username))
        case 5:
            await message.answer(text="Ваше тестирование не выполнено"
                                      f"\nПо вопросам пересдачи пишите  ✍️"
                                      f"\n@strattonautomation",
                                 reply_markup=keyboards.main_actions(user_id=message.from_user.id,
                                                                     username=message.from_user.username))


def get_test_status(user_id, username):
    cursor = con.cursor(buffered=True)
    cursor.execute(f"SELECT test_status, user_id FROM users_data WHERE user_id = {user_id}")
    row = cursor.fetchone()
    cursor.close()
    print(row)
    if row is None:
        add_user(user_id, username)
        return row
    return row[0]


def add_user(user_id, username):
    cursor = con.cursor(buffered=True)
    cursor.execute(f"INSERT INTO users_data (user_id, username) VALUES (%s, %s);", (user_id, username))
    con.commit()
    cursor.close()
    logging.info(f"Пользователь @{username} с id - {user_id} добавлен")


async def appoint_test(message, time):
    now = datetime.datetime.now()
    if time.hour <= now.hour and time.minute <= now.minute:
        return await message.answer(text="Указанное время уже прошло ⌛️. ")
    cursor = con.cursor(buffered=True)
    cursor.execute(
        f"UPDATE users_data SET time='{time.strftime('%H:%M')}', test_status=1 WHERE user_id={message.from_user.id}")
    con.commit()
    cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {message.from_user.id}")
    row_db = cursor.fetchone()
    print(row_db)
    if row_db != [] and row_db[0][0] is not None and row_db[0][1] is not None:
        date_to = datetime.datetime.strptime(row_db[0].split(" ")[0] + " " + time.strftime('%H:%M'),
                                             '%Y-%m-%d %H:%M')

    scheduler = AsyncIOScheduler(timezone=tzlocal.get_localzone_name())
    started_at = datetime.datetime.strptime(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "%Y-%m-%d %H:%M:%S")
    cursor.execute("UPDATE users_data SET run_date=%s WHERE user_id=%s", (started_at, message.from_user.id))
    con.commit()
    scheduler.add_job(send_testing_message_m, trigger='date', run_date=date_to,
                      kwargs={"message": message, "run_date": started_at, "test_status": 2})
    scheduler.add_job(send_testing_message_m, trigger='date',
                      run_date=str(date_to + config.exam_times["send_notification"]),
                      kwargs={"message": message, "run_date": started_at, "test_status": 3})
    scheduler.add_job(send_testing_message_m, trigger='date', run_date=str(date_to +
                                                                           config.exam_times["duration"]),
                      kwargs={"message": message, "run_date": started_at, "test_status": 5})
    scheduler.start()
    cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {message.from_user.id}")
    row_db = cursor.fetchall()
    cursor.close()
    dates = row_db[0][0].split(' ')[0].split('-')
    date = f"{dates[2]}.{dates[1]}.{dates[0]}"
    await message.answer(text="Ура! Вы назначили себе задание! 🙂"
                              "\n"
                              f"\nДата: {date}"
                              f"\nВремя: {row_db[0][1]}"
                              "\nВремя на выполнение: 4 часа"
                              "\n"
                              "\nТеперь ожидайте задание 🙂",
                         reply_markup=keyboards.main_actions(user_id=message.from_user.id,
                                                             username=message.from_user.username,
                                                             add_remove_exam=exist_datetime(message.from_user.id)))


# Select request from db
def sql_db_select(columns: list, filter=None, table="users_data"):
    columns = ", ".join(columns)
    cursor = con.cursor()
    if filter is not None:
        query = f"SELECT {columns} FROM {table} WHERE {filter[0]}={filter[filter[0]]}"
        cursor.execute(query)
        row = cursor.fetchone()
    else:
        query = f"SELECT {columns} FROM {table}"
        cursor.execute(query)
        row = cursor.fetchall()
    cursor.close()
    logging.info(query)
    return row


# {"tag": "home_text"}
def sql_db_update(columns: dict, filter: dict, table="users_date"):
    set_query = ""

    for col in columns:
        set_query += col + "=" + str(columns[col]) + ", "
    else:
        set_query = set_query.removesuffix(", ")

    cursor = con.cursor()
    query = f"UPDATE {table} SET {set_query} WHERE {filter}={filter[filter[0]]}"
    cursor.execute(query)
    con.commit()
    cursor.close()

    logging.info(query)


def exist_user(user_id):
    cursor = con.cursor()
    cursor.execute(f"SELECT user_id FROM users_data WHERE user_id={user_id}")
    if cursor.fetchone()[0] is not None:
        return True
    else:
        return False
