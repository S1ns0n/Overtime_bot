import aiohttp
from typing import Optional, Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None

    async def create_session(self):
        """Создание aiohttp сессии"""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Закрытие сессии"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict[Any, Any]]:
        """Базовый метод для запросов"""
        url = f"{self.base_url}{endpoint}"
        try:
            async with self.session.request(method, url, **kwargs) as response:
                if response.status in [200, 201]:
                    return await response.json()
                elif response.status == 404:
                    return None
                else:
                    logger.error(f"API Error: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None

    # === Авторизация ===
    async def login(self, login: str, password: str) -> Optional[Dict]:
        """Авторизация по логину и паролю"""
        return await self._request("POST", "/employees/login", json={
            "login": login,
            "password": password
        })

    async def link_telegram(self, employee_id: int, tg_id: int) -> bool:
        """Привязка Telegram ID к сотруднику"""
        result = await self._request("PUT", f"/employees/{employee_id}/set_tg_id", json={
            "tg_id": tg_id
        })
        return result is not None

    async def get_employee_by_tg_id(self, tg_id: int) -> Optional[Dict]:
        """Получить сотрудника по Telegram ID"""
        return await self._request("GET", f"/employees/telegram/{tg_id}")

    async def unlink_telegram(self, employee_id: int) -> bool:
        """Отвязать Telegram ID"""
        result = await self._request("PUT", f"/employees/{employee_id}/unset_tg_id", json={
            "tg_id": None
        })
        return result is not None

    # === Действия сотрудника ===
    async def get_employee_actions(self, employee_id: int) -> Optional[List[Dict]]:
        """Получить все действия сотрудника"""
        return await self._request("GET", f"/employees/{employee_id}/actions")

    async def get_employee_info(self, employee_id: int) -> Optional[Dict]:
        """Получить информацию о сотруднике"""
        return await self._request("GET", f"/employees/{employee_id}")

    # === Администраторские функции ===
    async def get_all_employees(self) -> Optional[List[Dict]]:
        """Получить список всех сотрудников"""
        return await self._request("GET", "/employees")

    async def create_overtime(self, employee_id: int, hours: int, date: str, actiontype_id: int = 1) -> Optional[Dict]:
        """Создать запись о переработке"""
        return await self._request("POST", "/actions", json={
            "employee_id": employee_id,
            "hours": hours,
            "date_action": date,
            "actiontype_id": actiontype_id
        })

    async def get_holiday_document_by_action(self, action_id: int) -> Optional[bytes]:
        """Получить файл справки по id действия"""
        return await self._request_binary("POST", f"/documents/holiday/{action_id}")

    async def _request_binary(self, method: str, endpoint: str) -> Optional[bytes]:
        """Запрос для получения бинарных данных (файла)"""
        url = f"{self.base_url}{endpoint}"
        print(url)
        try:
            async with self.session.request(method, url) as response:
                if response.status == 200:
                    return await response.read()
                elif response.status == 404:
                    return None
                else:
                    logger.error(f"API Error: {response.status} - {await response.text()}")
                    return None
        except Exception as e:
            logger.error(f"Request error: {e}")
            return None