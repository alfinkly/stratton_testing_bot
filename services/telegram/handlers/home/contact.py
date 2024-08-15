from aiogram import F, Router
from aiogram.types import Message, ReplyKeyboardMarkup, TelegramObject

from database.database import ORM
from services.telegram.handlers.home.main import home
from services.telegram.misc.keyboards import Keyboards

router = Router()


async def ask_contact(event: TelegramObject):
    await event.bot.send_message(chat_id=event.from_user.id,
                                 text="Для регистрации нажмите на кнопку ⬇️",
                                 reply_markup=Keyboards.send_phone())


@router.message(F.contact)
async def contact_received(message: Message, orm: ORM):
    user = await orm.user_repo.save_user(message)
    await message.answer("Спасибо за предоставленную информацию!", reply_markup=ReplyKeyboardMarkup(keyboard=[[]]))
    await home(message, user)
