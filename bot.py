import asyncio

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import aiogram_bot
from config.logger import logger
from database import db
from handlers import start, create_form, edit_form, girl_lk, pop_up_commands, admin_panel, status, g_services
from keyboards import set_commands_menu


async def start_params() -> None:
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(start.router)
    dp.include_router(create_form.router)
    dp.include_router(edit_form.router)
    dp.include_router(girl_lk.router)
    dp.include_router(admin_panel.router)
    dp.include_router(status.router)
    dp.include_router(g_services.router)
    dp.include_router(pop_up_commands.router)
    # dp.include_router(unknown_command.router)

    # dp.message.middleware(AlbumsMiddleware(5))
    logger.info('Bot started')

    # Регистрируем меню команд
    await set_commands_menu(aiogram_bot)

    # инициализирем БД
    await db.db_start()

    # Пропускаем накопившиеся апдейты и запускаем polling
    await aiogram_bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(aiogram_bot)


async def main():
    task1 = asyncio.create_task(start_params())
    await asyncio.gather(task1)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning('Bot stopped')
    except Exception as e:
        logger.error(e)

