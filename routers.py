from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from config import TOKEN
import keyboards

router = Router()



@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        f"Приветствую @{message.from_user.username}, Я бот Staratton.kz",
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
        reply_markup=keyboards.get_calendar(2024, 2)
    )


@router.message(F.text == "Юху")
async def info(message: Message):
    await message.answer(
        f"Юхууу",
        reply_markup=keyboards.main_actions()
    )