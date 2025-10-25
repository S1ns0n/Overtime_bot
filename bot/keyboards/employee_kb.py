from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_employee_menu() -> ReplyKeyboardMarkup:
    """Главное меню сотрудника"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📊 Мои действия"),
        KeyboardButton(text="⏰ Мои часы")
    )
    builder.row(
        KeyboardButton(text="📅 Мои выходные"),
        KeyboardButton(text="👤 Профиль")
    )
    return builder.as_markup(resize_keyboard=True)

def get_profile_menu() -> ReplyKeyboardMarkup:
    """Меню профиля"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="🚪 Выйти из профиля"))
    builder.row(KeyboardButton(text="◀️ Назад"))
    return builder.as_markup(resize_keyboard=True)

def get_days_off_inline(actions: list) -> InlineKeyboardMarkup:
    """Инлайн клавиатура с выходными днями"""
    builder = InlineKeyboardBuilder()
    for action in actions:
        builder.row(InlineKeyboardButton(
            text=f"📅 {action['date_action']} ({action['action_type_name']})",
            callback_data=f"document_{action['action_id']}"
        ))
    return builder.as_markup()
