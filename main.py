from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from aiogram.types import InputFile
from aiogram.utils.exceptions import ChatNotFound
import asyncio
import aiohttp

import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from moviepy.editor import VideoFileClip

import os

import sqlite3

import buttons
import messages


logging.basicConfig(level=logging.INFO)


API_TOKEN = 'token'

storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)


scheduler = AsyncIOScheduler()
scheduler.start()

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE
    )
''')


cursor.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT,
        media TEXT,
        media_type TEXT,
        button_type TEXT,
        button_text TEXT,
        button_url TEXT,
        callback_text TEXT,
        repeat_time INTEGER
    )
''')

conn.commit()
conn.close()



async def send_video_note_from_file(chat_id, video_path):
 clip = VideoFileClip(video_path)
 compressed_path = 'compressed_video.mp4'
 clip.write_videofile(compressed_path, codec='libx264', bitrate='500k')

 with open(compressed_path, 'rb') as f:
    compressed_video_data = f.read()

 await bot.send_video_note(chat_id=chat_id, video_note=compressed_video_data)
 os.remove(compressed_path) 


@dp.message_handler(commands={'start', 'help'})
async def start_bot(message: types.Message):
 user_id = message.from_user.id

 conn = sqlite3.connect('bot.db')
 cursor = conn.cursor()
 cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
 conn.commit()
 conn.close()

 video_path = 'videos/video.mp4' 
 await send_video_note_from_file(user_id, video_path) 


 await message.answer(messages.one, reply_markup=buttons.start, parse_mode=ParseMode.MARKDOWN)
 await asyncio.sleep(3)

 await message.answer(messages.two, parse_mode=ParseMode.MARKDOWN)
 await asyncio.sleep(5)

 await message.answer(messages.tree)
 await asyncio.sleep(1)

 video_path = 'videos/video2.mp4'
 await send_video_note_from_file(user_id, video_path)

 await message.answer('ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ👇🏻', reply_markup=buttons.register)
 await message.answer(messages.four, reply_markup=buttons.msg_reg, parse_mode=ParseMode.MARKDOWN)
 await asyncio.sleep(6)

 await message.answer(messages.five, reply_markup=buttons.register, parse_mode=ParseMode.MARKDOWN)



@dp.callback_query_handler(text="OpenYrok")
async def msg_r(call: types.CallbackQuery):
 await call.answer('Уроки открыты') 
 await call.message.answer(messages.OPYR, reply_markup=buttons.register, parse_mode=ParseMode.MARKDOWN)


##########################
##########################

admin = 6306428168 

class NewMessage(StatesGroup):
    text = State()
    media = State()
    button_type = State()
    button_text = State()
    button_url = State()
    repeat_time = State()
    callback_text = State()  

class EditMessage(StatesGroup):
    select_message = State()
    text = State()
    media = State()
    button_type = State()
    button_text = State()
    button_url = State()
    callback_text = State()
    repeat_time = State()


@dp.message_handler(commands=['admin'])
async def adminkaa(message: types.Message):
    if message.from_user.id == admin:
        await message.answer('Приветствую в панели администратора!\n\nВыберите действие ниже👇🏻', reply_markup=buttons.adminka_btn)
    else:
        await message.answer('Отказано')

@dp.callback_query_handler(text="panel")
async def panel(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer('ПАНЕЛЬ АДМИНИСТРАТОРА:', reply_markup=buttons.panel_adm)



@dp.callback_query_handler(text="new_msg")
async def new_msg(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Введите текст нового сообщения:", reply_markup=buttons.skip_button)
    await NewMessage.text.set()

@dp.message_handler(state=NewMessage.text)
async def new_msg_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Прикрепите фото или видео (если надо):", reply_markup=buttons.skip_button)
    await NewMessage.media.set()

@dp.message_handler(state=NewMessage.media, content_types=['photo', 'video'])
async def new_msg_media(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.photo:
            data['media'] = message.photo[-1].file_id
            data['media_type'] = 'photo'
        elif message.video:
            file_id = message.video.file_id
            compressed_file_id = await compress_video(file_id)
            data['media'] = compressed_file_id
            data['media_type'] = 'video'
    await message.answer("Выберите тип кнопки: URL, текст или без кнопки.", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton("URL", callback_data="button_url"),
        InlineKeyboardButton("Текст", callback_data="button_text"),
        InlineKeyboardButton("Без кнопки", callback_data="no_button")
    ))
    await NewMessage.button_type.set()

@dp.callback_query_handler(state=NewMessage.media, text="skip")
async def skip_new_media(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['media'] = None
        data['media_type'] = None
    await call.message.answer("Выберите тип кнопки: URL, текст или без кнопки.", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton("URL", callback_data="button_url"),
        InlineKeyboardButton("Текст", callback_data="button_text"),
        InlineKeyboardButton("Без кнопки", callback_data="no_button")
    ))
    await NewMessage.button_type.set()

@dp.callback_query_handler(state=NewMessage.button_type)
async def select_new_button_type(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_type'] = call.data
    await call.message.answer("Введите текст кнопки:", reply_markup=buttons.skip_button)
    await NewMessage.button_text.set()

@dp.message_handler(state=NewMessage.button_text)
async def new_msg_button_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_text'] = message.text
    button_type = data.get('button_type')
    if button_type == 'button_url':
        await message.answer("Введите URL для кнопки:", reply_markup=buttons.skip_button)
        await NewMessage.button_url.set()
    elif button_type == 'button_text':
        await message.answer("Введите текст, который будет отправлен при нажатии на кнопку:", reply_markup=buttons.skip_button)
        await NewMessage.callback_text.set()  
    else:
        await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
        await NewMessage.repeat_time.set()

@dp.message_handler(state=NewMessage.button_url)
async def new_msg_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
    await NewMessage.repeat_time.set()

@dp.callback_query_handler(state=NewMessage.button_url, text="skip")
async def skip_new_button_url(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_url'] = None
    await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
    await NewMessage.repeat_time.set()

@dp.message_handler(state=NewMessage.callback_text)
async def new_msg_callback_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['callback_text'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
    await NewMessage.repeat_time.set()

@dp.message_handler(state=NewMessage.repeat_time)
async def new_msg_repeat_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['repeat_time'] = int(message.text) if message.text.isdigit() else None
        text = data.get('text')
        media = data.get('media')
        media_type = data.get('media_type')
        button_type = data.get('button_type')
        button_text = data.get('button_text')
        button_url = data.get('button_url')
        callback_text = data.get('callback_text')
        repeat_time = data.get('repeat_time')

    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time))
    conn.commit()
    conn.close()

    if repeat_time:
        scheduler.add_job(
            send_message,
            IntervalTrigger(minutes=repeat_time),
            args=[text, media, media_type, button_type, button_text, button_url, callback_text]
        )

    await message.answer("Новое сообщение создано успешно!")
    await state.finish()

@dp.callback_query_handler(state=NewMessage.repeat_time, text="skip")
async def skip_new_repeat_time(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        text = data.get('text')
        media = data.get('media')
        media_type = data.get('media_type')
        button_type = data.get('button_type')
        button_text = data.get('button_text')
        button_url = data.get('button_url')
        callback_text = data.get('callback_text')
        repeat_time = None

    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time))
    conn.commit()
    conn.close()

    await call.message.answer("Новое сообщение создано успешно!")
    await state.finish()

async def send_all_messages():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()

    for user in users:
        for message in messages:
            user_id = user[0]
            text = message[1]
            media = message[2]
            media_type = message[3]
            button_type = message[4]
            button_text = message[5]
            button_url = message[6]
            callback_text = message[7]
            repeat_time = message[8]

            if button_type == 'button_text':
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=button_text, callback_data=f"callback_{callback_text}")
                )
            elif button_type == 'button_url':
                keyboard = InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=button_text, url=button_url)
                )
            else:
                keyboard = None

            if media_type == 'photo':
                await bot.send_photo(chat_id=user_id, photo=media, caption=text, reply_markup=keyboard)
            elif media_type == 'video':
                await bot.send_video(chat_id=user_id, video=media, caption=text, reply_markup=keyboard)
            else:
                await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard)

    conn.close()

async def send_message(text, media, media_type, button_type, button_text, button_url, callback_text):
    chat_id = admin
    if button_type == 'button_text':
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text=button_text, callback_data=f"callback_{callback_text}")
        )
    elif button_type == 'button_url':
        keyboard = InlineKeyboardMarkup().add(
            InlineKeyboardButton(text=button_text, url=button_url)
        )
    else:
        keyboard = None

    if media_type == 'photo':
        await bot.send_photo(chat_id=chat_id, photo=media, caption=text, reply_markup=keyboard)
    elif media_type == 'video':
        await bot.send_video(chat_id=chat_id, video=media, caption=text, reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)

def reschedule_messages():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT text, photo, button_type, button_text, button_url, callback_text, repeat_time FROM messages WHERE repeat_time IS NOT NULL')
    messages = cursor.fetchall()
    conn.close()

    for msg in messages:
        text, photo, button_type, button_text, button_url, callback_text, repeat_time = msg
        scheduler.add_job(
            send_message,
            IntervalTrigger(minutes=repeat_time),
            args=[text, photo, button_type, button_text, button_url, callback_text]
        )


@dp.callback_query_handler(lambda call: call.data.startswith('callback_'))
async def handle_button_callback(call: types.CallbackQuery):
    callback_text = call.data.split('callback_')[1]
    await call.message.answer(f"{callback_text}")

def get_message_list():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, text FROM messages")
    messages = cursor.fetchall()
    conn.close()
    return messages


@dp.callback_query_handler(text="edit_msg")
async def edit_msg(call: types.CallbackQuery):
    await call.answer()
    messages = get_message_list()
    
    if messages:
        keyboard = InlineKeyboardMarkup()
        for msg_id, msg_text in messages:
            button_text = f"{msg_id}: {msg_text[:30]}"  
            keyboard.add(InlineKeyboardButton(button_text, callback_data=f"select_msg_{msg_id}"))
        await call.message.answer("Выберите сообщение для редактирования:", reply_markup=keyboard)
    else:
        await call.message.answer("Сообщения для редактирования не найдены.")
    
    await EditMessage.select_message.set()

@dp.callback_query_handler(lambda c: c.data.startswith('select_msg_'), state=EditMessage.select_message)
async def select_message_id(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    message_id = int(call.data.split('_')[2])
    async with state.proxy() as data:
        data['message_id'] = message_id
    await call.message.answer("Введите новый текст сообщения:", reply_markup=buttons.skip_button)
    await EditMessage.text.set()

@dp.callback_query_handler(state=EditMessage.select_message, text="skip")
async def skip_select_message(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите новый текст сообщения:", reply_markup=buttons.skip_button)
    await EditMessage.text.set()

@dp.message_handler(state=EditMessage.text)
async def edit_msg_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Прикрепите новое фото или видео (если надо):", reply_markup=buttons.skip_button)
    await EditMessage.media.set()

@dp.callback_query_handler(state=EditMessage.text, text="skip")
async def skip_edit_text(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['text'] = None
    await call.message.answer("Прикрепите новое фото или видео (если надо):", reply_markup=buttons.skip_button)
    await EditMessage.media.set()

@dp.message_handler(state=EditMessage.media, content_types=['photo', 'video'])
async def edit_msg_media(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.photo:
            data['media'] = message.photo[-1].file_id
            data['media_type'] = 'photo'
        elif message.video:
            file_id = message.video.file_id
            compressed_file_id = await compress_video(file_id)
            data['media'] = compressed_file_id
            data['media_type'] = 'video'
    await message.answer("Выберите тип кнопки: URL, текст или без кнопки.", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton("URL", callback_data="button_url"),
        InlineKeyboardButton("Текст", callback_data="button_text"),
        InlineKeyboardButton("Без кнопки", callback_data="no_button")
    ))
    await EditMessage.button_type.set()

@dp.callback_query_handler(state=EditMessage.media, text="skip")
async def skip_edit_media(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['media'] = None
        data['media_type'] = None
    await call.message.answer("Выберите тип кнопки: URL, текст или без кнопки.", reply_markup=InlineKeyboardMarkup().add(
        InlineKeyboardButton("URL", callback_data="button_url"),
        InlineKeyboardButton("Текст", callback_data="button_text"),
        InlineKeyboardButton("Без кнопки", callback_data="no_button")
    ))
    await EditMessage.button_type.set()

@dp.callback_query_handler(state=EditMessage.button_type)
async def select_edit_button_type(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_type'] = call.data
    await call.message.answer("Введите текст кнопки:", reply_markup=buttons.skip_button)
    await EditMessage.button_text.set()

@dp.message_handler(state=EditMessage.button_text)
async def edit_msg_button_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_text'] = message.text
    button_type = data.get('button_type')
    if button_type == 'button_url':
        await message.answer("Введите URL для кнопки:", reply_markup=buttons.skip_button)
        await EditMessage.button_url.set()
    elif button_type == 'button_text':
        await message.answer("Введите текст, который будет отправлен при нажатии на кнопку:", reply_markup=buttons.skip_button)
        await EditMessage.callback_text.set()
    else:
        await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
        await EditMessage.repeat_time.set()

@dp.callback_query_handler(state=EditMessage.button_text, text="skip")
async def skip_edit_button_text(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_text'] = None
    button_type = data.get('button_type')
    if button_type == 'button_url':
        await call.message.answer("Введите URL для кнопки:", reply_markup=buttons.skip_button)
        await EditMessage.button_url.set()
    elif button_type == 'button_text':
        await call.message.answer("Введите текст, который будет отправлен при нажатии на кнопку:", reply_markup=buttons.skip_button)
        await EditMessage.callback_text.set()
    else:
        await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
        await EditMessage.repeat_time.set()

@dp.message_handler(state=EditMessage.button_url)
async def edit_msg_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
    await EditMessage.repeat_time.set()

@dp.callback_query_handler(state=EditMessage.button_url, text="skip")
async def skip_edit_button_url(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_url'] = None
    await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
    await EditMessage.repeat_time.set()

@dp.message_handler(state=EditMessage.callback_text)
async def edit_msg_callback_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['callback_text'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
    await EditMessage.repeat_time.set()

@dp.callback_query_handler(state=EditMessage.callback_text, text="skip")
async def skip_edit_callback_text(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['callback_text'] = None
    await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=buttons.skip_button)
    await EditMessage.repeat_time.set()

@dp.message_handler(state=EditMessage.repeat_time)
async def edit_msg_repeat_time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['repeat_time'] = int(message.text) if message.text.isdigit() else None
        message_id = data.get('message_id')
        text = data.get('text')
        media = data.get('media')
        media_type = data.get('media_type')
        button_type = data.get('button_type')
        button_text = data.get('button_text')
        button_url = data.get('button_url')
        callback_text = data.get('callback_text')
        repeat_time = data.get('repeat_time')

    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE messages
        SET text=?, media=?, media_type=?, button_type=?, button_text=?, button_url=?, callback_text=?, repeat_time=?
        WHERE id=?
    ''', (text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time, message_id))
    conn.commit()
    conn.close()

    if repeat_time:
        scheduler.add_job(
            send_message,
            IntervalTrigger(minutes=repeat_time),
            args=[text, media, media_type, button_type, button_text, button_url, callback_text]
        )

    await message.answer("Сообщение успешно отредактировано!")
    await state.finish()

@dp.callback_query_handler(state=EditMessage.repeat_time, text="skip")
async def skip_edit_repeat_time(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        message_id = data.get('message_id')
        text = data.get('text')
        media = data.get('media')
        media_type = data.get('media_type')
        button_type = data.get('button_type')
        button_text = data.get('button_text')
        button_url = data.get('button_url')
        callback_text = data.get('callback_text')
        repeat_time = None

    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE messages
        SET text=?, media=?, media_type=?, button_type=?, button_text=?, button_url=?, callback_text=?, repeat_time=?
        WHERE id=?
    ''', (text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time, message_id))
    conn.commit()
    conn.close()

    await call.message.answer("Сообщение успешно отредактировано!")
    await state.finish()


class Broadcast(StatesGroup):
    text = State()
    media = State()


@dp.callback_query_handler(text="rss")
async def rss_broadcast(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Введите текст сообщения для рассылки:", reply_markup=buttons.skip_button)
    await Broadcast.text.set()


@dp.message_handler(state=Broadcast.text)
async def broadcast_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Прикрепите фото или видео (если есть):", reply_markup=buttons.skip_button)
    await Broadcast.media.set()


@dp.message_handler(state=Broadcast.media, content_types=['photo', 'video'])
async def broadcast_media(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if message.photo:
            data['media'] = message.photo[-1].file_id
            data['media_type'] = 'photo'
        elif message.video:
            file_id = message.video.file_id
            compressed_file_id = await compress_video(file_id)
            data['media'] = compressed_file_id
            data['media_type'] = 'video'
        text = data.get('text')
        media = data.get('media')
        media_type = data.get('media_type')


    await send_broadcast(text, media, media_type)
    await message.answer("Рассылка завершена.")
    await state.finish()


@dp.callback_query_handler(state=Broadcast.media, text="skip")
async def skip_broadcast_media(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        text = data.get('text')
        data['media'] = None
        data['media_type'] = None


    await send_broadcast(text, None, None)
    await call.message.answer("Рассылка завершена.")
    await state.finish()


async def send_broadcast(text, media, media_type):
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users')
    users = cursor.fetchall()
    conn.close()

    for user in users:
        user_id = user[0]
        try:
            if media:
                if media_type == 'photo':
                    await bot.send_photo(chat_id=user_id, photo=media, caption=text)
                elif media_type == 'video':
                    await bot.send_video_note(chat_id=user_id, video_note=media)
                    if text:
                        await bot.send_message(chat_id=user_id, text=text)
            else:
                await bot.send_message(chat_id=user_id, text=text)
        except ChatNotFound:
            logging.warning(f"Chat not found for user_id: {user_id}")

async def compress_video(file_id):
    file_info = await bot.get_file(file_id)
    file_path = file_info.file_path
    download_url = f"https://api.telegram.org/file/bot{API_TOKEN}/{file_path}"

    async with aiohttp.ClientSession() as session:
        async with session.get(download_url) as response:
            if response.status == 200:
                video_data = await response.read()
                with open('downloaded_video.mp4', 'wb') as f:
                    f.write(video_data)

                clip = VideoFileClip('downloaded_video.mp4')
                compressed_path = 'compressed_video.mp4'
                clip.write_videofile(compressed_path, codec='libx264', bitrate='500k')

                with open(compressed_path, 'rb') as f:
                    compressed_video_data = f.read()

                video_note = await bot.send_video_note(chat_id=admin, video_note=compressed_video_data)
                os.remove('downloaded_video.mp4')
                os.remove('compressed_video.mp4')

                return video_note.video_note.file_id


def main():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    ''')
    conn.commit()
    conn.close()


def reschedule_messages():
    conn = sqlite3.connect('bot.db')
    cursor = conn.cursor()
    cursor.execute('SELECT text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time FROM messages WHERE repeat_time IS NOT NULL')
    messages = cursor.fetchall()
    conn.close()

    for msg in messages:
        text, media, media_type, button_type, button_text, button_url, callback_text, repeat_time = msg
        scheduler.add_job(
            send_message,
            IntervalTrigger(minutes=repeat_time),
            args=[text, media, media_type, button_type, button_text, button_url, callback_text]
        )



if __name__ == '__main__':
    reschedule_messages() 
    executor.start_polling(dp, skip_updates=True)