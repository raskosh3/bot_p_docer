from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import logging
from aiogram.types import FSInputFile
from keyboards import get_categories_keyboard, get_products_keyboard, get_product_keyboard
from config import Config

router = Router()
logger = logging.getLogger(__name__)


class CatalogStates(StatesGroup):
    viewing_categories = State()
    viewing_products = State()
    viewing_product = State()


@router.message(F.text == "🍰 Каталог")
async def show_categories(message: Message, state: FSMContext):
    await state.set_state(CatalogStates.viewing_categories)
    text = "🏪 Выберите категорию продукции:"
    await message.answer(text, reply_markup=get_categories_keyboard())


@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CatalogStates.viewing_categories)
    text = "🏪 Выберите категорию продукции:"
    await callback.message.edit_text(text, reply_markup=get_categories_keyboard())
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_products(callback: CallbackQuery, state: FSMContext):
    try:
        category = callback.data.split("_")[1]
        await state.set_state(CatalogStates.viewing_products)
        await state.update_data(current_category=category)

        products = Config.PRODUCTS.get(category, {})
        category_name = "🥧 Пироги" if category == "пироги" else "🥞 Блины"

        text = f"{category_name} - доступные позиции:"
        await callback.message.edit_text(text, reply_markup=get_products_keyboard(category, products))
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в show_products: {e}")
        await callback.answer("❌ Ошибка при загрузке категории", show_alert=True)


@router.callback_query(F.data.startswith("back_to_products_"))
async def back_to_products(callback: CallbackQuery, state: FSMContext):
    try:
        category = callback.data.split("_")[3]
        await state.set_state(CatalogStates.viewing_products)

        products = Config.PRODUCTS.get(category, {})
        category_name = "🥧 Пироги" if category == "пироги" else "🥞 Блины"

        text = f"{category_name} - доступные позиции:"
        await callback.message.edit_text(text, reply_markup=get_products_keyboard(category, products))
        await callback.answer()
    except Exception as e:
        logger.error(f"Ошибка в back_to_products: {e}")
        await callback.answer("❌ Ошибка", show_alert=True)


@router.callback_query(F.data.startswith("product_"))
async def show_product(callback: CallbackQuery, state: FSMContext):
    try:
        _, category, product_key = callback.data.split("_", 2)
        await state.set_state(CatalogStates.viewing_product)

        product = Config.PRODUCTS[category][product_key]

        text = f"""
🍰 {product['name']}

📝 {product['description']}
💰 Цена: {product['price']} руб.

Выберите действие:
        """

        await callback.message.delete()
        await callback.message.answer(
            text=text,
            reply_markup=get_product_keyboard(category, product_key)
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в show_product: {e}")
        await callback.answer("❌ Произошла ошибка при загрузке товара", show_alert=True)