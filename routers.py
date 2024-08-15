import datetime
import logging

import coloredlogs
import pytz
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message

import keyboards
import methods
from tg_config import con
from methods import exist_datetime

from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto
from services.telegram.handlers.nda.nda import GetCheckKeyboard

router = Router()
# con = sqlite3.connect("database.database", timeout=30)
# cursor = con.cursor(buffered=True)
coloredlogs.install()


