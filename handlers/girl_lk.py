from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import logger
from database import db
from keyboards import main_kb
from states.states import ReqMoney

router = Router()
router.message.filter(
)


@router.callback_query(F.data == 'girls_lk')
async def p_girls_lk(callback: CallbackQuery):
    await callback.answer()
    try:
        uid = callback.from_user.id
        username = callback.from_user.username
        gd = await db.get_girl_data(uid)
        g_orders, g_balance = gd['orders'], gd['balance']
        g_info = (f'<b>ID:</b> {uid}'
                  f'\n<b>Ник:</b> {username}'
                  f'\n<b>Выполнено заказов:</b> {g_orders}'
                  f'\n<b>Баланс:</b> {g_balance}')
        await callback.message.answer(g_info, reply_markup=main_kb.lk_menu())
    except Exception as e:
        logger.error(e)
        await callback.message.answer('Информация не найдена. Возможно, вы еще не создали анкету.')


@router.callback_query(F.data == 'req_money')
async def p_req_money(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    uid = callback.from_user.id
    try:
        g_balance = (await db.get_girl_data(uid))['balance']
        wd_reqs = await db.get_withdraw_requests()
        for k, v in wd_reqs:
            if v == uid:
                raise ValueError
        if g_balance > 0:
            await callback.message.answer('Введите номер банковской карты: ')
            await state.set_state(ReqMoney.input_card)
        else:
            await callback.message.answer('<b>🔴 Минимальная сумма вывода - </b> 500 рублей')
            return
    except ValueError:
        await callback.message.answer('Максимальное количество заявок на вывод - 1.'
                                      '\nПожалуйста, дождитесь обработки вашей заявки администратором, или свяжитесь с тех. поддержкой.')


@router.message(ReqMoney.input_card)
async def p_input_card(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer('Пожалуйста, введите корректный номер карты.')
    else:
        uid = message.from_user.id
        username = message.from_user.username
        g_balance = (await db.get_girl_data(uid))['balance']
        await db.create_withdraw_request(uid, username, int(g_balance))
        await message.answer('Заявка на вывод средств создана.'
                             '\nВам будет отправлено уведомление, после подтверждения заявки администратором.')
        await state.clear()
