from aiogram import Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from bot.states.forms import AuthForm
from bot.keyboards.employee_kb import get_employee_menu, get_profile_menu


router = Router()
COMMANDS = ["/start","/hel["]

@router.message(CommandStart(), StateFilter(default_state))
async def cmd_start(message: Message, state: FSMContext, employee: dict = None, api_client=None):
    """Команда /start"""
    if employee:
        # Пользователь уже авторизован
        role_name = "Администратор" if employee["role_id"] == 1 else "Сотрудник"

        await message.answer(
            f"👋 С возвращением, {employee['name']} {employee['patronymic']}!\n"
            f"Роль: {role_name}",
            reply_markup=get_employee_menu()
        )
    else:
        # Запрашиваем авторизацию
        await message.answer(
            "👋 Добро пожаловать в систему учета переработок!\n\n"
            "🔐 Для начала работы необходимо авторизоваться.\n"
            "Введите ваш логин:",
            reply_markup=ReplyKeyboardRemove()
        )
        await state.set_state(AuthForm.login)


@router.message(AuthForm.login)
async def process_login(message: Message, state: FSMContext):
    """Обработка ввода логина"""
    if message.text.strip() in COMMANDS:
        await message.delete()
        return
    await state.update_data(login=message.text)
    await message.answer("🔑 Теперь введите пароль:")
    await state.set_state(AuthForm.password)


@router.message(AuthForm.password)
async def process_password(message: Message, state: FSMContext, api_client):
    """Обработка ввода пароля и авторизация"""
    if message.text.strip() in COMMANDS:
        await message.delete()
        return
    data = await state.get_data()
    login = data.get("login")
    password = message.text

    # Удаляем сообщение с паролем для безопасности
    await message.delete()
    print(f"ЛОГИН И ПАРЛ: {login}, {password}")
    # Пытаемся авторизоваться
    employee = await api_client.login(login, password)

    if not employee:
        await message.answer(
            "❌ Неверный логин или пароль.\n"
            "Попробуйте снова. Введите логин:"
        )
        await state.set_state(AuthForm.login)
        return

    # Привязываем Telegram ID
    success = await api_client.link_telegram(employee["employee_id"], message.from_user.id)

    if not success:
        await message.answer("❌ Ошибка при привязке аккаунта. Попробуйте позже.")
        await state.clear()
        return

    # Успешная авторизация
    role_name = "Администратор" if employee["role_id"] == 1 else "Сотрудник"


    await message.answer(
        f"✅ Авторизация успешна!\n\n"
        f"👤 {employee['surname']} {employee['name']} {employee['patronymic']}\n"
        f"📋 Должность: {employee.get('post', {}).get('name_post', 'Не указана')}\n"
        f"🏢 Отдел: {employee.get('otdel', {}).get('name_otdel', 'Не указан')}\n"
        f"👔 Роль: {role_name}",
        reply_markup=get_profile_menu()
    )

    await state.clear()


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message, employee: dict = None):
    """Показать профиль"""
    if not employee:
        await message.answer("❌ Вы не авторизованы. Используйте /start")
        return

    role_name = "Администратор" if employee["role_id"] == 1 else "Сотрудник"

    profile_text = (
        f"👤 <b>Ваш профиль</b>\n\n"
        f"ФИО: {employee['surname']} {employee['name']} {employee['patronymic']}\n"
        f"Логин: {employee['login']}\n"
        f"Роль: {role_name}\n"
        f"Telegram ID: {employee['tg_id']}"
    )

    await message.answer(profile_text, reply_markup=get_profile_menu(), parse_mode="HTML")


@router.message(F.text == "🚪 Выйти из профиля")
async def logout(message: Message, employee: dict = None, api_client=None):
    """Выход из профиля"""
    if not employee:
        await message.answer("❌ Вы не авторизованы.")
        return

    # Отвязываем Telegram ID
    success = await api_client.unlink_telegram(employee["employee_id"])

    if success:
        await message.answer(
            "👋 Вы вышли из системы.\n"
            "Используйте /start для повторной авторизации.",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer("❌ Ошибка при выходе из системы.")


@router.message(F.text == "◀️ Назад")
async def back_to_menu(message: Message, employee: dict = None):
    """Возврат в главное меню"""
    if not employee:
        await message.answer("❌ Вы не авторизованы. Используйте /start")
        return

    await message.answer("📋 Главное меню:", reply_markup=get_employee_menu())
