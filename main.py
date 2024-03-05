import asyncio
import datetime

import tzlocal
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup
import logging
import coloredlogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import callback_router
import config
import keyboards
import routers
from config import TOKEN, con
from factories import IsCompleteCallbackFactory, TimeCallbackFactory
from methods import send_testing_message

bot = Bot(token=TOKEN)
dp = Dispatcher()
dp.include_routers(routers.router, callback_router.router)
coloredlogs.install()
cursor = con.cursor()


@dp.callback_query(IsCompleteCallbackFactory.filter(F.action == "isComplete"))
async def times(callback: types.CallbackQuery, callback_data: IsCompleteCallbackFactory):
    if callback_data.from_who == 0:
        if callback_data.is_complete == 0:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        elif callback_data.is_complete == 1:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await send_testing_message(callback, go_to=True)
            await callback.message.send_copy(config.checker_id, reply_markup=keyboards.
                                             keyboard_is_exam_complete(from_who=1, sender=callback.from_user.id))
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s", (4, callback.from_user.id))
            con.commit()
    elif callback_data.from_who == 1:
        if callback_data.is_complete == 0:
            await callback.message.answer(text=f"Вы отклонили тестирование ❌")
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await bot.send_message(callback_data.sender, text="Тестирование отклонен ❌")
        elif callback_data.is_complete == 1:
            await callback.message.answer(text=f"Вы приняли тестирование ✅")
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await bot.send_message(callback_data.sender, text="Тестирование принято ✅")
            await send_testing_message(callback, go_to=True)
    await callback.answer()


async def reactive_jobs():
    cursor = con.cursor(buffered=True)
    cursor.execute("SELECT user_id, date, time FROM stratton_bot_data.users_data "
                   "WHERE user_id is not null and date is not null and time is not null and test_status = 1")
    users = cursor.fetchall()
    for user in users:
        print(user)
        date_to = datetime.datetime.strptime(user[1].split(" ")[0] + " " + user[2],
                                             '%Y-%m-%d %H:%M')
        scheduler = AsyncIOScheduler(timezone=tzlocal.get_localzone_name())
        started_at = datetime.datetime.now()
        cursor.execute("UPDATE users_data SET run_date=%s WHERE user_id=%s", (started_at, user[0]))
        con.commit()

        scheduler.add_job(send_testing_message, trigger='date', run_date=date_to,
                          kwargs={"callback": callback, "run_date": started_at})
        scheduler.add_job(send_testing_message, trigger='date',
                          run_date=str(date_to + config.exam_times["send_notification"]),
                          kwargs={"callback": callback, "run_date": started_at})
        scheduler.add_job(send_testing_message, trigger='date', run_date=str(date_to +
                                                                             config.exam_times["duration"]),
                          kwargs={"callback": callback, "run_date": started_at})
        scheduler.start()


async def start_bot():
    await reactive_jobs()
    logging.basicConfig(level=logging.DEBUG)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
    print("Started!")
