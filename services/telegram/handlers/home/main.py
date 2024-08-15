from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database.models import User
from services.telegram.misc.keyboards import Keyboards

router = Router()


@router.message(F.text == "Главная")
@router.message(Command("start"))
async def home(message: Message, user: User):
    # TODO Постепенно заменять тексты на Texts
    await message.answer(
        f"Приветствую @{message.from_user.username}🙂🤝🏼 "
        f"\nЯ бот компании Stratton.kz"
        f"\nПомогу тебе получить практическое задание 👇",
        reply_markup=Keyboards.home(user=user, add_remove_exam=True if user.testing_at else False)
    )


@router.message(F.text == "Подробная информация")
async def info(message: Message, user: User):
    await message.answer(f"""🏬  Компания Stratton.kz

🤖 Мы автоматизируем бизнес-процессы посредством роботизации, внедрения чат-ботов и функциональных сайтов.

ℹ️ Подробнее о компании <a href="https://stratton.taplink.ws/p/o-kompanii/">тут</a>""",
                         reply_markup=Keyboards.home(user=user),
                         parse_mode=ParseMode.HTML
                         )


@router.message(F.text == "Контакты")
async def contact(message: Message, user: User):
    await message.answer(
        f"Для связи с нами пишите ✍️"
        f"\n@alfinkly",
        reply_markup=Keyboards.home(user=user)
    )


@router.message(F.text == "alfinkly")
async def info(message: Message):
    await message.answer(f"Мои создатель жив?")


@router.callback_query(F.data == "nothing")
async def nothing(callback: CallbackQuery):
    await callback.answer()