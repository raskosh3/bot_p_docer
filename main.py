import asyncio
import logging
import sys
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

# Загрузка .env файла
from dotenv import load_dotenv
load_dotenv()

# Импортируем обработчики
from handlers.start import router as start_router
from handlers.catalog import router as catalog_router
from handlers.cart import router as cart_router
from handlers.order import router as order_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("🚀 Запуск бота...")
        
        # Получаем токен
        BOT_TOKEN = os.getenv('BOT_TOKEN')
        logger.info(f"🔑 Токен: {BOT_TOKEN[:10]}...")
        
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN не установлен!")
            return
        
        # Создаем HTTP API сервер
        http_api = TelegramAPIServer.from_base('http://api.telegram.org')
        
        # Создаем сессию с HTTP API
        session = AiohttpSession(api=http_api)
        
        # Инициализация бота с HTTP сессией
        bot = Bot(token=BOT_TOKEN, session=session)
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация роутеров
        dp.include_router(start_router)
        dp.include_router(catalog_router)
        dp.include_router(cart_router)
        dp.include_router(order_router)

        # Удаляем webhook
        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("✅ Бот запущен и готов к работе!")
        
        # Запускаем поллинг
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка при запуске бота: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'bot' in locals():
            await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()