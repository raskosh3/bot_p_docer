from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
import logging

from keyboards import get_cart_keyboard, get_main_keyboard
from database import Database
from config import Config

router = Router()
db = Database()
logger = logging.getLogger(__name__)


@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    cart_items = db.get_user_cart(message.from_user.id)

    if not cart_items:
        await message.answer("🛒 Ваша корзина пуста", reply_markup=get_main_keyboard())
        return

    total = 0
    cart_text = "🛒 Ваша корзина:\n\n"

    for item in cart_items:
        item_total = item['price'] * item['quantity']
        total += item_total
        cart_text += f"• {item['name']}\n"
        cart_text += f"  Количество: {item['quantity']} x {item['price']} руб. = {item_total} руб.\n\n"

    cart_text += f"💰 Итого: {total} руб."

    await message.answer(cart_text, reply_markup=get_cart_keyboard(cart_items))


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    try:
        logger.info(f"Callback data: {callback.data}")

        # Разбираем callback data
        parts = callback.data.split("_")
        logger.info(f"Parts: {parts}")

        # Ожидаемый формат: add_to_cart_категория_продукт
        if len(parts) < 4:
            await callback.answer("❌ Неверный формат данных", show_alert=True)
            return

        category = parts[3]
        product_key = parts[4] if len(parts) > 4 else parts[3]

        logger.info(f"Category: {category}, Product key: {product_key}")

        # Проверяем существование категории и продукта
        if category not in Config.PRODUCTS:
            await callback.answer("❌ Категория не найдена", show_alert=True)
            return

        if product_key not in Config.PRODUCTS[category]:
            await callback.answer("❌ Продукт не найден", show_alert=True)
            return

        # Получаем информацию о продукте
        product_info = Config.PRODUCTS[category][product_key]
        logger.info(f"Product info: {product_info}")

        product_data = {
            'category': category,
            'product_key': product_key,
            'name': product_info['name'],
            'price': product_info['price'],
            'quantity': 1
        }

        db.add_to_cart(callback.from_user.id, product_data)
        await callback.answer("✅ Товар добавлен в корзину!")

    except Exception as e:
        logger.error(f"Ошибка при добавлении в корзину: {e}")
        await callback.answer("❌ Ошибка при добавлении в корзину", show_alert=True)


@router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery):
    try:
        parts = callback.data.split("_")
        if len(parts) < 3:
            await callback.answer("❌ Неверный формат данных", show_alert=True)
            return

        category = parts[1]
        product_key = parts[2]

        db.remove_from_cart(callback.from_user.id, product_key, category)

        # Обновляем сообщение корзины
        cart_items = db.get_user_cart(callback.from_user.id)

        if not cart_items:
            await callback.message.edit_text("🛒 Ваша корзина пуста")
            await callback.answer("✅ Товар удален из корзины")
            return

        total = 0
        cart_text = "🛒 Ваша корзина:\n\n"

        for item in cart_items:
            item_total = item['price'] * item['quantity']
            total += item_total
            cart_text += f"• {item['name']}\n"
            cart_text += f"  Количество: {item['quantity']} x {item['price']} руб. = {item_total} руб.\n\n"

        cart_text += f"💰 Итого: {total} руб."

        await callback.message.edit_text(cart_text, reply_markup=get_cart_keyboard(cart_items))
        await callback.answer("✅ Товар удален из корзины")

    except Exception as e:
        logger.error(f"Ошибка при удалении из корзины: {e}")
        await callback.answer("❌ Ошибка при удалении товара", show_alert=True)


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    try:
        db.clear_cart(callback.from_user.id)
        await callback.message.edit_text("🛒 Ваша корзина очищена")
        await callback.answer("✅ Корзина очищена")
    except Exception as e:
        logger.error(f"Ошибка при очистке корзины: {e}")
        await callback.answer("❌ Ошибка при очистке корзины", show_alert=True)