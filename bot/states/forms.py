from aiogram.fsm.state import State, StatesGroup

class AuthForm(StatesGroup):
    login = State()
    password = State()

class OvertimeForm(StatesGroup):
    employee = State()
    date = State()
    hours = State()

class DocumentRequest(StatesGroup):
    select_date = State()