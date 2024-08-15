from aiogram import Bot
from aiogram.types import Message, CallbackQuery


class TgActions:
    def __init__(self, tg_object: [Message, CallbackQuery, Bot], *users_id):
        self.users_id = users_id
        self.tg_object = tg_object

    async def send_message(self, text: str, **params):
        if isinstance(self.tg_object, Message):
            await self.tg_object.answer(
                text=text,
                **params
            )
        elif isinstance(self.tg_object, CallbackQuery):
            await self.tg_object.message.answer(
                text=text,
                **params
            )
        elif isinstance(self.tg_object, Bot):
            for user_id in self.users_id:
                await self.tg_object.send_message(
                    chat_id=user_id,
                    text=text,
                    **params
                )