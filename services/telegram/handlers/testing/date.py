import datetime

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from services.telegram.misc.keyboards import Keyboards
from services.telegram.misc.callbacks import DateCallback
from services.telegram.handlers.states import SelectDatetime

router = Router()


@router.callback_query(DateCallback.filter(F.action == "set_date"),
                       SelectDatetime.wait_date)
async def set_date(callback: CallbackQuery,
                   callback_data: DateCallback,
                   state: FSMContext):
    testing_at = datetime.datetime(year=callback_data.year,
                                   month=callback_data.month,
                                   day=callback_data.day)
    await state.update_data(testing_at=testing_at, delete_msg=callback.message)
    await callback.message.edit_text(
        text=f"Выберите или напишите удобное время 🕗",
        reply_markup=Keyboards.get_times(testing_at)
    )
    await callback.answer()
    await state.set_state(SelectDatetime.wait_time)


@router.callback_query(DateCallback.filter(F.action == "month"))
async def month(callback: CallbackQuery, callback_data: DateCallback):
    await callback.message.edit_reply_markup(reply_markup=Keyboards.get_calendar(year=callback_data.year,
                                                                                 month=callback_data.month))
    await callback.answer()


@router.callback_query(F.data == "back_to_date")
async def month(callback: CallbackQuery):
    today = datetime.datetime.now()
    await callback.message.edit_text(
        text=f"Выберите удобную дату  📅",
        reply_markup=Keyboards.get_calendar(today.year, today.month)
    )
    await callback.answer()