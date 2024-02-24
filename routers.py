import datetime
import sqlite3

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from methods import exist_datetime
import config
import keyboards

router = Router()
con = sqlite3.connect("database.db")
cursor = con.cursor()


@router.message(Command("start"))
async def start(message: Message):
    try:
        cursor.execute(f"SELECT user_id FROM users_data WHERE user_id = {message.from_user.id}")
        row = cursor.fetchall()
        if row == []:
            print("User not on base!")
            cursor.execute(f"INSERT INTO users_data (user_id) VALUES ({message.from_user.id});")
            con.commit()
            print("User @" + message.from_user.username + " with id-" + message.from_user.id + " added to base")
    except Exception:
        print("sql eror")
    await message.answer(
        f"Приветствую @{message.from_user.username}, Я бот Stratton.kz",
        reply_markup=keyboards.main_actions(remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Подробная информация")
async def info(message: Message):
    await message.answer(
        f"Тут должна быть информация о компании которой у меня не оказалось. Как то так :)",
        reply_markup=keyboards.main_actions(remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Контакты")
async def info(message: Message):
    await message.answer(
        f"Для связи с нами пишите  @strattonautomation",
        reply_markup=keyboards.main_actions(remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Записаться на тест")
async def info(message: Message):
    await message.answer(
        f"Укажите удобную для вас дату:",
        reply_markup=keyboards.get_calendar(2024, 2, message)
    )


@router.message(F.text == "Юху")
async def info(message: Message):
    await message.answer(
        f"Юхууу",
        reply_markup=keyboards.main_actions(remove_exam=exist_datetime(message.from_user.id))
    )


@router.message(F.text == "Отменить тестирование")
async def remove_exam(message: Message):
    try:
        cursor.execute(f"UPDATE users_data SET date=NULL, time=NULL WHERE user_id={message.from_user.id}")
        con.commit()
        await message.answer(text="Ваше тестирование удалено",
                             reply_markup=keyboards.main_actions(remove_exam=exist_datetime(message.from_user.id)))
    except Exception:
        await message.answer(text="Не удалось удалить тестирование",
                             reply_markup=keyboards.main_actions(remove_exam=exist_datetime(message.from_user.id)))


@router.message(Command("remake"))
async def start(message: Message):
    try:
        if config.DEV_MODE:
            cursor.execute(f"DELETE FROM users_data")
            con.commit()
    except Exception:
        print("sql eror")
    await message.answer(text="АНИГИЛЯЦИЯ УСПЕШНА",
                         reply_markup=keyboards.main_actions(remove_exam=exist_datetime(message.from_user.id)))


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
        await message.reply("Извините, видео должно быть не более 30 секунд.")

    if date_to < now < date_to + datetime.timedelta(minutes=3):
        await message.answer("Закончить досрочно?", reply_markup=keyboards.keyboard_is_exam_complete())
        #
    else:
        await message.answer("Вы отправили видео не в срок!")
