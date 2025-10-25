from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("help"))
async def cmd_help(message: Message, employee: dict = None, is_admin: bool = False):
    """Команда помощи"""
    if not employee:
        await message.answer(
            "ℹ️ <b>Помощь</b>\n\n"
            "Вы не авторизованы. Используйте /start для входа в систему.",
            parse_mode="HTML"
        )
        return

    help_text = "ℹ️ <b>Доступные команды:</b>\n\n"
    help_text += "📊 Мои действия - просмотр всех действий\n"
    help_text += "⏰ Мои часы - информация о часах\n"
    help_text += "📅 Мои выходные - список выходных дней\n"
    help_text += "👤 Профиль - информация о профиле\n"

    if is_admin:
        help_text += "\n<b>Администраторские функции:</b>\n"
        help_text += "➕ Оформить переработку\n"

    await message.answer(help_text, parse_mode="HTML")
