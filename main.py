import asyncio
from aiogram import Bot, Dispatcher

import callback_router
import routers
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(routers.router, callback_router.router)


# async def edit_reply_mark(mark, callback):
#     await bot.edit_message_reply_markup(callback.message.chat.id,
#                                         callback.message.message_id,
#                                         reply_markup=mark)


async def start_bot():
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(start_bot())
    print("Started!")
