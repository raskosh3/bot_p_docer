from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="🍰 Каталог"))
    builder.add(KeyboardButton(text="ℹ️ О нас"))
    builder.add(KeyboardButton(text="🛒 Корзина"))
    builder.add(KeyboardButton(text="🤖 Заказать бота"))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


def get_categories_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🥧 Пироги", callback_data="category_пироги"))
    builder.add(InlineKeyboardButton(text="🥞 Блины", callback_data="category_блины"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    builder.adjust(2)
    return builder.as_markup()


def get_products_keyboard(category: str, products: dict):
    builder = InlineKeyboardBuilder()
    for product_key in products.keys():
        product_name = products[product_key]['name']
        builder.add(InlineKeyboardButton(
            text=product_name,
            callback_data=f"product_{category}_{product_key}"
        ))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_categories"))
    builder.adjust(1)
    return builder.as_markup()


def get_product_keyboard(category: str, product_key: str):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(
        text="➕ Добавить в корзину",
        callback_data=f"add_to_cart_{category}_{product_key}"
    ))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"back_to_products_{category}"))
    builder.adjust(1)
    return builder.as_markup()


def get_cart_keyboard(cart_items):
    builder = InlineKeyboardBuilder()
    if cart_items:
        builder.add(InlineKeyboardButton(text="📦 Оформить заказ", callback_data="checkout"))
        builder.add(InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart"))

    for item in cart_items:
        builder.add(InlineKeyboardButton(
            text=f"❌ Удалить {item['name']}",
            callback_data=f"remove_{item['category']}_{item['product_key']}"
        ))

    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    builder.adjust(1)
    return builder.as_markup()


def get_back_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    return builder.as_markup()