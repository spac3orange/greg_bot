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
from aiocache import Cache
from aiocache.serializers import JsonSerializer
from typing import Dict, Any

router = Router()
router.message.filter(
)

cache = Cache(Cache.MEMORY, serializer=JsonSerializer())


async def go_main(callback):
    uid = callback.from_user.id
    await callback.message.answer('Добро пожаловать!', reply_markup=main_kb.start_btns(uid))


async def check_folder(folder_name):
    if not os.path.exists(f'media/{folder_name}'):
        # Создаем папку
        os.makedirs(f'media/{folder_name}')
        logger.info(f"Папка {folder_name} успешно создана.")
    else:
        logger.info(f"Папка {folder_name} уже существует.")


async def compare_dicts(dict2):
    dict1 = {'CS 2': 'game_cs2', 'DOTA 2': 'game_dota2',
             'VALORANT': 'game_val', 'APEX': 'game_apex',
             'Общение': 'game_talk'}
    diff = {}
    for key, value in dict1.items():
        if key not in dict2 or dict2[key] != value:
            diff[key] = value
    return diff


async def parse_media(path):
    return FSInputFile(path)


@router.callback_query(F.data == 'create_form')
async def p_create_form(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.answer()
    await callback.message.answer('Как тебя зовут?')
    await state.set_state(CreateForm.input_name)


@router.message(CreateForm.input_name)
async def p_input_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer('Сколько тебе лет?')
    await state.set_state(CreateForm.input_age)


@router.message(CreateForm.input_age, lambda message: message.text.isdigit())
async def p_input_age(message: Message, state: FSMContext):
    age = message.text
    await state.update_data(age=age)
    await message.answer('Теперь пришли фото, или запиши видео (до 15 сек), оно будет отображаться в твоей анкете:')
    await state.set_state(CreateForm.input_photo)


@router.message(CreateForm.input_photo, lambda message: message.content_type in [ContentType.PHOTO, ContentType.VIDEO])
async def p_process_media(message: Message, state: FSMContext):
    try:
        uid = message.from_user.id
        randint = random.randint(1000, 9999)

        if message.content_type == ContentType.PHOTO:
            media_type = 'photo'
            file_id = message.photo[-1].file_id
            file_extension = 'jpg'
        elif message.content_type == ContentType.VIDEO:
            media_type = 'video'
            file_id = message.video.file_id
            file_extension = 'mp4'

        file_info = await aiogram_bot.get_file(file_id)
        if file_info.file_size > 10 * 1024 * 1024:
            await message.answer("Файл слишком большой. Пожалуйста, загрузите файл размером не более 10 мегабайт.")
            return

        media_name = f'{uid}_{randint}_{media_type}.{file_extension}'
        file_info = await aiogram_bot.get_file(file_id)
        downloaded_file = await aiogram_bot.download_file(file_info.file_path)
        await check_folder(uid)
        with open(f'media/{uid}/{media_name}', 'wb') as media_file:
            media_file.write(downloaded_file.read())

        await state.update_data(avatar_path1=f'media/{uid}/{media_name}')
        await state.set_state(CreateForm.input_photo2)
        await message.answer('Загрузи следующий файл или напиши <b>Далее</b>')
    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при загрузке файла.')


@router.message(CreateForm.input_photo2, lambda message: message.content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.TEXT])
async def p_process_media2(message: Message, state: FSMContext):
    try:
        if message.text:
            if message.text.lower() == 'далее':
                game_dict = {'CS 2': 'game_cs2', 'DOTA 2': 'game_dota2',
                             'VALORANT': 'game_val', 'APEX': 'game_apex',
                             'Общение': 'game_talk'}
                await state.update_data(game_dict=game_dict)

                await message.answer('Выбери игры, в которые ты играешь: ', reply_markup=main_kb.choose_games(game_dict))
                await state.set_state(CreateForm.input_games)
        else:
            uid = message.from_user.id
            randint = random.randint(1000, 9999)

            if message.content_type == ContentType.PHOTO:
                media_type = 'photo'
                file_id = message.photo[-1].file_id
                file_extension = 'jpg'
            elif message.content_type == ContentType.VIDEO:
                media_type = 'video'
                file_id = message.video.file_id
                file_extension = 'mp4'

            file_info = await aiogram_bot.get_file(file_id)
            if file_info.file_size > 10 * 1024 * 1024:
                await message.answer("Файл слишком большой. Пожалуйста, загрузите файл размером не более 10 мегабайт.")
                return

            media_name = f'{uid}_{randint}_{media_type}.{file_extension}'
            file_info = await aiogram_bot.get_file(file_id)
            downloaded_file = await aiogram_bot.download_file(file_info.file_path)
            await check_folder(uid)
            with open(f'media/{uid}/{media_name}', 'wb') as media_file:
                media_file.write(downloaded_file.read())

            await state.update_data(avatar_path2=f'media/{uid}/{media_name}')
            await state.set_state(CreateForm.input_photo3)
            await message.answer('Загрузи следующий файл или напиши <b>Далее</b>')

    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при загрузке файла.')


@router.message(CreateForm.input_photo3, lambda message: message.content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.TEXT])
async def p_process_media3(message: Message, state: FSMContext):
    try:
        if message.text:
            if message.text.lower() == 'далее':
                game_dict = {'CS 2': 'game_cs2', 'DOTA 2': 'game_dota2',
                             'VALORANT': 'game_val', 'APEX': 'game_apex',
                             'Общение': 'game_talk'}
                await state.update_data(game_dict=game_dict)

                await message.answer('Выбери игры, в которые ты играешь: ', reply_markup=main_kb.choose_games(game_dict))
                await state.set_state(CreateForm.input_games)
        else:
            uid = message.from_user.id
            randint = random.randint(1000, 9999)

            if message.content_type == ContentType.PHOTO:
                media_type = 'photo'
                file_id = message.photo[-1].file_id
                file_extension = 'jpg'
            elif message.content_type == ContentType.VIDEO:
                media_type = 'video'
                file_id = message.video.file_id
                file_extension = 'mp4'

            file_info = await aiogram_bot.get_file(file_id)
            if file_info.file_size > 10 * 1024 * 1024:
                await message.answer("Файл слишком большой. Пожалуйста, загрузите файл размером не более 10 мегабайт.")
                return

            media_name = f'{uid}_{randint}_{media_type}.{file_extension}'
            file_info = await aiogram_bot.get_file(file_id)
            downloaded_file = await aiogram_bot.download_file(file_info.file_path)
            await check_folder(uid)
            with open(f'media/{uid}/{media_name}', 'wb') as media_file:
                media_file.write(downloaded_file.read())

            await state.update_data(avatar_path3=f'media/{uid}/{media_name}')

            game_dict = {'CS 2': 'game_cs2', 'DOTA 2': 'game_dota2',
                         'VALORANT': 'game_val', 'APEX': 'game_apex',
                         'Общение': 'game_talk'}
            await state.update_data(game_dict=game_dict)

            await message.answer('Выбери игры, в которые ты играешь: ', reply_markup=main_kb.choose_games(game_dict))
            await state.set_state(CreateForm.input_games)

    except Exception as e:
        logger.error(e)
        await message.answer('Ошибка при загрузке файла.')


@router.callback_query(lambda callback: callback.data in ['game_cs2', 'game_dota2', 'game_val', 'game_apex', 'game_talk'])
async def p_choose_game(callback: CallbackQuery, state: FSMContext):

    remove_game = callback.data
    print(remove_game)
    game_dict = (await state.get_data())['game_dict']
    if remove_game:
        new_game_dict = {k: v for k, v in game_dict.items() if v != remove_game}
    else:
        new_game_dict = game_dict
    await state.update_data(game_dict=new_game_dict)
    await callback.message.edit_text('Выбери игры, в которые ты играешь: ', reply_markup=main_kb.choose_games(new_game_dict))


@router.callback_query(F.data == 'game_continue')
async def p_check_form(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text('Расскажи о себе: ')
    await state.set_state(CreateForm.input_description)


@router.message(CreateForm.input_description)
async def p_add_price_form(message: Message, state: FSMContext):
    await state.update_data(form_description=message.text)
    await message.answer('Введи желаемую цену за час игры: ')
    await state.set_state(CreateForm.input_price)


@router.message(CreateForm.input_price, lambda message: message.text.isdigit() and int(message.text) >= 300)
async def p_input_description(message: Message, state: FSMContext):
    await state.update_data(price=int(message.text))
    data = await state.get_data()
    media = await parse_media(data['avatar_path'])
    chosen_games = await compare_dicts(data['game_dict'])
    game_list = []
    for game in chosen_games:
        game_list.append(game)
    game_str = ', '.join(game_list)
    await state.update_data(games_str=game_str)
    await message.answer('Предпросмотр анкеты: ')
    full_form = (f'{data["name"]}, {data["age"]}'
                 f'\n<b>Игры:</b> \n{game_str}'
                 f'\n{data['form_description']}'
                 f'\n<b>Цена за час:</b> {data["price"]}')
    await message.answer_photo(media, caption=full_form, reply_markup=main_kb.approve_form())


@router.message(CreateForm.input_price)
async def p_input_description(message: Message, state: FSMContext):
    await message.answer('Цена должна быть цифрой!'
                         '\nМинимальная цена: 300 руб.')


@router.callback_query(F.data == 'form_created')
async def p_form_created(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer()
    print(data)
    uid, username = callback.from_user.id, callback.from_user.username
    await state.clear()
    # Получение путей к аватарам из состояния
    avatar_path = data.get('avatar_path', None)
    avatar_path2 = data.get('avatar_path2', None)
    avatar_path3 = data.get('avatar_path3', None)
    print(avatar_path, avatar_path2, avatar_path3)
    # Преобразование путей в абсолютные пути
    avatar_abspath = os.path.abspath(avatar_path) if avatar_path else None
    avatar_abspath2 = os.path.abspath(avatar_path2) if avatar_path2 else None
    avatar_abspath3 = os.path.abspath(avatar_path3) if avatar_path3 else None

    avatar_abspath = os.path.abspath(data['avatar_path'])
    await db.insert_girl_data(
        uid, username, data.get('name', 'Uknown'),
        int(data['age']), data['games_str'],
        avatar_abspath, data['form_description'],
        data['price']
    )
    await callback.message.answer('Анкета создана.')
    await db.reg_in_shift(uid, username)
    await go_main(callback)