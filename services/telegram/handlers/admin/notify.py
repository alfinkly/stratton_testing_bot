from aiogram import Bot
from aiogram.types import CallbackQuery

from data.variables import env
from services.telegram.misc.actions import TgActions
from services.telegram.misc.enums import Sender
from services.telegram.misc.keyboards import Keyboards


async def notify_admins(bot: Bot, text: str, **params):
    tga = TgActions(bot, *env.admins)
    await tga.send_message(text, **params)


async def send_test_to_admins(callback: CallbackQuery):
    for user_id in env.admins:
        await callback.message.send_copy(chat_id=user_id,
                                         reply_markup=Keyboards.is_test_complete(from_who=Sender.admin,
                                                                                 sender=callback.from_user.id))
