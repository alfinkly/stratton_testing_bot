from pathlib import Path
from environs import Env
import datetime
import mysql.connector
import os

from functions.misc import load_json


DIRECTORY_PROJECT = Path(__file__).parent
DIRECTORY_PROJECT_DATA = DIRECTORY_PROJECT / 'data'
DIRECTORY_FILES = DIRECTORY_PROJECT_DATA / 'files'
JSON_FILES = DIRECTORY_FILES / "json"
JSON_DEFAULT = JSON_FILES / "default"
JSON_CONFIG = JSON_FILES / "config"

os.makedirs(DIRECTORY_PROJECT_DATA, exist_ok=True)
os.makedirs(DIRECTORY_FILES, exist_ok=True)
os.makedirs(JSON_FILES, exist_ok=True)
os.makedirs(JSON_DEFAULT, exist_ok=True)
os.makedirs(JSON_CONFIG, exist_ok=True)

months = {1: "Январь", 2: "Февраль", 
          3: "Март", 4: "Апрель", 
          5: "Май", 6: "Июнь", 
          7: "Июль", 8: "Август", 
          9: "Сентябрь", 10: "Октябрь", 
          11: "Ноябрь", 12: "Декабрь"}

checker_ids = load_json("checker_ids")

exam_times = {
    "duration": datetime.timedelta(hours=4),
    "send_notification": datetime.timedelta(hours=3, minutes=50)
}

tasks = [
    "Напишите бота с командой /timer, после которой бот напишет пользователю через 5 секунд и напишет дату начала и "
    "конца таймера.",
    "Напишите команду /wiki для получения краткой информации из Википедии по запросу пользователя.",
    "Напишите команду /poll для проведения опроса с использованием InlineKeyboardButton и отправки результатов и "
    "имени пользователя администратору.",
    "Напишите бота для отправки изображения в ответ на команду /image.",
    "Напишите бота для игры в камень-ножницы-бумагу с помощью кнопок.",
    "Создайте клавиатуру с кнопками: при нажатии первой кнопки бот отправит изображение, а при нажатии второй - "
    "файл.",
    "Разработайте функцию для обработки текстовых сообщений от пользователя и отправки ответа в виде эхо-сообщения.",
    "Напишите бота, который будет писать всем пользователям из базы данных в 8:00 \"Доброе утро\".",
    "Реализуйте функцию для записи информации о пользователях в базу данных при первом взаимодействии.",
    "Напишите бота, который предлагает пользователю пройти опрос с помощью кнопок и сохранить результаты в базе "
    "данных.",
    "Создайте команду /quote для отправки случайных цитат из заранее подготовленного списка.",
    "Напишите скрипт для отправки нового сгенерированного файла Excel со всеми данными пользователя (id, имя, "
    "имя пользователя и т. д.) пользователю.",
    "Напишите функцию /holidays для отправки ближайшего праздника из базы данных, пользователю.",
    "Создайте бота для игры в \"Угадай число\n с пользователем.",
    "Напишите бота для игры в крестики-нолики с пользователем.",
    "Напишите бота, который будет отправлять админу все входящие сообщения, а сообщения админа будут отправляться "
    "всем пользователям.",
    "Напишите команду /todo, после которой пользователь напишет задачу, и команду /todo_list для вывода всех "
    "задач.",
    "Напишите бота, который будет сохранять все сообщения в базе данных (PostgreSQL) в формате (id; сообщение).",
    "Напишите команду /mailing для отправки рассылки всем пользователям, которые пользовались ботом."
]

env = Env()
env.read_env(DIRECTORY_FILES / ".env")
DEV_MODE = env.bool("DEV_MODE")
PATHS = {
    'tesseract': env.str("TESSERACT_PATH"),
    'data': env.str("NDA_DATA_PATH")
}
SUPERVISOR_TG_USERNAME = f"@{env.str('SUPERVISOR_TG_USERNAME')}"
if DEV_MODE:
    TOKEN = env.str("DEV_MODE_TOKEN")
    exam_times = {
        "duration": datetime.timedelta(minutes=20), 
        "send_notification": datetime.timedelta(seconds=15)
    }
    con = mysql.connector.connect(
        host=    env.str("DEV_MODE_MYSQL_HOST"),
        user=    env.str("DEV_MODE_MYSQL_USER"),
        password=env.str("DEV_MODE_MYSQL_PASS"),
        database=env.str("DEV_MODE_MYSQL_DB_NAME")
    )
else:
    TOKEN = env.str("TOKEN")
    con = mysql.connector.connect(
        host=    env.str("MYSQL_HOST"),
        user=    env.str("MYSQL_USER"),
        password=env.str("MYSQL_PASS"),
        database=env.str("MYSQL_DB_NAME")
    )