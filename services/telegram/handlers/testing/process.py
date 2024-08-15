from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from data.variables import INTERN_INSTRUCTION, NDA_HELLO
from database.database import ORM
from database.models import User
from services.telegram.handlers.admin.notify import notify_admins, send_test_to_admins
from services.telegram.handlers.testing.time import is_time_over
from services.telegram.misc.callbacks import IsCompleteCallback
from services.telegram.misc.enums import TestStatus, Sender
from services.telegram.misc.keyboards import Keyboards

router = Router()


@router.message(F.video)
async def video(message: Message, user: User, orm: ORM):
    if user.test_status in [TestStatus.started, TestStatus.test_ending]:
        user = await orm.user_repo.find_user_by_user_id(user.user_id)
        if is_time_over(user.testing_at):
            video_format = message.video.mime_type.lower()
            if message.video.duration > 60:
                return await message.reply("Видео должно быть не более 60 секунд. 🕗")
            if message.video.file_size > 10485760:  # 10 МБ в байтах
                return await message.reply("Видео должно весить не более 10МБ. 💾")
            if not (video_format in ["video/mp4", "video/quicktime"]):
                return await message.reply("Формат видео недопустим. Только видео с расширением .mov или .mp4 ")
            await message.answer_video(video=message.video.file_id,
                                       reply_markup=Keyboards.is_test_complete(from_who=Sender.user,
                                                                               sender=user.user_id),
                                       caption=f"Тестирование @{message.from_user.username}"
                                               f"\n\nЗадание: \n"
                                               f"{user.task}\n\n")
    elif user.test_status is TestStatus.result_sent:
        await message.answer("Вы уже отправили тестирование! ❌")


# @router.message(F.text, SelectDatetime.wait_time)
# async def фыв(message: Message, state: FSMContext, user: User):
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

@router.callback_query(F.data == "on_task")
async def on_task(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=InlineKeyboardMarkup(inline_keyboard=[]))
    await notify_admins(callback.bot, f"@{callback.from_user.username} приступил к тестированию")
    await callback.answer("Вы начали тестирование ⏳")


@router.callback_query(IsCompleteCallback.filter(F.action == "isComplete"))
async def is_complete(callback: CallbackQuery, callback_data: IsCompleteCallback, orm: ORM):
    if callback_data.from_who == Sender.user:
        if callback_data.is_complete == 1:  # Отправить тестирование (видео)
            await send_test_to_admins(callback)
            await orm.user_repo.upsert_user(callback.from_user.id, test_status=TestStatus.result_sent)
        elif callback_data.is_complete == 0:  # Не отправлять тестирование (видео)
            await callback.message.delete()
    elif callback_data.from_who == Sender.admin:
        user = await orm.user_repo.find_user_by_user_id(callback_data.sender)
        if user.test_status is not TestStatus.failed:
            if callback_data.is_complete == 0:  # Админ ОТКЛОНИЛ тестирование
                await callback.message.answer(text=f"Вы отклонили тестирование @{user.username} ❌")
                await callback.bot.send_message(callback_data.sender, text=f"Тестирование отклонено ❌")

            elif callback_data.is_complete == 1:  # Админ ПРИНЯЛ тестирование
                await callback.message.answer(text=f"Вы приняли тестирование @{user.username} ✅")
                await callback.bot.send_message(callback_data.sender, text=INTERN_INSTRUCTION,
                                                parse_mode=ParseMode.HTML, reply_markup=Keyboards.invite_to_group())
                await orm.user_repo.upsert_user(callback_data.sender, test_status=TestStatus.completed)
            # await bot.send_document(callback_data.sender, FSInputFile(f'{PATHS["data"]}nda.docx'))
            # await bot.send_message(callback_data.sender, text='Ознакомьтесь с документом 🙂')
            # await bot.send_message(callback_data.sender,
            #                        text=NDA_HELLO,
            #                        reply_markup=GenerateKeyboard({'Приступить': 'data'}))
        else:
            await callback.message.answer(text=f"Тестирование @{user.username} уже оценено")
    await callback.answer()
