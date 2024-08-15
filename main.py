import datetime

import pytz
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.enums import ParseMode
import keyboards
import routers
from tg_config import con
from factories import IsCompleteCallbackFactory, TimeCallbackFactory
from methods import send_testing_message_callback

from services.telegram.handlers.nda.nda import GenerateKeyboard
from aiogram.types import FSInputFile
from tg_config import PATHS




# cursor = con.cursor(buffered=True)


@dp.callback_query(IsCompleteCallbackFactory.filter(F.action == "isComplete"))
async def times(callback: types.CallbackQuery, callback_data: IsCompleteCallbackFactory):
    con.reconnect()
    if callback_data.from_who == 0:
        if callback_data.is_complete == 0:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
        elif callback_data.is_complete == 1:
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await send_testing_message_callback(callback, to_complete=True)
            for c_id in config.checker_ids:
                await callback.message.send_copy(c_id, reply_markup=keyboards.
                                                 keyboard_is_exam_complete(from_who=1, sender=callback.from_user.id))
            cursor = con.cursor(buffered=True)
            cursor.execute("UPDATE users_data SET test_status=%s WHERE user_id=%s", (4, callback.from_user.id))
            con.commit()
            cursor.close()
    elif callback_data.from_who == 1:
        if callback_data.is_complete == 0:
            await callback.message.answer(text=f"Вы отклонили тестирование @{callback.from_user.username} ❌")
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await bot.send_message(callback_data.sender, text=f"Тестирование отклонено❌",
                                   reply_markup=keyboards.main_actions(callback.from_user.id,
                                                                       callback.from_user.username))
        elif callback_data.is_complete == 1:
            await callback.message.answer(text=f"Вы приняли тестирование @{callback.from_user.username} ✅")
            await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
            await bot.send_message(callback_data.sender, text=f"""Тестирование принято
<a href='https://t.me/+9FMpM6obgMQ3MmYy'>Приглашение в группу стажеров</a>""",
                                   reply_markup=keyboards.main_actions(callback.from_user.id,
                                                                       callback.from_user.username),
                                   parse_mode=ParseMode.HTML)
            await bot.send_message(callback_data.sender, text="""Приветствую в группе Stratton Python Interns
Для начала представьтесь, написав Имя, Город и немного про свои скиллы и увлечения!
С вами в группе наставники:
Адил @crepecafe - PM команды разработки
Михаил @M1khal1 - разработчик команды Python

Группа является комьюнити единомышленников, где каждый может общаться по теме разработки, просить у участников помощи в  тестировании ботов, советов.

⚠️Правила:
❗️1. Пишем на Aiogram 3;
❗️2. После выполнения задания протестировать задание на корректность! И только после всех проверок прислать ссылку на ЗАПУЩЕННОГО бота для проверки функционала;
❗️3. Соблюдать дедлайны и отвечать на сообщения наставников. После получения задачи пишите в ответ "принято" ✅!
❗️4. Флуд запрещен! ⛔️
Вот так сообщения не писать! ❌👇🏿
или через
консоль разработчика
Win + R
туда cmd
и путь к своему файлу
к мейну
или к питону
напрямую
❗️5. Пользоваться этим <a href="https://docs.google.com/document/d/1JDWAFRgLbI76j60YnF0-PhxmZPe_WBdQfq6xaBlC_kg/edit">руководством</a> при написании ботов!
6. Прочитать все закрепленные сообщения

Задание назначается после вступления в группу! Напишите, легче или сложнее назначить первую задачу!

После выполнения и демонстрации заданий на локалке cтажеру на усмотрение наставников может быть выдан сервер для размещения ботов! Мы сами предложим!

Всем успешной стажировки и скорейшего перехода в продуктовую (боевую) команду!""", parse_mode=ParseMode.HTML)
            await send_testing_message_callback(callback, to_complete=True)
            
            # dokuzunosaidustaato

            await bot.send_document(callback_data.sender, FSInputFile(f'{PATHS["data"]}nda.docx'))
            await bot.send_message(callback_data.sender, text='Ознакомьтесь с документом 🙂')
            await bot.send_message(callback_data.sender, text='Теперь вам надо отправить свои данные для подписания NDA, вам нужно будет сфотографировать свое удостоверение личности 🙂 \nЕсли у вас не получается отсканировать данные, пропустите этап нажав на кнопку "пропустить" 🙂',
                                   reply_markup=GenerateKeyboard({'Приступить': 'data'}))
    await callback.answer()





@dp.callback_query(F.data == "on_task")
async def month(callback: types.CallbackQuery):
    con.reconnect()
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
    for c_id in config.checker_ids:
        await bot.send_message(chat_id=c_id, text=f"@{callback.from_user.username} приступил к тестированию")
    await callback.message.edit_text(text="Вы начали тестирование ✅")
    today = datetime.datetime.now()
    cursor = con.cursor()
    cursor.execute("UPDATE users_data SET on_task=%s WHERE user_id=%s", (today, callback.from_user.id))
    con.commit()
    cursor.close()
    await callback.answer()





