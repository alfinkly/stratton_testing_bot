from random import randint

from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, ReplyKeyboardRemove
from config import TOKEN
import keyboards

router = Router()


class DateCallbackFactory(CallbackData, prefix='fabnum'):
    action: str
    day: int = None
    month: str = None


@router.callback_query(DateCallbackFactory.filter(F.action == "set_date"))
async def send_random_value(callback: types.CallbackQuery, callback_data: DateCallbackFactory):
    await callback.message.answer(f"Вы записаны на {callback_data.day} {callback_data.month}")

    for markup in callback.message.reply_markup.inline_keyboard:
        print(markup, "\n")
    # await bot.edit_message_reply_markup(callback.message.chat.id,
    #                                     callback.message.message_id,
    #                                     reply_markup=callback.message.reply_markup)
    # await edit_reply_mark([], callback)
    await callback.answer()


@router.callback_query(F.data == "nothing")
async def send_random_value(callback: types.CallbackQuery):
    await callback.answer()