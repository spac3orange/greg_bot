from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger
from filters.is_admin import IsAdmin
from keyboards import main_kb
from database import db
router = Router()
router.message.filter(
)


async def parse_media(path='media/main_media_1.jpg'):
    return FSInputFile(path)


@router.message(Command(commands='start'))
async def process_start(message: Message, state: FSMContext):
    uid = message.from_user.id
    username = message.from_user.username
    media = await parse_media()
    await message.answer_photo(photo=media, caption='Добро пожаловать!', reply_markup=main_kb.start_btns(uid))
    logger.info(f'User connected: {username}')


@router.callback_query(F.data == 'back_to_main')
async def p_bctm(callback: CallbackQuery):
    await callback.answer()
    uid = callback.from_user.id
    media = await parse_media()
    await callback.message.reply_photo(photo=media, caption='<b>Добро пожаловать</b>', reply_markup=main_kb.start_btns(uid))
