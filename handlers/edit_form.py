import json

from aiogram import Router, F
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.media_group import MediaGroupBuilder

from config import logger, aiogram_bot
from database import db
from keyboards import main_kb
import magic
router = Router()
router.message.filter(
)


async def parse_media(path):
    return FSInputFile(path)


async def get_mime_type(file_path):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mime_type


async def is_video(file_path):
    mime_type = await get_mime_type(file_path)
    return mime_type.startswith('video')


async def is_photo(file_path):
    mime_type = await get_mime_type(file_path)
    return mime_type.startswith('image')


@router.callback_query(F.data == 'my_forms')
async def p_forms(callback: CallbackQuery):
    await callback.answer()
    try:
        uid = callback.from_user.id
        await aiogram_bot.send_chat_action(callback.from_user.id, 'typing')
        gd = await db.get_girl_data(uid)

        # Получение списка аватаров из JSON
        avatar_paths = json.loads(gd['avatar_path'])
        print(avatar_paths)
        # Создание альбома медиафайлов
        album_builder = MediaGroupBuilder()
        for avatar_path in avatar_paths:
            if await is_video(avatar_path):
                album_builder.add_video(media=FSInputFile(avatar_path))
            elif await is_photo(avatar_path):
                album_builder.add_photo(media=FSInputFile(avatar_path))

        form_descr = (f"{gd['name']}, {gd['age']}"
                      f"\n<b>Игры:</b> {gd['games']}"
                      f"\n{gd['description']}"
                      f"\n<b>Цена за включение веб-камеры:</b> {gd['price']}"
                      f"\n<b>Цена за дополнительных участников:</b> {gd['price_per_ppl']}")

        # Отправка группы медиа
        if album_builder:
            await callback.message.answer_media_group(media=album_builder.build())
            await callback.message.answer(text=form_descr, reply_markup=main_kb.edit_form())
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
