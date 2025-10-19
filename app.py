import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Импортируем ваши обработчики
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

async def health_check(request):
    """Health check endpoint"""
    return web.Response(text="✅ Bakery Bot is running!")

async def start_web_server():
    """Запуск веб-сервера - В ПЕРВУЮ ОЧЕРЕДЬ"""
    app = web.Application()
    app.router.add_get('/', health_check)
    app.router.add_get('/health', health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    
    logger.info(f"🌐 Web server started on port {port}")
    return runner

async def start_telegram_bot():
    """Запуск Telegram бота - во вторую очередь"""
    try:
        logger.info("🚀 Starting Telegram bot...")
        
        bot = Bot(token=os.getenv('BOT_TOKEN'))
        dp = Dispatcher(storage=MemoryStorage())

        # Регистрация роутеров
        dp.include_router(start_router)
        dp.include_router(catalog_router)
        dp.include_router(cart_router)
        dp.include_router(order_router)

        await bot.delete_webhook(drop_pending_updates=True)
        
        logger.info("✅ Telegram bot started!")
        
        # Запускаем поллинг (блокирующая операция)
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Bot error: {e}")
        raise

async def main():
    """Основная функция"""
    # 1. Сначала запускаем веб-сервер (важно для Render!)
    runner = await start_web_server()
    
    # 2. Затем запускаем бота
    try:
        await start_telegram_bot()
    except Exception as e:
        logger.error(f"Bot failed: {e}")
    finally:
        # Корректное завершение
        await runner.cleanup()

if __name__ == "__main__":
    # Проверяем переменные
    if not os.getenv('BOT_TOKEN'):
        logger.error("❌ BOT_TOKEN not set!")
        exit(1)
        
    # Запускаем
    asyncio.run(main())
