from aiogram.types import Message, CallbackQuery, FSInputFile, ContentType
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger, aiogram_bot, config_aiogram
from filters import CTFilter, IsAdmin
from keyboards import main_kb
from database import db
from states.states import CreateForm
import random
import os
router = Router()
router.message.filter(
    IsAdmin(F)
)


async def parse_media(path):
    return FSInputFile(path)


@router.callback_query(F.data == 'admin_panel')
async def p_admin_panel(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    admins = config_aiogram.admin_id
    await callback.message.answer(f'<b>Admins:</b> {admins}', reply_markup=main_kb.admin_menu())


@router.callback_query(F.data == 'wd_requests')
async def p_wd_reqs(callback: CallbackQuery):
    wd_req = await db.get_withdraw_requests()
    print(wd_req)
    for req in wd_req:
        req_str = (f'<b>ID:</b> {req["user_id"]}'
                   f'\n<b>Username:</b>{req["username"]}'
                   f'\n<b>Баланс:</b> {req["balance"]}'
                   f'\n<b>Дата:</b> {req["date"]}')
        await callback.message.answer(req_str, reply_markup=main_kb.req_menu(req['user_id']))


@router.callback_query(F.data.startswith('apply_req_'))
async def p_apply_req(callback: CallbackQuery):
    req_id = callback.data.split('_')[-1]
    await callback.message.answer('Заявка обработана.')
    await db.change_withdraw_request_status(req_id, True)
    try:
        await aiogram_bot.send_message(chat_id=int(req_id), text='Ваша заявка обработана.'
                                                                 '\nСредства поступят на указанную карту в течении 24 часов.')
    except Exception as e:
        logger.error(e)
        return


@router.callback_query(F.data.startswith('decline_req_'))
async def p_decline_req(callback: CallbackQuery):
    req_id = callback.data.split('_')[-1]
    await callback.message.answer('Заявка отменена и удалена.')
    await db.delete_wd_request(int(req_id))
    try:
        await aiogram_bot.send_message(chat_id=int(req_id), text='Ваша заявка отменена.'
                                                                 '\nДля уточнения деталей, свяжитесь с тех. поддержкой.')
    except Exception as e:
        logger.error(e)
        return


@router.callback_query(F.data == 'all_forms')
async def p_get_all_forms(callback: CallbackQuery):
    all_girls = await db.get_all_girls()
    await callback.answer()
    if all_girls:
        for i in all_girls:
            del_id = i['user_id']
            media = await parse_media(i['avatar_path'])
            full_form = (f'{i["name"]}, {i["age"]}'
                         f'\n<b>Игры:</b> \n{i["games"]}'
                         f'\n{i['description']}')
            await callback.message.answer_photo(photo=media, caption=full_form, reply_markup=main_kb.adm_form_edit(del_id))
    else:
        await callback.message.answer('Анкеты не найдены.')


@router.callback_query(F.data.startswith('adm_del_form_'))
async def p_adm_del_form(callback: CallbackQuery):
    await callback.answer()
    try:
        del_id = int(callback.data.split('_')[-1])
        await db.delete_form(del_id)
        await callback.message.answer('Анкета удалена.')
    except Exception as e:
        logger.error(e)
        await callback.message.answer('Ошибка при удалении анкеты.')