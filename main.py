import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup

import callback_router
import config
import keyboards
import routers
from config import TOKEN
from factories import IsCompleteCallbackFactory, TimeCallbackFactory
from methods import send_testing_message

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(routers.router, callback_router.router)


@dp.callback_query(IsCompleteCallbackFactory.filter(F.action == "isComplete"))
async def times(callback: types.CallbackQuery, callback_data: TimeCallbackFactory):
    if callback_data.from_who == 0:
        if callback_data.is_complete == 0:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        elif callback_data.is_complete == 1:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await send_testing_message(callback, go_to=True)
        await callback.message.send_copy(config.checker_id, reply_markup=keyboards.
                                         keyboard_is_exam_complete(from_who=1, sender=callback.from_user.id))
    elif callback_data.from_who == 1:
        if callback_data.is_complete == 0:
            await callback.message.answer(text=f"Вы отклонили тестирование")
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await bot.send_message(callback_data.sender, text="Тестирование отклонен")
        elif callback_data.is_complete == 1:
            await callback.message.answer(text=f"Вы приняли тестирование")
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await bot.send_message(callback_data.sender, text="Тестирование принято")
            await send_testing_message(callback, go_to=True)
    await callback.answer()


async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
    print("Started!")
