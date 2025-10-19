from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile  # Изменили импорт
from aiogram.filters import CommandStart
import os
import logging

from keyboards import get_main_keyboard, get_back_keyboard
from config import Config

router = Router()
logger = logging.getLogger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды /start"""

    welcome_text = """🍰Вас приветствует пекарня «Кулинарный дом Белецких». Я шеф Ирина Белецкая!🥖 

Готовим по нашим семейным рецептам, с любовью. Так что расскажите, душа просит сегодня сладенького или сытного? 
Воздушных блинов, румяных пирогов или нежных сырников? Жду у печи!

Здесь вы можете:
• 🍰 Посмотреть наш каталог продукции
• ℹ️ Узнать больше о нашей пекарне
• 🛒 Сформировать заказ

Выберите нужный раздел в меню ниже👇"""

    # Путь к изображению
    image_path = "C:\\Users\\Yefom1t\\PycharmProjects\\bot_bot\\pirog5\\images\\welcome.jpg"

    logger.info(f"Команда /start от {message.from_user.id}")
    logger.info(f"Пытаюсь отправить изображение: {image_path}")
    logger.info(f"Файл существует: {os.path.exists(image_path)}")

    try:
        # Пытаемся отправить фото
        if os.path.exists(image_path):
            logger.info("Файл найден, создаю FSInputFile...")
            photo = FSInputFile(image_path)  # Используем FSInputFile
            logger.info("FSInputFile создан, отправляю фото...")

            await message.answer_photo(
                photo=photo,
                caption=welcome_text,
                reply_markup=get_main_keyboard()
            )
            logger.info("✅ Фото отправлено успешно!")
        else:
            logger.warning("Файл не найден, отправляю только текст")
            await message.answer(welcome_text, reply_markup=get_main_keyboard())

    except Exception as e:
        logger.error(f"❌ Ошибка при отправке фото: {e}")
        logger.info("Отправляю только текст из-за ошибки...")
        await message.answer(welcome_text, reply_markup=get_main_keyboard())


@router.message(F.text == "🤖 Заказать бота")
async def about_bot(message: Message):
    bot_info = """🤖 Бизнес Бот Про — мы создаём ботов, которые реально работают: продают, обучают, консультируют и управляют процессами без вашего участия.

🧩 Всё в привычном Telegram, без сложных систем и лишних настроек.

🚀 Запросите консультацию, расскажите задачу или любую идею — от заявок до учёта персонала, мы покажем, как это автоматизировать."""
    await message.answer(bot_info, reply_markup=get_back_keyboard())


@router.message(F.text == "ℹ️ О нас")
async def about_bakery(message: Message):
    about_text = """🏪 О нашей пекарне

Мы - семейная пекарня с многолетними традициями. 
Используем только натуральные ингредиенты и готовим с любовью!

📍 Наш адрес: 
🕒 Время работы: 8:00 - 20:00
📞 Телефон:

Мы предлагаем:
• Свежую выпечку ежедневно
• Качественные продукты
• Быструю доставку
• Приятные цены"""
    await message.answer(about_text, reply_markup=get_back_keyboard())


@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text("Главное меню:", reply_markup=None)
    await callback.message.answer("Выберите раздел:", reply_markup=get_main_keyboard())
    await callback.answer()