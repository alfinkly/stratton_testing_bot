from aiogram import Router, types, F
from aiogram.types import ContentType
from aiogram.filters.command import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackQuery
from aiogram.types import FSInputFile
from services.nda.module import *
from tg_config import PATHS

router = Router()


def GenerateKeyboard(values):
    buttons=[]
    for i in values:
        buttons.append(InlineKeyboardButton(text=i, callback_data=Callback(action=values[i]).pack()))
    keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])
    return keyboard


def GetCheckKeyboard():
    buttons=[]
    buttons.append([InlineKeyboardButton(text='Дата выдачи', callback_data=ChangeCallback(action='changeField', field='Дата выдачи').pack())])
    buttons.append([InlineKeyboardButton(text='ИИН', callback_data=ChangeCallback(action='changeField', field='ИИН').pack())])
    buttons.append([InlineKeyboardButton(text='Имя', callback_data=ChangeCallback(action='changeField', field='Имя').pack())])
    buttons.append([InlineKeyboardButton(text='Фамилия', callback_data=ChangeCallback(action='changeField', field='Фамилия').pack())])
    buttons.append([InlineKeyboardButton(text='Отчество', callback_data=ChangeCallback(action='changeField', field='Отчество').pack())])
    buttons.append([InlineKeyboardButton(text='Дата рождения', callback_data=ChangeCallback(action='changeField', field='Дата рождения').pack())])
    buttons.append([InlineKeyboardButton(text='Всё верно', callback_data=Callback(action='allright').pack())])
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


@router.message(Command("start"))
async def Start(msg: types.Message):
    await msg.answer(text='Начните отправку фотографии вашего удостверение личности', reply_markup=GenerateKeyboard({'Начать': 'data'}))


@router.callback_query(Callback.filter(F.action=='data'))
async def IMGHandler(cb: CallbackQuery, state: FSMContext):
    await state.update_data(face=True)
    await cb.message.edit_text(text='Отправьте фотографию лицевой стороны удостверения личности')


@router.message(F.content_type == ContentType.PHOTO)
async def process_photo(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('face') or data.get('back'):
        file_name = f"{PATHS['data']}{'faceside' if data.get('face') else 'backside'}{msg.from_user.id}.png"
        await msg.bot.download(msg.photo[-1], destination=file_name)
        fields = ReadPhoto(file_name, data.get('face'))
        await ReportToAdmin(msg, fields, msg.photo[-1].file_id)
        if fields:
            emptyFields = dict( (k,v) for k, v in fields.items() if v is None)
            notEmptyFields = dict( (k,v) for k, v in fields.items() if v is not None)
            if len(emptyFields)==0:
                await state.clear()
                if data.get('face'):
                    asd = fields|dict((k, v) for k,v in data.items() if k != 'face')
                    asd['fImageId'] = msg.photo[-1].file_id
                    asd['back'] = True
                    await state.update_data(asd)
                    await msg.answer(text='Отправьте обратную сторону удостверения личности')
                else:
                    asd = fields|dict((k, v) for k,v in data.items() if k != 'back')
                    asd['sImageId'] = msg.photo[-1].file_id
                    await state.update_data(asd)

                    await SendToAdmin(msg, 
                                      state, 
                                      GenerateKeyboard({'Изменить':'change', 'Всё верно':'allright'}))                 
            else:
                await state.clear()
                ndata = notEmptyFields|dict((k,v) for k,v in data.items() if v is not None)
                ndata = data|ndata
                ndata = emptyFields|ndata
                ndata['fImageId' if ndata.get('face') else 'sImageId'] = msg.photo[-1].file_id
                await state.update_data(ndata)
                await msg.answer(text=f'Не найдена информация: {", ".join([i for i in ndata if i not in ["face","back"] and ndata[i] is None])} \nПопробуйте отправить другое фото', 
                                 reply_markup=GenerateKeyboard({'Пропустить':'skip'}))
        else:
            await msg.answer(text='Произола ошибка \nПопробуйте отправить другое фото')
        

@router.callback_query(Callback.filter(F.action=='skip'))
async def MainHandler(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if data.get('face'):
        await state.clear()
        await cb.message.edit_text(text='Отправьте фотографию обратной стороны удостверения личности')
        data['back'] = True
        await state.update_data(dict((k, v) for k,v in data.items() if k != 'face'))
    elif data.get('back'):
        await state.update_data(dict((k, v) for k,v in data.items() if k != 'back'))
        await SendToAdmin(cb, 
                          state, 
                          GenerateKeyboard({'Изменить':'change', 'Всё верно':'allright'}))
    await cb.answer()


@router.callback_query(Callback.filter(F.action=='main'))
async def MainHandler(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await cb.message.answer(text='Начните отправку фотографии вашего удостверение личности', reply_markup=GenerateKeyboard({'Начать': 'data'}))
    

@router.callback_query(Callback.filter(F.action=='change'))
async def ChangeHandler(cb: CallbackQuery, state: FSMContext):
    text = cb.message.text
    for i in text.split('\n'):
        asd=i.split('-')
        if len(asd)==1:
            await state.update_data(username=list(filter(lambda x:x.count('@'), asd[0].split()))[0].split('@')[-1], text=text)
            break
    await cb.message.edit_text(cb.message.text, reply_markup=GetCheckKeyboard())


@router.callback_query(ChangeCallback.filter(F.action=='changeField'))
async def ChangeHandler(cb: CallbackQuery, callback_data: ChangeCallback, state: FSMContext):
    await state.update_data(change=callback_data.field)
    await cb.message.edit_text(cb.message.text)
    await cb.message.answer(f'Напишите данные для поля-{callback_data.field}')


@router.callback_query(Callback.filter(F.action=='allright'))
async def OKHandler(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ndata={}
    for i in data['text'].split('\n'):
        asd=i.split('-')
        if len(asd)!=1:
            ndata[asd[0]]=asd[1]
    file_name = f"{PATHS['data']}docx{data['username']}.docx"
    GetDocx(file_name, ndata)

    await state.clear()
    document = FSInputFile(file_name)
    await cb.bot.send_document(cb.from_user.id, document)


@router.message()
async def echo_message(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    if data.get('change'):
        text = data['text'].split('\n')
        for i in range(len(text)):
            asd = text[i].split('-')
            if asd[0]==data['change']:
                text[i] = f"{asd[0]}-{msg.text}"
                break
        text='\n'.join(text)
        await state.update_data(text=text)
    
        media = []
        photoPaths = [data['fImageId'], data['sImageId']]
        for path in photoPaths:
            media.append(InputMediaPhoto(media=path))
        await msg.answer_media_group(media=media)
        await msg.answer(text, reply_markup=GetCheckKeyboard())
    else:
        await msg.answer("baaaka")
