from aiogram.fsm.state import State, StatesGroup


class FirstDialogSG(StatesGroup):
    first = State()
    second = State()
    third = State()
    fourth = State()
    fifth = State()