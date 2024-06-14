from aiogram.types import Message, CallbackQuery, FSInputFile, ContentType
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger, aiogram_bot
from filters import CTFilter
from keyboards import main_kb
from database import db
router = Router()
router.message.filter(
)


async def parse_media(path):
    return FSInputFile(path)


@router.callback_query(F.data == 'my_forms')
async def p_forms(callback: CallbackQuery):
    await callback.answer()
    try:
        uid = callback.from_user.id
        await aiogram_bot.send_chat_action(callback.from_user.id, 'typing')
        gd = await db.get_girl_data(uid)
        avatar = await parse_media(gd['avatar_path'])
        form_descr = (f"{gd['name']}, {gd['age']}"
                      f"\n<b>Игры:</b> {gd['games']}"
                      f"\n{gd['description']}"
                      f"\n<b>Цена за час:</b> {gd['price']}")
        await callback.message.answer_photo(avatar, caption=form_descr, reply_markup=main_kb.edit_form())
    except Exception as e:
        logger.error(e)
        await callback.message.answer('Информация не найдена. Возможно, вы еще не создали анкету.')


@router.callback_query(F.data == 'del_self_form')
async def p_del_form(call: CallbackQuery):
    try:
        uid = call.from_user.id
        await db.delete_form(uid)
        await call.message.answer('Анкета удалена.')
    except Exception as e:
        logger.error(e)
        await call.message.answer('Ошибка при удалении анкеты. Попробуйте позднее.')
