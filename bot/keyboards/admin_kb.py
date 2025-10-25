from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

def get_admin_menu() -> ReplyKeyboardMarkup:
    """Главное меню администратора"""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="➕ Оформить переработку"),
        KeyboardButton(text="📊 Мои действия")
    )
    builder.row(
        KeyboardButton(text="⏰ Мои часы"),
        KeyboardButton(text="📅 Мои выходные")
    )
    builder.row(KeyboardButton(text="👤 Профиль"))
    return builder.as_markup(resize_keyboard=True)

def get_employees_inline(employees: list) -> InlineKeyboardMarkup:
    """Инлайн клавиатура со списком сотрудников"""
    builder = InlineKeyboardBuilder()
    for emp in employees:
        full_name = f"{emp['surname']} {emp['name']} {emp['patronymic']}"
        builder.row(InlineKeyboardButton(
            text=full_name,
            callback_data=f"emp_{emp['employee_id']}"
        ))
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()

def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="❌ Отмена"))
    return builder.as_markup(resize_keyboard=True)
