from aiogram.types import Message, CallbackQuery, FSInputFile, ContentType
from aiogram.filters import CommandStart, Command
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from config import logger, aiogram_bot
from filters import CTFilter
from keyboards import main_kb
from database import db
from states.states import CreateForm
import random
import os
router = Router()
router.message.filter(
)


@router.message(Command('support'))
async def p_sup(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Тех. Поддержка: @None')