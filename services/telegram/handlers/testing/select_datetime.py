import datetime

import pytz
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from services.telegram.misc.keyboards import Keyboards
from database.models import User
from services.telegram.misc.callbacks import DateCallback
from services.telegram.handlers.states import SelectDatetime

router = Router()


@router.callback_query(DateCallback.filter(F.action == "set_date"), SelectDatetime.wait_date)
async def set_date(callback: CallbackQuery, callback_data: DateCallback, state: FSMContext):
    date = datetime.datetime(year=callback_data.year, month=callback_data.month, day=callback_data.day)
    await state.update_data(datetime=date)
    await callback.message.answer(f"Выберите удобное время  🕗"
                                  f"\nИли напишите своё время", reply_markup=Keyboards.get_times(callback))
    await callback.answer()
    await state.set_state(SelectDatetime.wait_time)


@router.callback_query(DateCallback.filter(F.action == "month"))
async def month(callback: CallbackQuery, callback_data: DateCallback):
    await callback.message.edit_reply_markup(reply_markup=Keyboards.get_calendar(year=callback_data.year,
                                                                                 month=callback_data.month,
                                                                                 message=callback))
    await callback.answer()


@router.callback_query(F.data == "back_to_date")
async def month(callback: CallbackQuery):
    today = datetime.datetime.now()
    await callback.message.edit_text(
        text=f"Выберите удобную дату  📅",
        reply_markup=Keyboards.get_calendar(today.year, today.month)
    )
    await callback.answer()


@router.message(F.video)
async def video(message: Message):
    if methods.get_test_status(message.from_user.id, message.from_user.username) in [2, 3]:
        cursor = con.cursor(buffered=True)
        cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {message.from_user.id}")
        row_db = cursor.fetchall()
        date_to = datetime.datetime.strptime(row_db[0][0].split(" ")[0] + " " + row_db[0][1], '%Y-%m-%d %H:%M')
        date_to = pytz.timezone('Asia/Almaty').localize(date_to)
        now = datetime.datetime.now(tz=pytz.timezone('Asia/Almaty'))
        video_format = message.video.mime_type.lower()
        if message.video.duration > 60:
            return await message.reply("Извините, видео должно быть не более 60 секунд. 🕗")
        if message.video.file_size > 10485760:  # 10 МБ в байтах
            return await message.reply("Извините, видео должно весить не более 10МБ. 💾")
        if not (video_format in ["video/mp4", "video/quicktime"]):
            return await message.reply(
                "Извините, формат видео недопустим. Только видео с расширением .mov или .mp4 ")
        if date_to < now < date_to + config.exam_times["duration"]:
            cursor.execute(f"SELECT tasks FROM users_data WHERE user_id={message.from_user.id}")
            tasks_text = cursor.fetchone()
            await message.answer_video(video=message.video.file_id,
                                       reply_markup=keyboards.is_test_complete(from_who=0,
                                                                               sender=message.from_user.id),
                                       caption=f"Тестирование @{message.from_user.username}"
                                               f"\n\nЗадание: \n"
                                               f"{tasks_text[0]}\n\n"
                                       )
            con.commit()
            cursor.close()
    elif methods.get_test_status(message.from_user.id, message.from_user.username) in [5, 6]:
        await message.answer("Вы отправили видео не в срок! ⌛️")
    elif methods.get_test_status(message.from_user.id, message.from_user.username) == 4:
        await message.answer("Вы уже отправили тестирование! ❌")


@router.message(F.text, SelectDatetime.wait_time)
async def set_time(message: Message, state: FSMContext, user: User):
    # data = await state.get_data()
    # if data.get('change'):
    #     text = data['text'].split('\n')
    #     for i in range(len(text)):
    #         asd = text[i].split('-')
    #         if asd[0] == data['change']:
    #             text[i] = f"{asd[0]}-{message.text}"
    #             break
    #     text = '\n'.join(text)
    #     await state.update_data(text=text)
    #
    #     media = []
    #     photoPaths = [data['fImageId'], data['sImageId']]
    #     for path in photoPaths:
    #         media.append(InputMediaPhoto(media=path))
    #     await message.answer_media_group(media=media)
    #     await message.answer(text, reply_markup=GetCheckKeyboard())

    # dokuzunosaiduowari
    is_time = False
    for time_format in ["%H:%M", "%H %M", "%H-%M", "%H.%M", "%H_%M"]:
        try:
            time = datetime.datetime.strptime(message.text, time_format)
            is_time = True
            await methods.appoint_test(message, time)
            break
        except ValueError:
            pass
    if not is_time:
        await message.answer("Это не похоже на время")

    # elif methods.get_test_status(message.from_user.id, message.from_user.username) in [2, 3]:
    #     if (message.text.startswith("@") and message.text.endswith("bot") and not (" " in message.text)) or \
    #             (message.text.startswith("https://t.me/") and message.text.endswith("bot") and
    #              not (" " in message.text)):
    #         cursor.execute(f"SELECT date, time FROM users_data WHERE user_id = {message.from_user.id}")
    #         row_db = cursor.fetchall()
    #         date_to = datetime.datetime.strptime(row_db[0][0].split(" ")[0] + " " + row_db[0][1], '%Y-%m-%d %H:%M')
    #         now = datetime.datetime.now()
    #         if date_to < now < date_to + config.exam_times["duration"]:  # or config.DEV_MODE:
    #             await message.send_copy(message.from_user.id,
    #                                     reply_markup=keyboards.keyboard_is_exam_complete(from_who=0,
    #                                                                                      sender=message.from_user.id))
    #     else:
    #         await message.reply("Это не похоже на ссылку на бота.")
    # elif methods.get_test_status(message.from_user.id, message.from_user.username) == 4:
    #     await message.answer("Вы уже отправили тестирование! ❌")
