from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from database.database import ORM
from services.scheduler.add import add_testing_jobs
from services.telegram.misc.callbacks import TimeCallback
from services.telegram.handlers.states import SelectDatetime
import datetime

from config import Environ
from data.variables import TEST_APPOINT, TEST_APPOINT_TO_ADMIN
from database.models import User
from services.telegram.misc.actions import TgActions
from services.telegram.misc.enums import TestStatus

router = Router()


@router.message(F.text, SelectDatetime.wait_time)
async def set_time(message: Message, state: FSMContext, user: User, orm: ORM, scheduler: AsyncIOScheduler,
                   env: Environ):
    data = await state.get_data()
    testing_at: datetime.datetime = data["testing_at"]
    testing_at = with_time(testing_at, message.text)
    if testing_at is None:
        return await message.answer("Это не похоже на время")
    elif is_time_over(testing_at):
        return await message.answer("Указанное время уже прошло ⌛️")

    user = await orm.user_repo.upsert_user(user.user_id, test_status=TestStatus.waiting, testing_at=testing_at)
    await add_testing_jobs(scheduler, message, user.user_id, orm)

    text_date = testing_at.strftime('%Y.%m.%d')
    text_time = testing_at.strftime('%H:%M')
    await message.answer(text=TEST_APPOINT.format(text_date, text_time))
    tga = TgActions(message.bot, *env.admins)
    await tga.send_message(text=TEST_APPOINT_TO_ADMIN.format(user.username, user.fullname, text_date, text_time,
                                                             user.phone_number))

    await message.delete()
    await data["delete_msg"].delete()


@router.callback_query(TimeCallback.filter(F.action == "times"))
async def time_select(callback: CallbackQuery, callback_data: TimeCallback, state: FSMContext, user: User, orm: ORM,
                      scheduler: AsyncIOScheduler, env: Environ):
    data = await state.get_data()
    date: datetime.datetime = data["testing_at"]
    testing_at = date.replace(hour=callback_data.hour, minute=callback_data.minute)

    if is_time_over(testing_at):
        return await callback.message.answer(text="Указанное время уже прошло ⌛️")

    await orm.user_repo.upsert_user(user.user_id, test_status=TestStatus.waiting, testing_at=testing_at)
    await add_testing_jobs(scheduler, callback, user.user_id, orm)

    text_date = testing_at.strftime('%Y.%m.%d')
    text_time = testing_at.strftime('%H:%M')
    await callback.message.edit_text(text=TEST_APPOINT.format(text_date, text_time),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
    tga = TgActions(callback.bot, *env.admins)
    await tga.send_message(text=TEST_APPOINT_TO_ADMIN.format(user.username, user.fullname, text_date, text_time,
                                                             user.phone_number))
    await callback.answer()


def is_time_over(time) -> bool:
    now = datetime.datetime.now()
    if time <= now:
        return True
    return False


def with_time(date, text) -> datetime:
    for time_format in ["%H:%M", "%H %M", "%H-%M", "%H.%M", "%H_%M"]:
        try:
            time = datetime.datetime.strptime(text, time_format)
            result = date.replace(hour=time.hour, minute=time.minute)
            return result

        except ValueError:
            continue