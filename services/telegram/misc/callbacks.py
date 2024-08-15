from aiogram.filters.callback_data import CallbackData


class DateCallback(CallbackData, prefix='date'):
    action: str
    day: int = None
    month: int = None
    year: int = None


class TimeCallback(CallbackData, prefix='time'):
    action: str
    hour: int = None
    minute: int = None


class IsCompleteCallback(CallbackData, prefix='isc'):
    action: str
    is_complete: int  # 1 - yes; 0 - no
    from_who: int  # 1 - checker; 0 - tester
    sender: int = None


class Callback(CallbackData, prefix='callback'):
    action: str


class ChangeCallback(CallbackData, prefix='change'):
    action: str
    field: str
