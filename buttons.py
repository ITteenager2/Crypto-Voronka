from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

start = InlineKeyboardMarkup()
start.add(InlineKeyboardButton('ОТКРЫТЬ УРОКИ', callback_data='OpenYrok'))

register = InlineKeyboardMarkup()
register.add(InlineKeyboardButton('ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ', url='https://rp-hub.ru/'))

msg_reg = InlineKeyboardMarkup()
msg_reg.add(InlineKeyboardButton('ЗАПИСАТЬСЯ НА КОНСУЛЬТАЦИЮ', callback_data='msg_r'))


adminka_btn = InlineKeyboardMarkup().add(
    InlineKeyboardButton("Панель", callback_data="panel"),
    InlineKeyboardButton('Рассылка', callback_data="rss")
)
panel_adm = InlineKeyboardMarkup().add(
    InlineKeyboardButton('Создать новое сообщение', callback_data="new_msg"),
    InlineKeyboardButton('Редактировать сообщение', callback_data="edit_msg")
)

skip_button = InlineKeyboardMarkup().add(InlineKeyboardButton("Пропустить", callback_data="skip"))