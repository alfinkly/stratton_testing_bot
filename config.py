import datetime
import mysql.connector

TOKEN = "6788352837:AAHKakh-Kun4k-gzrFvheQrx0zKKRxrPnis"

months = {1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь", 7: "Июль",
          8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"}

# checker_id = 992654384   # Deaspecty
checker_ids = [564023521, 992654384]

exam_times = {
    "duration": datetime.timedelta(hours=4),
    "send_notification": datetime.timedelta(hours=3, minutes=50)
}

DEV_MODE = True

task = "\nЗадания по Python." + \
       "\nЗадание 1." + \
       "\nСоздание функции генерации excel файла при помощи библиотеки openpyxl." + \
       "\nТребуется создание нового excel файла с автоматической генерацией следующих данных:" + \
       "\n1. Страницы «TDSheet» с 3 колонками: Имя, текущая. дата и текущее время. Имя должно быть сгенерировано " \
       "случайным образом. Можно из массива из 10 значении или же сторонних библиотек." + \
       "\n2. Название файла должно быть ИМЯ + тек дата + случайное трехзначное число+ .xlsx." + \
       "\n3. Сохранено в папке …\мой документы\skcu\\" + \
       "\nhttps://openpyxl.readthedocs.io/en/stable/tutorial.html" + \
       "\n" + \
       "\nЗадание 2." + \
       "\nИспользуя import smtplib, отправить сгенерированный в первом задании Excel файл (если не получилось, " \
       "то пустой файл) адресату Х." + \
       "\nhttps://www.tutorialspoint.com/python/python_sending_email.htm" + \
       "\nЗадание 3." + \
       "\nИспользуя библиотеку pyTelegramBot (import telebot) написать простого бота, который будет отвечать на " \
       "отправленный текст «Strattonbot+ отправленный текст»." + \
       "\nhttps://groosha.gitbook.io/telegram-bot-lessons/chapter1" + \
       "\nЗадание 4." + \
       "\nЗаписывать любое обращение к боту в базу данных. База данных может быть любой (желательно Microsoft Access)." + \
       "\nВ 2 колонки: Текст сообщения и дата отправки." + \
       "\n" + \
       "\nРезультат выслать ссылкой и можно записать видео работы на 30 секунд"

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MyFuckingSQL%5003",
    database="stratton_bot_data"
)

if DEV_MODE:
    TOKEN = "6788352837:AAEDFVjpaoi-_h5H3gRwXBd3-SPKM-azDs0"
    exam_times = {"duration": datetime.timedelta(minutes=20), "send_notification": datetime.timedelta(seconds=15)}
    checker_ids = [992654384]
    con = mysql.connector.connect(
        host="localhost",
        user="root",
        password="MyFuckingSQL%5003",
        database="stratton_dev"
    )
