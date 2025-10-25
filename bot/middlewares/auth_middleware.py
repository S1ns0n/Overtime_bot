from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации"""

    def __init__(self, api_client):
        self.api_client = api_client
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        # Получаем user из Message или CallbackQuery
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user
        else:
            return await handler(event, data)

        # Проверяем авторизацию
        employee = await self.api_client.get_employee_by_tg_id(user.id)

        # Добавляем данные в контекст
        data["employee"] = employee
        data["is_authorized"] = employee is not None
        data["is_admin"] = employee.get("role_id") == 1 if employee else False

        return await handler(event, data)
