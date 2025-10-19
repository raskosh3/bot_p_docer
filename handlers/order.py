from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import Database
from config import Config
from keyboards import get_main_keyboard

router = Router()
db = Database()


class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_phone = State()


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    cart_items = db.get_user_cart(callback.from_user.id)

    if not cart_items:
        await callback.answer("❌ Корзина пуста!")
        return

    await state.set_state(OrderStates.waiting_for_name)
    await callback.message.answer("📝 Для оформления заказа нам нужна ваша контактная информация.\n\nВведите ваше имя:")
    await callback.answer()


@router.message(OrderStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderStates.waiting_for_address)
    await message.answer("🏠 Введите ваш адрес доставки:")


@router.message(OrderStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.waiting_for_phone)
    await message.answer("📞 Введите ваш номер телефона:")


@router.message(OrderStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    try:
        await state.update_data(phone=message.text)
        user_data = await state.get_data()

        # Сохраняем информацию о пользователе
        db.update_user_info(message.from_user.id, user_data)

        # Формируем заказ
        cart_items = db.get_user_cart(message.from_user.id)
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Сообщение для администратора
        order_text = "🆕 НОВЫЙ ЗАКАЗ!\n\n"
        order_text += f"👤 Клиент: {user_data['name']}\n"
        order_text += f"🏠 Адрес: {user_data['address']}\n"
        order_text += f"📞 Телефон: {user_data['phone']}\n"
        order_text += f"🆔 ID пользователя: {message.from_user.id}\n"
        order_text += f"👤 Username: @{message.from_user.username if message.from_user.username else 'нет'}\n\n"
        order_text += "📦 Состав заказа:\n"

        for item in cart_items:
            item_total = item['price'] * item['quantity']
            order_text += f"• {item['name']} - {item['quantity']} x {item['price']} руб. = {item_total} руб.\n"

        order_text += f"\n💰 Итого: {total} руб."

        # Отправляем администратору
        if Config.ADMIN_ID:
            await bot.send_message(Config.ADMIN_ID, order_text)
        else:
            # Если ADMIN_ID не указан, логируем заказ
            from main import logger
            logger.info(f"Новый заказ (ADMIN_ID не указан): {order_text}")

        # Сообщение пользователю
        user_order_text = "✅ Ваш заказ принят!\n\n"
        user_order_text += f"👤 Имя: {user_data['name']}\n"
        user_order_text += f"🏠 Адрес: {user_data['address']}\n"
        user_order_text += f"📞 Телефон: {user_data['phone']}\n\n"
        user_order_text += "📦 Ваш заказ:\n"

        for item in cart_items:
            item_total = item['price'] * item['quantity']
            user_order_text += f"• {item['name']} - {item['quantity']} x {item['price']} руб. = {item_total} руб.\n"

        user_order_text += f"\n💰 Итого: {total} руб.\n\n"
        user_order_text += "⏳ Мы свяжемся с вами в ближайшее время для подтверждения заказа!"

        # Очищаем корзину
        db.clear_cart(message.from_user.id)

        await message.answer(user_order_text, reply_markup=get_main_keyboard())
        await state.clear()

    except Exception as e:
        await message.answer("❌ Произошла ошибка при оформлении заказа. Попробуйте позже.",
                             reply_markup=get_main_keyboard())
        await state.clear()