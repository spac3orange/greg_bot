import os
import random
import magic
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from aiogram.types import Message, CallbackQuery, ContentType
from aiogram.utils.media_group import MediaGroupBuilder

from config import logger, aiogram_bot
from database import db
from keyboards import main_kb
from states.states import CreateForm

router = Router()
router.message.filter(
)

FORBIDDEN_CHARS = ['<', '>']
# Лямбда-функция для проверки запрещенных символов
lambda_check_forbidden_chars = lambda message: not contains_forbidden_chars(message.text)


async def get_mime_type(file_path):
    mime = magic.Magic(mime=True)
    mime_type = mime.from_file(file_path)
    return mime_type


def contains_forbidden_chars(text):
    return any(char in text for char in FORBIDDEN_CHARS)


async def is_video(file_path):
    mime_type = await get_mime_type(file_path)
    return mime_type.startswith('video')


async def is_photo(file_path):
    mime_type = await get_mime_type(file_path)
    return mime_type.startswith('image')



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


@router.message(CreateForm.input_name, lambda_check_forbidden_chars)
async def p_input_name(message: Message, state: FSMContext):
    name = message.text

    await state.update_data(name=name)
    await message.answer('Сколько тебе лет?')
    await state.set_state(CreateForm.input_age)

@router.message(CreateForm.input_name)
async def p_input_name_inv(message: Message, state: FSMContext):
    name = message.text
    await message.answer('Обнаружены запрещенные символы &lt; или &gt;.\nПожалуйста, не используйте их.')
    return



@router.message(CreateForm.input_age, lambda message: message.text.isdigit())
async def p_input_age(message: Message, state: FSMContext):
    age = message.text
    await state.update_data(age=age)
    await message.answer('Теперь пришли фото, или запиши видео (до 15 сек), оно будет отображаться в твоей анкете:\n\nПожалуйста, отправляй файлы по одному. Всего в анкете может быть до 3-х меда файлов.')
    await state.set_state(CreateForm.input_photo)


@router.message(CreateForm.input_photo, lambda message: message.content_type in [ContentType.PHOTO, ContentType.VIDEO] and message.media_group_id is None)
async def p_process_media(message: Message, state: FSMContext):
    try:
        uid = message.from_user.id
        randint = random.randint(1000, 9999)

        if message.content_type == ContentType.PHOTO:
            media_type = 'photo'
            file_id = message.photo[-1].file_id
        elif message.content_type == ContentType.VIDEO:
            media_type = 'video'
            file_id = message.video.file_id

            # Получаем информацию о файле
        file_info = await aiogram_bot.get_file(file_id)
        file_path = file_info.file_path
        file_extension = os.path.splitext(file_path)[1][1:]  # Извлекаем расширение файла без точки
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


@router.message(CreateForm.input_photo2, lambda message: message.content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.TEXT] and message.media_group_id is None)
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
            elif message.content_type == ContentType.VIDEO:
                media_type = 'video'
                file_id = message.video.file_id

                # Получаем информацию о файле
            file_info = await aiogram_bot.get_file(file_id)
            file_path = file_info.file_path
            file_extension = os.path.splitext(file_path)[1][1:]  # Извлекаем расширение файла без точки
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


@router.message(CreateForm.input_photo3, lambda message: message.content_type in [ContentType.PHOTO, ContentType.VIDEO, ContentType.TEXT] and message.media_group_id is None)
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
            elif message.content_type == ContentType.VIDEO:
                media_type = 'video'
                file_id = message.video.file_id

                # Получаем информацию о файле
            file_info = await aiogram_bot.get_file(file_id)
            file_path = file_info.file_path
            file_extension = os.path.splitext(file_path)[1][1:]  # Извлекаем расширение файла без точки

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


@router.message(CreateForm.input_photo, lambda message: message.media_group_id is not None)
async def p_process_media_group1(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, загружайте медиа файлы по одному.')
    return


@router.message(CreateForm.input_photo2, lambda message: message.media_group_id is not None)
async def p_process_media_group2(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, загружайте медиа файлы по одному.')
    return


@router.message(CreateForm.input_photo3, lambda message: message.media_group_id is not None)
async def p_process_media_group3(message: Message, state: FSMContext):
    await message.answer('Пожалуйста, загружайте медиа файлы по одному.')
    return


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


@router.message(CreateForm.input_description, lambda_check_forbidden_chars)
async def p_add_price_form(message: Message, state: FSMContext):

    await state.update_data(form_description=message.text)
    await message.answer('Укажи желаемую цену за включение веб-камеры: ')
    await state.set_state(CreateForm.input_viewers_p)





@router.message(CreateForm.input_description)
async def p_add_price_form_inv(message: Message, state: FSMContext):
    await message.answer('Обнаружены запрещенные символы &lt; или &gt;.\nПожалуйста, не используйте их.')
    return


@router.message(CreateForm.input_viewers_p, lambda message: message.text.isdigit() and int(message.text) >= 300)
async def p_input_v_price(message: Message, state: FSMContext):
    await state.update_data(web_price=int(message.text))
    await message.answer('Укажи желаемую сумму доплаты за 1 человека: ')
    await state.set_state(CreateForm.input_price)


@router.message(CreateForm.input_viewers_p)
async def p_input_description(message: Message, state: FSMContext):
    await message.answer('Цена должна быть цифрой!'
                         '\nМинимальная цена: 300 руб.')


@router.message(CreateForm.input_price, lambda message: message.text.isdigit() and int(message.text) >= 50)
async def p_input_description(message: Message, state: FSMContext):
    await state.update_data(add_viewers=int(message.text))
    data = await state.get_data()
    print(data)

    # Получение путей к аватарам из состояния
    avatar_path1 = data.get('avatar_path1', None)
    avatar_path2 = data.get('avatar_path2', None)
    avatar_path3 = data.get('avatar_path3', None)
    print(avatar_path1, avatar_path2, avatar_path3)

    # Преобразование путей в абсолютные пути
    avatar_abspath1 = os.path.abspath(avatar_path1) if avatar_path1 else None
    avatar_abspath2 = os.path.abspath(avatar_path2) if avatar_path2 else None
    avatar_abspath3 = os.path.abspath(avatar_path3) if avatar_path3 else None

    chosen_games = await compare_dicts(data['game_dict'])
    game_list = []
    for game in chosen_games:
        game_list.append(game)
    game_str = ', '.join(game_list)
    await state.update_data(games_str=game_str)
    await message.answer('Предпросмотр анкеты: ')
    # Создание альбома медиафайлов
    full_form = (f'{data["name"]}, {data["age"]}'
                 f'\n<b>Игры:</b> \n{game_str}'
                 f'\n{data["form_description"]}'
                 f'\n<b>Цена за включение веб-камеры:</b> {data["web_price"]} рублей'
                 f'\n<b>Цена за дополнительных участников:</b> {data["add_viewers"]} рублей')
    album_builder = MediaGroupBuilder()
    if avatar_abspath1:
        if await is_video(avatar_abspath1):
            album_builder.add_video(media=FSInputFile(avatar_abspath1))
        elif await is_photo(avatar_abspath1):
            album_builder.add_photo(media=FSInputFile(avatar_abspath1))

    if avatar_abspath2:
        if await is_video(avatar_abspath2):
            album_builder.add_video(media=FSInputFile(avatar_abspath2))
        elif await is_photo(avatar_abspath2):
            album_builder.add_photo(media=FSInputFile(avatar_abspath2))

    if avatar_abspath3:
        if await is_video(avatar_abspath3):
            album_builder.add_video(media=FSInputFile(avatar_abspath3))
        elif await is_photo(avatar_abspath3):
            album_builder.add_photo(media=FSInputFile(avatar_abspath3))
    # Отправка группы медиа
    if album_builder:
        await message.answer_media_group(media=album_builder.build())
        await message.answer(text=full_form, reply_markup=main_kb.approve_form())


@router.message(CreateForm.input_price)
async def p_input_description(message: Message, state: FSMContext):
    await message.answer('Цена должна быть цифрой!'
                         '\nМинимальная цена: 50 рублей')


@router.callback_query(F.data == 'form_created')
async def p_form_created(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    await callback.answer()
    print(data)
    uid, username = callback.from_user.id, callback.from_user.username

    # Получение путей к аватарам из состояния
    avatar_path1 = data.get('avatar_path1', None)
    avatar_path2 = data.get('avatar_path2', None)
    avatar_path3 = data.get('avatar_path3', None)

    # Преобразование путей в абсолютные пути
    avatar_paths = [os.path.abspath(path) for path in [avatar_path1, avatar_path2, avatar_path3] if path]

    # Вставка данных в базу данных
    await db.insert_girl_data(
        uid, username, data.get('name', 'Unknown'),
        int(data['age']), data['games_str'],
        avatar_paths, data['form_description'],
        data['web_price'], data['add_viewers']
    )

    # Регистрация в смене
    await db.reg_in_shift(uid, username)

    # Отправка сообщения пользователю с подтверждением создания анкеты
    await callback.message.answer('Анкета создана.\nТеперь ты можешь добавить услуги.', reply_markup=main_kb.g_add_serv())
    await state.clear()
