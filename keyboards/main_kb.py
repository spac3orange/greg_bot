from aiogram.utils.keyboard import InlineKeyboardBuilder
from config import config_aiogram


def start_btns(uid):
    admins = config_aiogram.admin_id
    kb_builder = InlineKeyboardBuilder()
    if str(uid) in admins:
        kb_builder.button(text='Создать анкету', callback_data='create_form')
        kb_builder.button(text='Моя анкета', callback_data='my_forms')
        kb_builder.button(text='Статус', callback_data='edit_status')
        kb_builder.button(text='Личный кабинет', callback_data='girls_lk')
        kb_builder.button(text='Админ панель', callback_data='admin_panel')
        kb_builder.button(text='Тех. Поддержка', url='https://t.me/stepusiks')
    else:
        kb_builder.button(text='Создать анкету', callback_data='create_form')
        kb_builder.button(text='Моя анкета', callback_data='my_forms')
        kb_builder.button(text='Статус', callback_data='edit_status')
        kb_builder.button(text='Личный кабинет', callback_data='girls_lk')
        kb_builder.button(text='Тех. Поддержка', url='https://t.me/stepusiks')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def lk_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Запросить вывод', callback_data='req_money')
    kb_builder.button(text='Назад', callback_data='back_to_main')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def choose_games(game_dict):
    kb_builder = InlineKeyboardBuilder()

    for k, v in game_dict.items():
        kb_builder.button(text=f'{k}', callback_data=f'{v}')

    kb_builder.button(text='Продолжить', callback_data='game_continue')
    kb_builder.button(text='Назад', callback_data='back_to_main')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def approve_form():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Подтвердить', callback_data='form_created')
    kb_builder.button(text='Изменить анкету', callback_data='create_form')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def edit_form():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Редактировать', callback_data='create_form')
    kb_builder.button(text='Удалить', callback_data='del_self_form')
    kb_builder.button(text='Назад', callback_data='back_to_main')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def admin_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Заявки на вывод', callback_data='wd_requests')
    kb_builder.button(text='Анкеты', callback_data='all_forms')
    kb_builder.button(text='Назад', callback_data='back_to_main')
    kb_builder.adjust(1)
    return kb_builder.as_markup(resize_keyboard=True)


def req_menu(req_id):
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Оплачено', callback_data=f'apply_req_{req_id}')
    kb_builder.button(text='Отказать', callback_data=f'decline_req_{req_id}')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)


def adm_form_edit(del_id):
    print(del_id)
    print(type(del_id))
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Удалить', callback_data=f'adm_del_form_{del_id}')
    return kb_builder.as_markup(resize_keyboard=True)


def g_status_menu():
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text='Онлайн', callback_data=f'chstatus_online')
    kb_builder.button(text='Оффлайн', callback_data=f'chstatus_offline')
    kb_builder.adjust(2)
    return kb_builder.as_markup(resize_keyboard=True)
