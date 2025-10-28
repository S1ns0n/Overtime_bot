import os

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from datetime import datetime
from collections import defaultdict
import tempfile
from bot.keyboards.employee_kb import get_days_off_inline

router = Router()


@router.message(F.text == "📊 Мои действия")
async def show_my_actions(message: Message, employee: dict = None, api_client=None):
    """Показать все действия сотрудника"""
    if not employee:
        await message.answer("❌ Вы не авторизованы. Используйте /start")
        return

    actions = await api_client.get_employee_actions(employee["employee_id"])

    if not actions:
        await message.answer("📊 У вас пока нет записей о действиях.")
        return

    # Группируем по месяцам
    actions_by_month = defaultdict(list)
    for action in actions:
        date = datetime.strptime(action["date_action"], "%Y-%m-%d")
        month_key = date.strftime("%Y-%m")
        actions_by_month[month_key].append(action)

    response = "📊 <b>Ваши действия:</b>\n\n"

    for month, month_actions in sorted(actions_by_month.items(), reverse=True):
        month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
        response += f"<b>{month_name}</b>\n"

        for action in sorted(month_actions, key=lambda x: x["date_action"], reverse=True):
            response += (
                f"  📅 {action['date_action']}\n"
                f"  📝 {action['action_type_name']}\n"
                f"  ⏰ {action['hours']} ч.\n\n"
            )

    await message.answer(response, parse_mode="HTML")


@router.message(F.text == "⏰ Мои часы")
async def show_my_hours(message: Message, employee: dict = None, api_client=None):
    """Показать информацию о часах"""
    if not employee:
        await message.answer("❌ Вы не авторизованы. Используйте /start")
        return

    actions = await api_client.get_employee_actions(employee["employee_id"])

    # Подсчет переработанных часов за текущий месяц
    current_month = datetime.now().strftime("%Y-%m")
    month_hours = 0

    if actions:
        for action in actions:
            action_date = datetime.strptime(action["date_action"], "%Y-%m-%d")
            if action_date.strftime("%Y-%m") == current_month:
                month_hours += action["hours"]

    idle_hours = employee.get("idle_hours", 0)

    response = (
        f"⏰ <b>Информация о часах</b>\n\n"
        f"📅 Переработано в этом месяце: <b>{month_hours}</b> ч.\n"
        f"💤 Неиспользованных часов: <b>{idle_hours}</b> ч.\n\n"
        f"ℹ️ Неиспользованные часы можно использовать для оформления выходных дней."
    )

    await message.answer(response, parse_mode="HTML")


@router.message(F.text == "📅 Мои выходные")
async def show_days_off(message: Message, employee: dict = None, api_client=None):
    """Показать выходные дни (где actiontype = выходной)"""
    if not employee:
        await message.answer("❌ Вы не авторизованы. Используйте /start")
        return

    actions = await api_client.get_employee_actions(employee["employee_id"])

    if not actions:
        await message.answer("📅 У вас пока нет выходных дней.")
        return

    # Фильтруем только выходные (предполагаем что actiontype_id = 2 это выходной)
    days_off = [a for a in actions if "выходной" in a["action_type_name"].lower() or a["actiontype_id"] == 1]

    if not days_off:
        await message.answer("📅 У вас пока нет оформленных выходных дней.")
        return

    response = "📅 <b>Ваши выходные дни:</b>\n\n"
    response += "Нажмите на дату, чтобы запросить справку о выходном дне:\n\n"

    keyboard = get_days_off_inline(days_off)

    await message.answer(response, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("document_"))
async def request_document(callback: CallbackQuery, api_client):
    action_id = int(callback.data.split("_")[1])
    await callback.answer("📄 Формирование справки...")

    file_bytes = await api_client.get_holiday_document_by_action(action_id)
    if not file_bytes:
        await callback.message.answer("❌ Ошибка при получении документа.")
        return

    with tempfile.NamedTemporaryFile(suffix='.doc', delete=False) as tmp:
        tmp.write(file_bytes)
        temp_filepath = tmp.name

    try:
        input_doc = FSInputFile(temp_filepath, filename=f"holiday_document_{action_id}.doc")
        await callback.message.answer_document(document=input_doc)
    finally:
        if os.path.exists(temp_filepath):
            os.unlink(temp_filepath)