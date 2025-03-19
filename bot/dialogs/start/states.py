from aiogram.fsm.state import State, StatesGroup


class FirstDialogSG(StatesGroup):
    start = State()
    choose_lang = State()
    choose_chat = State()
    chat_actions = State()
    ban_words_list = State()
    banned_ids_list = State()
    choose_user_ban_time = State()
    input_ban_words = State()
    choose_punishment = State()
    final_confirm = State()