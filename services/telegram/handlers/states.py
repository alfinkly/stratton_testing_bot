from aiogram.fsm.state import StatesGroup, State


class SelectDatetime(StatesGroup):
    wait_date = State()
    wait_time = State()