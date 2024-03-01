import datetime
import logging
import sqlite3

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import methods
from methods import exist_datetime
import config
import keyboards

router = Router()
con = sqlite3.connect("database.db", timeout=30)
cursor = con.cursor()


@router.message(Command("start"))
async def start(message: Message):
    # try:
    cursor.execute(f"SELECT user_id FROM users_data WHERE user_id = {message.from_user.id}")
    row = cursor.fetchall()
    if row == []:
        cursor.execute(f"INSERT INTO users_data (user_id) VALUES ({str(message.from_user.id)});")
        con.commit()
        logging.info(f"Пользователь @{message.from_user.username} с id - {message.from_user.id} добавлен")
    # except Exception:
    #     logging.error("Не удалось добавить пользователя")
    await message.answer(
        f"Приветствую @{message.from_user.username}🙂🤝🏼 "
        f"\nЯ бот компании Stratton.kz"
        f"\nПомогу тебе получить практическое задание 👇",
        reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Главная")
async def start(message: Message):
    await message.answer(
        f"Приветствую @{message.from_user.username}🙂🤝🏼 "
        f"\nЯ бот компании Stratton.kz"
        f"\nПомогу тебе получить практическое задание 👇",
        reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Подробная информация")
async def info(message: Message):
    await message.answer(
        f"Компания Stratton.kz  🏬"
        f"\n"
        f"\n🤖  Мы разрабатываем чат-боты Telegram для бизнеса. Наши боты сделаны не на конструкторах, а пишутся с нуля."
        f"\n"
        f"\n🤖  Мы разрабатываем чат-боты Instagram для бизнеса. Автоматизируйте общение с клиентами и улучшайте продажи в Instagram. Просто и удобно."
        f"\n"
        f"\nРоботизация бизнес-процессов избавляет от рутины и выгорания сотрудников, повышает точность и скорость выполнения операций."
        f"\n"
        f"\nПовысьте узнаваемость своих услуг и продуктов с помощью удобного сайта.",
        reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Контакты")
async def info(message: Message):
    await message.answer(
        f"Для связи с нами пишите ✍️"
        f"\n@strattonautomation",
        reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Записаться на тестирование")
async def info(message: Message):
    if methods.is_status_active(message):
        cursor.execute(f"select test_status from users_data where user_id={message.from_user.id}")
        try:
            row = cursor.fetchone()
            if row[0] is None or row[0] == 1:
                await message.answer(
                    f"Выберите удобную дату  📅",
                    reply_markup=keyboards.get_calendar(2024, 2, message)
                )
        except Exception:
            print("Error 4444")
    else:
        await message.answer(
            f"Тестирование было пройдено"
            f"\n"
            f"\nПо вопросам пересдачи пишите  ✍️"
            f"\n@strattonautomation",
        )


@router.message(F.text == "Юху")
async def info(message: Message):
    await message.answer(
        f"Юхууу",
        reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Отменить тестирование")
async def add_remove_exam(message: Message):
    try:
        if methods.is_status_active(message):
            cursor.execute(f"UPDATE users_data SET date=NULL, time=NULL, test_status=NULL "
                           f"WHERE user_id={message.from_user.id}")
            con.commit()
            return await message.answer(text="Ваше тестирование удалено  ❌",
                                        reply_markup=keyboards.main_actions(message=message,
                                                                            add_remove_exam=exist_datetime(
                                                                                message.from_user.id)))
    except Exception:
        return await message.answer(text="Не удалось удалить тестирование",
                                    reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(
                                        message.from_user.id)))
    return await message.answer(text="Нельзя отменить пройденное тестирование  ❌",
                                reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(
                                    message.from_user.id)))


@router.message(Command("remake"))
async def start(message: Message):
    try:
        if config.DEV_MODE:
            cursor.execute(f"DELETE FROM users_data")
            con.commit()
            print("remaked!")
            await message.answer(text="АНИГИЛЯЦИЯ УСПЕШНА",
                                 reply_markup=keyboards.main_actions(message=message, add_remove_exam=exist_datetime(
                                     message.from_user.id)))
    except Exception:
        print("remake eror")


@router.message(F.video)
async def video(message: Message):
    cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {message.from_user.id}")
    row_db = cursor.fetchall()
    date_to = datetime.datetime.strptime(row_db[0][0].split(" ")[0] + " " + row_db[0][1] +
                                         ":00", '%Y-%m-%d %H:%M:%S')
    now = datetime.datetime.now()
    print(now < date_to)
    print(date_to)
    print(date_to + datetime.timedelta(minutes=3))
    if message.video.duration > 30:
        await message.reply("Извините, видео должно быть не более 30 секунд.  🕗")

    if date_to < now < date_to + config.exam_times["duration"]:  # or config.DEV_MODE:
        await message.send_copy(message.from_user.id,
                                reply_markup=keyboards.keyboard_is_exam_complete(from_who=0,
                                                                                 sender=message.from_user.id))
    else:
        await message.answer("Вы отправили видео не в срок!  ⌛️")
