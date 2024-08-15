import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from database.database import ORM
from database.models import User
from services.telegram.handlers.states import SelectDatetime
from services.telegram.misc.keyboards import Keyboards
from services.telegram.misc.enums import TestStatus

router = Router()


@router.message(F.text == "Записаться на тестирование")
async def register_in_test(message: Message, user: User, state: FSMContext):
    if user.test_status <= TestStatus.waiting:
        today = datetime.datetime.now()
        msg = await message.answer(f"Выберите удобную дату: 📅",
                                   reply_markup=Keyboards.get_calendar(today.year, today.month))
    elif user.test_status <= TestStatus.result_sent:
        msg = await message.answer("Нельзя перезаписать начавшееся тестирование. ❌")
    elif user.test_status <= TestStatus.completed:
        msg = await message.answer(f"Тестирование было пройдено.\n\n"
                                   f"По вопросам пересдачи пишите ✍️\n"
                                   f"@alfinkly")
    await state.update_data(delete_msg=msg)
    await state.set_state(SelectDatetime.wait_date)


@router.message(F.text == "Отменить тестирование")
async def add_remove_exam(message: Message, orm: ORM, user: User, state: FSMContext):
    if user.test_status == TestStatus.waiting:
        await orm.user_repo.upsert_user(user.user_id, test_status=TestStatus.on_home)
        return await message.answer(text="Ваше тестирование удалено. ❌")
    elif user.test_status <= TestStatus.result_sent:
        return await message.answer(text="Нельзя отменить начавшееся тестирование. ❌")
    elif user.test_status <= TestStatus.completed:
        return await message.answer(text="Нельзя отменить пройденное тестирование. ❌")
    await state.clear()
