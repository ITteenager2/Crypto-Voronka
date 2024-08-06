##################################
##################################
# DEVELOPER: FSURE09 (TG)
##################################
# ИМПОРТЫ
##################################
##################################

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, ParseMode
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import sqlite3
import logging
from apscheduler.triggers.interval import IntervalTrigger
from aiogram.types import InputFile
from aiogram.utils.executor import start_polling
import moviepy
import aiohttp
from aiogram.utils.exceptions import ChatNotFound
from moviepy.editor import VideoFileClip
import os
# логирование
logging.basicConfig(level=logging.INFO)

# api token вашего бота
API_TOKEN = 'сюды токен тыкайте'

print('start bot by evgeshka @fsure09')
#токен и инициализация бота
storage = MemoryStorage()
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=storage)

# инициализация шедлера для отправки по кд сообщений
scheduler = AsyncIOScheduler()
scheduler.start()

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

# Создание таблицы пользователей
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL UNIQUE
    )
''')

# Создание таблицы сообщений с новой схемой
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

#inline buttons

# ПЕРВЫЕ 2 УРОКА кнопка
start = InlineKeyboardMarkup()
start.add(InlineKeyboardButton('ОТКРЫТЬ УРОКИ', callback_data='OpenYrok'))

# РЕГИСТРАЦИЯ кнопка
register = InlineKeyboardMarkup()
register.add(InlineKeyboardButton('ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ', url='https://rp-hub.ru/'))

# ЗАПИСАТЬСЯ КНОПКА С ТЕКСТОМ №2

msg_reg = InlineKeyboardMarkup()
msg_reg.add(InlineKeyboardButton('ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ', callback_data='msg_r'))

# смена статуса видео в кружочек (функция)
async def send_video_note_from_file(chat_id, video_path):
 clip = VideoFileClip(video_path)
 compressed_path = 'compressed_video.mp4'
 clip.write_videofile(compressed_path, codec='libx264', bitrate='500k')

 with open(compressed_path, 'rb') as f:
    compressed_video_data = f.read()

 await bot.send_video_note(chat_id=chat_id, video_note=compressed_video_data)
 os.remove(compressed_path) # удаляем отправленный файл из папки дабы не засорять его

# обработка команды /start
@dp.message_handler(commands={'start', 'help'})
async def start_bot(message: types.Message):
 user_id = message.from_user.id
 # добавляем человека в базу
 conn = sqlite3.connect('bot.db')
 cursor = conn.cursor()
 cursor.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
 conn.commit()
 conn.close()
 # даём путь видео и отсылаем его
 video_path = 'videos/video.mp4' # если надо поменять видео - меняете название своего файла mp4 на video либо меняете тут вместо video.mp4 на ваше_название.mp4
 await send_video_note_from_file(user_id, video_path) # отправляем видео

# первый текст
 await message.answer("""
 *Привет! На связи крипто-училка*

*Я подготовила 2 бесплатных ролика, где мы разберёмся, что такое криптовалюта, купим свои первые активы и, главное, поймем: как тут зарабатывать новичкам. *

Я могу долго расхваливать свой опыт в криптовалюте, но лучше предлагаю сразу заняться пользой. 

20 минут, и у тебя появится четкое понимание этой сферы.  

🎁 А те, кто пройдет бот полностью и просмотрит все уроки, получит в подарок персональную крипто-консультацию по стратегиям заработка в криптовалюте от нашей команды экспертов!

Нажимай кнопку и посмотри уроки, где ты узнаешь о криптовалюте больше, чем за всю свою жизнь. Нажмите здесь 👇""", reply_markup=start, parse_mode=ParseMode.MARKDOWN)

# ПЕРВЫЙ УРОК
 # 3 сек ждём
 await asyncio.sleep(3)
 # текст
 await message.answer('''
 *Урок 1 «Что такое криптовалюта и почему на ней зарабатывают - простыми словами»*

 *Смотрите по ссылке: https://youtu.be/-XLYQH8Tvd0 *

 За 20 минут вы поймете: 
 • Что из себя представляет криптовалюта
 • Имеет ли она какую-то ценность? 
 • Насколько безопасно хранить деньги в криптовалюте? 
 • Что ожидать от крипто-рынка в ближайшие 3 года, и когда лучшее время для входа

 После прохождения урока вы будете чувствовать себя намного увереннее и сможете сделать свои первые шаги в крипте.

 Вас ожидают скринкасты на такие темы:
 1. Регистрация на бирже Bybit
 2. Покупка первой крипты Bybit
 3. Функционал биржи Bybit

 Ссылка на 1 урок: https://youtu.be/-XLYQH8Tvd0

 Приятного просмотра!''', parse_mode=ParseMode.MARKDOWN)

 # ВТОРОЙ УРОК
 # 5 сек ждем
 await asyncio.sleep(5)
 # текст
 await message.answer(''' 
*Урок 2 «Актуальные стратегии для получения профита с помощью криптовалют»*

*Смотрите по ссылке: https://youtu.be/cBxHl0L5lmM *

В уроке мы разберем: 
1. Какие есть актуальные стратегии заработка на криптовалюте
2. Примеры успешных проектов или сделок 
3. Что можно сделать уже сейчас, чтобы начать инвестировать в криптовалюту.

Прямо сейчас переходите по ссылке: https://youtu.be/cBxHl0L5lmM

И узнайте информацию, которая открывает секреты заработка на крипте.''')

# ЖДЁМ СЕКУНДУ ПЕРЕД ВИДЕО
 await asyncio.sleep(1)
 #подгружаем видео 
 video_path = 'videos/video2.mp4'
 await send_video_note_from_file(user_id, video_path)
 #кнопка
 await message.answer('ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ👇🏻', reply_markup=register)
 # сам текст
 await message.answer('''
*Поздравляю, вы прошли все уроки этого бота и получаете звание «Ответственный криптан»🥳*

*Сейчас в течение 30 минут у вас есть уникальная возможность записаться на бесплатную консультацию от моей команды экспертов и кураторов.*

https://forms.gle/afoEKiJKc129Cqnz6

Это зум-созвон на 30-40 минут во время которого вы: 
а. Получите личный план развития в крипте
б. Узнаете ответы на все свои вопросы, которые возникли во время просмотра уроков
в. Определите цели и конкретные шаги на ближайшие 3 месяца для их достижения
г. Получите возможность попасть по спец. условиям на наше новое обучение в формате интенсива.

Если хотите сделать следующий шаг в этом направлении, то нажмите здесь👇🏻''', reply_markup=msg_reg, parse_mode=ParseMode.MARKDOWN)

# ЖДЁМ 6 СЕК | ФОРМАТ ОБУЧЕНИЯ
 await asyncio.sleep(6)
 await message.answer('''
* Поздравляю, теперь мы с вами пойдем еще дальше в изучение криптовалют! *

* Записаться на бесплатную консультацию вы можете по ссылке: *
 
https://forms.gle/afoEKiJKc129Cqnz6

Где: ZOOM 
Формат: онлайн-звонок с экспертом
Длительность: 30-40 минут

Результат: после нашей консультации, вы примите решение: подходит ли вам инвестирование в криптовалюту или нет.

А также поймете какие действия вам нужно совершить для дальнейшего развития и получите спец. условия на наше новое обучение в формате интенсива.

Анкета для записи: https://forms.gle/afoEKiJKc129Cqnz6

Ссылка действует 30 минут❗️

После заполнения моя команда с вами свяжется и назначит время и дату консультации. Проверяйте свои мессенджеры, чтобы ничего не пропустить! ''', reply_markup=register, parse_mode=ParseMode.MARKDOWN)


# коллбек функция для нажатой кнопки ОТКРЫТЬ УРОКИ
@dp.callback_query_handler(text="OpenYrok")
async def msg_r(call: types.CallbackQuery):
 await call.answer('Уроки открыты') # уведомление 
 await call.message.answer('''
*Поздравляю, теперь мы с вами пойдем еще дальше в изучение криптовалют!*

*Записаться на бесплатную консультацию вы можете по ссылке:*
 
https://forms.gle/afoEKiJKc129Cqnz6

Где: ZOOM 
Формат: онлайн-звонок с экспертом
Длительность: 30-40 минут

Результат: после нашей консультации, вы примите решение: подходит ли вам инвестирование в криптовалюту или нет.

А также поймете какие действия вам нужно совершить для дальнейшего развития и получите спец. условия на наше новое обучение в формате интенсива.

Анкета для записи: https://forms.gle/afoEKiJKc129Cqnz6

Ссылка действует 30 минут❗️

После заполнения моя команда с вами свяжется и назначит время и дату консультации. Проверяйте свои мессенджеры, чтобы ничего не пропустить!''', reply_markup=register, parse_mode=ParseMode.MARKDOWN)


##########################
##########################
# ДЛЯ АДМИНИСТРАТОРОВ
##########################
##########################
admin = 6306428168 # ваш USER ID 

# кнопки для админки
adminka_btn = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Панель", callback_data="panel"),
    InlineKeyboardButton('Рассылка', callback_data="rss")
)
panel_adm = InlineKeyboardMarkup().add(
    InlineKeyboardButton('Создать новое сообщение', callback_data="new_msg"),
    InlineKeyboardButton('Редактировать сообщение', callback_data="edit_msg")
)

# классы для работы с состояниями 
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

# кнопка пропуска
skip_button = InlineKeyboardMarkup().add(InlineKeyboardButton("Пропустить", callback_data="skip"))


# Обработчик команды админ
@dp.message_handler(commands=['admin'])
async def adminkaa(message: types.Message):
    if message.from_user.id == admin:
        await message.answer('Приветствую в панели администратора!\n\nВыберите действие ниже👇🏻', reply_markup=adminka_btn)
    else:
        await message.answer('Отказано')
# обработчик панели
@dp.callback_query_handler(text="panel")
async def panel(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer('ПАНЕЛЬ АДМИНИСТРАТОРА:', reply_markup=panel_adm)


# создание нового сообщения
@dp.callback_query_handler(text="new_msg")
async def new_msg(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Введите текст нового сообщения:", reply_markup=skip_button)
    await NewMessage.text.set()

@dp.message_handler(state=NewMessage.text)
async def new_msg_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Прикрепите фото или видео (если надо):", reply_markup=skip_button)
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
    await call.message.answer("Введите текст кнопки:", reply_markup=skip_button)
    await NewMessage.button_text.set()

@dp.message_handler(state=NewMessage.button_text)
async def new_msg_button_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_text'] = message.text
    button_type = data.get('button_type')
    if button_type == 'button_url':
        await message.answer("Введите URL для кнопки:", reply_markup=skip_button)
        await NewMessage.button_url.set()
    elif button_type == 'button_text':
        await message.answer("Введите текст, который будет отправлен при нажатии на кнопку:", reply_markup=skip_button)
        await NewMessage.callback_text.set()  
    else:
        await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
        await NewMessage.repeat_time.set()

@dp.message_handler(state=NewMessage.button_url)
async def new_msg_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
    await NewMessage.repeat_time.set()

@dp.callback_query_handler(state=NewMessage.button_url, text="skip")
async def skip_new_button_url(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_url'] = None
    await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
    await NewMessage.repeat_time.set()

@dp.message_handler(state=NewMessage.callback_text)
async def new_msg_callback_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['callback_text'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
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

# ФУНКЦИЯ ДЛЯ СОЗДАНИЯ КНОПОК В СООБЩЕНИЯХ 
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

# функция редактирования сообщений
@dp.callback_query_handler(text="edit_msg")
async def edit_msg(call: types.CallbackQuery):
    await call.answer()
    messages = get_message_list()
    
    if messages:
        keyboard = InlineKeyboardMarkup()
        for msg_id, msg_text in messages:
            button_text = f"{msg_id}: {msg_text[:30]}"  # Показать первые 30 символов текста сообщения
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
    await call.message.answer("Введите новый текст сообщения:", reply_markup=skip_button)
    await EditMessage.text.set()

@dp.callback_query_handler(state=EditMessage.select_message, text="skip")
async def skip_select_message(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите новый текст сообщения:", reply_markup=skip_button)
    await EditMessage.text.set()

@dp.message_handler(state=EditMessage.text)
async def edit_msg_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Прикрепите новое фото или видео (если надо):", reply_markup=skip_button)
    await EditMessage.media.set()

@dp.callback_query_handler(state=EditMessage.text, text="skip")
async def skip_edit_text(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['text'] = None
    await call.message.answer("Прикрепите новое фото или видео (если надо):", reply_markup=skip_button)
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
    await call.message.answer("Введите текст кнопки:", reply_markup=skip_button)
    await EditMessage.button_text.set()

@dp.message_handler(state=EditMessage.button_text)
async def edit_msg_button_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_text'] = message.text
    button_type = data.get('button_type')
    if button_type == 'button_url':
        await message.answer("Введите URL для кнопки:", reply_markup=skip_button)
        await EditMessage.button_url.set()
    elif button_type == 'button_text':
        await message.answer("Введите текст, который будет отправлен при нажатии на кнопку:", reply_markup=skip_button)
        await EditMessage.callback_text.set()
    else:
        await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
        await EditMessage.repeat_time.set()

@dp.callback_query_handler(state=EditMessage.button_text, text="skip")
async def skip_edit_button_text(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_text'] = None
    button_type = data.get('button_type')
    if button_type == 'button_url':
        await call.message.answer("Введите URL для кнопки:", reply_markup=skip_button)
        await EditMessage.button_url.set()
    elif button_type == 'button_text':
        await call.message.answer("Введите текст, который будет отправлен при нажатии на кнопку:", reply_markup=skip_button)
        await EditMessage.callback_text.set()
    else:
        await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
        await EditMessage.repeat_time.set()

@dp.message_handler(state=EditMessage.button_url)
async def edit_msg_button_url(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['button_url'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
    await EditMessage.repeat_time.set()

@dp.callback_query_handler(state=EditMessage.button_url, text="skip")
async def skip_edit_button_url(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['button_url'] = None
    await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
    await EditMessage.repeat_time.set()

@dp.message_handler(state=EditMessage.callback_text)
async def edit_msg_callback_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['callback_text'] = message.text
    await message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
    await EditMessage.repeat_time.set()

@dp.callback_query_handler(state=EditMessage.callback_text, text="skip")
async def skip_edit_callback_text(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    async with state.proxy() as data:
        data['callback_text'] = None
    await call.message.answer("Введите время в минутах для повторной отправки сообщения (если надо):", reply_markup=skip_button)
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

# КЛАСС РАССЫЛКИ
class Broadcast(StatesGroup):
    text = State()
    media = State()

# ФУНКЦИЯ РАССЫЛКИ
@dp.callback_query_handler(text="rss")
async def rss_broadcast(call: types.CallbackQuery):
    await call.answer()
    await call.message.answer("Введите текст сообщения для рассылки:", reply_markup=skip_button)
    await Broadcast.text.set()


@dp.message_handler(state=Broadcast.text)
async def broadcast_text(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
    await message.answer("Прикрепите фото или видео (если есть):", reply_markup=skip_button)
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

    # Send broadcast message
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

    # Send broadcast message without media
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

# ФУНКЦИЯ КОМПРЕССА ВИДЕО В КРУЖОЧЕК
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

# список пользователей
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

# ФУНКЦИЯ ОТПРАВКИ СООБЩЕНИЙ ПО ПОЛЬЗОВАТЕЛЯМ (КАЖДЫЕ N-НЫЕ МИНУТЫ)
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


# Запуск самого бота
if __name__ == '__main__':
    reschedule_messages() 
    executor.start_polling(dp, skip_updates=True)


##################################
##################################
# DEVELOPER: FSURE09 (TG)
##################################
# ЖДУ ВАС ЕЩЕ <З
##################################
##################################
