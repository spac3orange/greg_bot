from datetime import datetime, timedelta
from aiogram.types import Message, CallbackQuery, FSInputFile, ContentType
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger, aiogram_bot
from filters import CTFilter
from keyboards import main_kb
from database import db
from states.states import SetStatusOnline
from utils import Scheduler
import random
import os

router = Router()
router.message.filter(
)


async def inform_status(uid):
    try:
        text = 'Ваша смена закончена. Статус переведен в <b>Offline</b>.'
        await db.clear_shift(uid)
        await aiogram_bot.send_message(uid, text)
    except Exception as e:
        logger.error(e)
        return


@router.callback_query(F.data == 'edit_status')
async def p_status_menu(call: CallbackQuery):
    await call.answer()
    g_status = await db.get_shift_status(call.from_user.id)

    if g_status == 'User not found':
        await call.message.answer('Анкета не найдена. Пожалуйста, сначала создайте анкету.')
        return
    start_time = g_status.get("shift_start", 'Нет')
    end_time = g_status.get("shift_end", "Нет")
    print(start_time, end_time)
    if start_time == 'None':
        start_time = end_time = 'Нет'

    await call.message.answer(f'Текущий статус: {g_status["shift_status"]}'
                              f'\nВремя начала смены: {start_time}'
                              f'\nВремя окончания смены: {end_time}', reply_markup=main_kb.g_status_menu())


@router.callback_query(F.data == 'chstatus_online')
async def p_chst_online(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите количество часов работы: ')
    await state.set_state(SetStatusOnline.input_hours)


@router.message(SetStatusOnline.input_hours, lambda message: message.text.strip().isdigit() and 0 < int(message.text) <= 24)
async def p_set_online_status(message: Message, state: FSMContext):
    user_id = message.from_user.id
    username = message.from_user.username
    hours = int(message.text)

    # Calculate shift start and end times
    shift_start = datetime.now()
    shift_end = shift_start + timedelta(hours=hours)

    # Convert datetime to string format if your database expects a string
    shift_start_str = shift_start.strftime('%d-%m-%Y %H:%M:%S')
    shift_end_str = shift_end.strftime('%d-%m-%Y %H:%M:%S')

    # Adding the shift to the database
    result = await db.add_shift(user_id, username, 'Online', shift_start_str, shift_end_str)
    await message.answer('Статус - <b>Online</b>. '
                         f'\nВремя работы: {shift_start_str} - {shift_end_str}')

    scheduler = Scheduler()
    timing = hours * 3600
    await scheduler.schedule_task(timing, user_id, inform_status)


@router.message(SetStatusOnline.input_hours)
async def err_status(message: Message, state: FSMContext):
    await message.answer('Ошибка обновления статуса. Пожалуйста, введите кол-во часов (цифра) от 1 до 24: ')
    return


@router.callback_query(F.data == 'chstatus_offline')
async def p_chst_offline(call: CallbackQuery, state: FSMContext):
    user_id = call.from_user.id
    await db.clear_shift(user_id)
    await call.answer()
    await call.message.answer('Статус - <b>Offline</b>')