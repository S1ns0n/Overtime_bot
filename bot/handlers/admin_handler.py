from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime

from bot.states.forms import OvertimeForm
from bot.keyboards.admin_kb import get_employees_inline, get_cancel_keyboard, get_admin_menu

router = Router()


@router.message(F.text == "➕ Оформить переработку")
async def start_overtime_registration(message: Message, state: FSMContext, is_admin: bool = False, api_client=None):
    """Начало оформления переработки"""
    if not is_admin:
        await message.answer("❌ Эта функция доступна только администраторам.")
        return

    # Получаем список всех сотрудников
    employees = await api_client.get_all_employees()

    if not employees:
        await message.answer("❌ Не удалось загрузить список сотрудников.")
        return

    keyboard = get_employees_inline(employees)

    await message.answer(
        "👥 <b>Выберите сотрудника для оформления переработки:</b>",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    await state.set_state(OvertimeForm.employee)


@router.callback_query(OvertimeForm.employee, F.data.startswith("emp_"))
async def select_employee(callback: CallbackQuery, state: FSMContext):
    """Выбор сотрудника"""
    employee_id = int(callback.data.split("_")[1])

    await state.update_data(employee_id=employee_id)
    await callback.message.delete()

    await callback.message.answer(
        "📅 <b>Введите дату переработки</b>\n\n"
        "Формат: ДД.ММ.ГГГГ (например, 25.10.2025)\n"
        "Или просто ДД.ММ для текущего года",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )

    await state.set_state(OvertimeForm.date)
    await callback.answer()


@router.callback_query(OvertimeForm.employee, F.data == "cancel")
async def cancel_overtime(callback: CallbackQuery, state: FSMContext, employee: dict = None):
    """Отмена оформления"""
    await state.clear()
    await callback.message.delete()

    keyboard = get_admin_menu() if employee and employee["role_id"] == 1 else None
    await callback.message.answer("❌ Оформление переработки отменено.", reply_markup=keyboard)
    await callback.answer()


@router.message(OvertimeForm.date, F.text == "❌ Отмена")
async def cancel_overtime_message(message: Message, state: FSMContext, employee: dict = None):
    """Отмена через кнопку"""
    await state.clear()

    keyboard = get_admin_menu() if employee and employee["role_id"] == 1 else None
    await message.answer("❌ Оформление переработки отменено.", reply_markup=keyboard)


@router.message(OvertimeForm.date)
async def process_date(message: Message, state: FSMContext):
    """Обработка даты"""
    date_str = message.text.strip()

    try:
        # Пробуем разные форматы
        if len(date_str.split(".")) == 2:
            # Формат ДД.ММ (добавляем текущий год)
            date = datetime.strptime(f"{date_str}.{datetime.now().year}", "%d.%m.%Y")
        else:
            # Формат ДД.ММ.ГГГГ
            date = datetime.strptime(date_str, "%d.%m.%Y")

        # Проверяем что дата не в будущем
        if date > datetime.now():
            await message.answer("❌ Дата не может быть в будущем. Попробуйте снова:")
            return

        formatted_date = date.strftime("%Y-%m-%d")
        await state.update_data(date=formatted_date)

        await message.answer(
            "⏰ <b>Введите количество часов переработки</b>\n\n"
            "⚠️ Максимум 4 часа за один раз\n"
            "Введите число от 1 до 4:",
            parse_mode="HTML"
        )

        await state.set_state(OvertimeForm.hours)

    except ValueError:
        await message.answer(
            "❌ Неверный формат даты.\n"
            "Используйте формат ДД.ММ.ГГГГ или ДД.ММ\n"
            "Например: 25.10.2025 или 25.10"
        )


@router.message(OvertimeForm.hours, F.text == "❌ Отмена")
async def cancel_hours(message: Message, state: FSMContext, employee: dict = None):
    """Отмена на этапе ввода часов"""
    await state.clear()

    keyboard = get_admin_menu() if employee and employee["role_id"] == 1 else None
    await message.answer("❌ Оформление переработки отменено.", reply_markup=keyboard)


@router.message(OvertimeForm.hours)
async def process_hours(message: Message, state: FSMContext, api_client, employee: dict = None):
    """Обработка количества часов и создание записи"""
    try:
        hours = int(message.text.strip())

        if hours < 1 or hours > 4:
            await message.answer("❌ Количество часов должно быть от 1 до 4. Попробуйте снова:")
            return

        # Получаем данные из состояния
        data = await state.get_data()
        employee_id = data["employee_id"]
        date = data["date"]

        # Создаем запись о переработке
        result = await api_client.create_overtime(
            employee_id=employee_id,
            hours=hours,
            date=date,
            actiontype_id=1  # Предполагаем что 1 = переработка
        )

        if result:
            # Получаем информацию о сотруднике для красивого вывода
            emp_info = await api_client.get_employee_info(employee_id)
            emp_name = f"{emp_info['surname']} {emp_info['name']}" if emp_info else f"ID {employee_id}"

            keyboard = get_admin_menu() if employee and employee["role_id"] == 1 else None

            await message.answer(
                f"✅ <b>Переработка успешно оформлена!</b>\n\n"
                f"👤 Сотрудник: {emp_name}\n"
                f"📅 Дата: {datetime.strptime(date, '%Y-%m-%d').strftime('%d.%m.%Y')}\n"
                f"⏰ Часов: {hours}",
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await message.answer(
                "❌ Ошибка при создании записи о переработке.\n"
                "Попробуйте позже."
            )

        await state.clear()

    except ValueError:
        await message.answer("❌ Введите целое число от 1 до 4:")
