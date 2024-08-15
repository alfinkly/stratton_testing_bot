import datetime
import mysql.connector

TOKEN = "6788352837:AAEDFVjpaoi-_h5H3gRwXBd3-SPKM-azDs0"

# checker_id = 992654384   # Deaspecty
checker_ids = [564023521, 992654384]

PATHS = {
    'tesseract': r"D:\progs\Tesseract-OCR\tesseract.exe",
    'data': './nda/data/'
}

DEV_MODE = True

con = mysql.connector.connect(
    host="localhost",
    user="root",
    password="MyFuckingSQL%5003",
    database="stratton_bot_data"
)




