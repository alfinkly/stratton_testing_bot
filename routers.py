import sqlite3

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from config import TOKEN
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
    except Exception:
        print("sql eror")
    await message.answer(
        f"Приветствую @{message.from_user.username}, Я бот Stratton.kz",
        reply_markup=keyboards.main_actions()
    )


@router.message(F.text == "Подробная информация")
async def info(message: Message):
    await message.answer(
        f"Тут должна быть информация о компании которой у меня не оказалось. Как то так :)",
        reply_markup=keyboards.main_actions()
    )


@router.message(F.text == "Контакты")
async def info(message: Message):
    await message.answer(
        f"Для связи с нами пишите  @strattonautomation",
        reply_markup=keyboards.main_actions()
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
        reply_markup=keyboards.main_actions()
    )