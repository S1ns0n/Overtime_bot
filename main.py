import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import Config
from bot.api_client import APIClient
from bot.middlewares.auth_middleware import AuthMiddleware

from bot.handlers import common, auth, employee_handler, admin_handler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Главная функция"""
    # Загружаем конфигурацию



    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    api_client = APIClient(Config.API_URL)
    await api_client.create_session()

    # Регистрируем middleware
    auth_middleware = AuthMiddleware(api_client)
    dp.message.middleware(auth_middleware)
    dp.callback_query.middleware(auth_middleware)

    # Регистрируем роутеры
    dp.include_router(auth.router)
    dp.include_router(employee_handler.router)
    dp.include_router(admin_handler.router)
    dp.include_router(common.router)

    # Добавляем api_client в контекст для всех хендлеров
    dp.workflow_data.update(api_client=api_client)

    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await api_client.close_session()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
