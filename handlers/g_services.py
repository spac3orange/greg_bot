from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile, Message
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.fsm.context import FSMContext
from states.states import AddService
from database import db
from keyboards import main_kb
from states.states import DelService
from config import logger

router = Router()
router.message.filter(
)


@router.callback_query(F.data == 'g_add_service')
async def p_inp_serv_name(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введи название услуги:')
    await state.set_state(AddService.input_name)


@router.message(AddService.input_name)
async def p_serv_inp_price(message: Message, state: FSMContext):
    await state.update_data(serv_type=message.text)
    serv_name = message.text
    await state.update_data(serv_name=serv_name)
    await message.answer('Введи цену услуги: ')
    await state.set_state(AddService.input_price)


@router.message(AddService.input_price, lambda message: message.text.isdigit())
async def p_save_serv(message: Message, state: FSMContext):
    uid, uname = message.from_user.id, message.from_user.username
    serv_price = int(message.text)
    data = await state.get_data()
    serv_name = data['serv_name']
    await message.answer(f'Имя услуги: {serv_name}'
                         f'\nЦена услуги: {serv_price}'
                         f'\n\nУслуга добавлена.'
                         f'\n\nДобавить новые услуги или редактировать существующие ты можешь на странице <b>Моя анкета</b>.', reply_markup=main_kb.g_add_additional_serv())
    await db.insert_service(uid, uname, serv_name, serv_price)


@router.callback_query(F.data == 'edit_services')
async def p_g_edit_serv(call: CallbackQuery, state: FSMContext):
    await call.answer()
    uid = call.from_user.id
    g_services = await db.get_services_by_user_id(uid)
    print(g_services)
    if g_services:
        s_string = ''
        for s in g_services:
            print(s)
            service_info = f'<b>Название:</b> {s["service_name"]}\n<b>Цена:</b> {s["price"]}\n'
            s_string += f'\n\n{service_info}'
        await call.message.answer(s_string, reply_markup=main_kb.g_edit_serv())

    else:
        await call.message.answer('У вас еще нет услуг.', reply_markup=main_kb.g_edit_serv())


@router.callback_query(F.data == 'g_del_service')
async def p_g_del_serv(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer('Введите название услуги:')
    await state.set_state(DelService.input_name)


@router.message(DelService.input_name)
async def p_del_serv(message: Message, state: FSMContext):
    serv_name = message.text
    uid = message.from_user.id
    try:
        await db.delete_service(uid, serv_name)
        await state.clear()
        await message.answer('Услуга удалена.')
    except Exception as e:
        await message.answer('Ошибка при удалении услуги.')
        logger.error(e)

