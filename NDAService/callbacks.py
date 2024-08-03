from aiogram.filters.callback_data import CallbackData

class Callback(CallbackData, prefix='callback'):
    action:str

class ChangeCallback(CallbackData, prefix='change'):
    action:str
    field:str
