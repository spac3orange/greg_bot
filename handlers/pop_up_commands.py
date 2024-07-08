from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

router = Router()
router.message.filter(
)


@router.message(Command('support'))
async def p_sup(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Тех. Поддержка: @egirlforyou')
