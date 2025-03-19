from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram_dialog.widgets.input import MessageInput, ManagedTextInput
from aiogram_dialog.widgets.kbd import Button, Select, Radio
from aiogram_dialog import DialogManager
from aiogram_dialog import ShowMode
from fluentogram import TranslatorHub, TranslatorRunner
from sqlalchemy import update

from .states import FirstDialogSG
from sqlalchemy import select, delete
from sqlalchemy.dialects.postgresql import insert
from bot.db import words, users, chats, banned

start_dialog_router = Router()


async def radio_lang_state_changed(callback: CallbackQuery, widget: Radio, dialog_manager: DialogManager, item_id: str):
    hub: TranslatorHub = dialog_manager.middleware_data['_translator_hub']
    dialog_manager.middleware_data['i18n'] = hub.get_translator_by_locale(locale=item_id)
    stmt_update = update(users).where(users.c.telegram_id == callback.from_user.id).values(language=item_id)
    await dialog_manager.middleware_data['connection'].execute(stmt_update)
    await dialog_manager.middleware_data['connection'].commit()


async def chat_choice(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager, item_id: str):
    dialog_manager.dialog_data['chat'] = int(item_id)
    stmt = select(chats.c.chat_title).select_from(chats).where(chats.c.telegram_id == callback.from_user.id,
                                                               chats.c.chat_id == int(item_id))
    chat_name = list(await dialog_manager.middleware_data['connection'].execute(stmt))[0][0]
    dialog_manager.dialog_data['chat_name'] = chat_name
    await dialog_manager.switch_to(state=FirstDialogSG.chat_actions)


async def ban_word_choice(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager,
                          item_id: str):
    stmt = delete(words).where(words.c.id == int(item_id))
    await dialog_manager.middleware_data['connection'].execute(stmt)
    await dialog_manager.middleware_data['connection'].commit()
    await dialog_manager.switch_to(state=FirstDialogSG.ban_words_list)


async def unban_user(callback: CallbackQuery, widget: Select, dialog_manager: DialogManager,
                          item_id: str):
    stmt = delete(banned).where(banned.c.banned_id == int(item_id))
    await dialog_manager.middleware_data['connection'].execute(stmt)
    await dialog_manager.middleware_data['connection'].commit()
    await callback.bot.unban_chat_member(chat_id=dialog_manager.dialog_data['chat'], user_id=int(item_id))
    await dialog_manager.switch_to(state=FirstDialogSG.banned_ids_list)


def check_correct_word(text: str) -> str:
    if len(text.split()) == 0:
        raise ValueError
    return text


def check_correct_ban_time(text: str) -> str:
    if all(i.isdigit() for i in text) and 1 <= int(text) <= 525000:
        return text
    raise ValueError


async def correct_text(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    dialog_manager.dialog_data['banned_words'] = text
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(i18n.words.written())
    dialog_manager.show_mode = ShowMode.AUTO
    await dialog_manager.switch_to(state=FirstDialogSG.choose_punishment)


async def correct_ban_time_input(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        text: str) -> None:
    dialog_manager.dialog_data['ban_time'] = int(text)
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    await message.answer(i18n.ban.time.written())
    dialog_manager.show_mode = ShowMode.AUTO
    await dialog_manager.switch_to(state=FirstDialogSG.final_confirm)


async def error_time_text(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    await message.answer(i18n.error.time.text())


async def error_words_text(
        message: Message,
        widget: ManagedTextInput,
        dialog_manager: DialogManager,
        error: ValueError) -> None:
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    await message.answer(i18n.error.words.text())


async def no_text(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    i18n: TranslatorRunner = dialog_manager.middleware_data['i18n']
    await message.answer(i18n.no.text())


async def choose_punish(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['punishment'] = callback.data
    dialog_manager.dialog_data['ban_time'] = 0


async def choose_user_ban_time(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['ban_time'] = int(callback.data)
    print(dialog_manager.dialog_data['ban_time'])


async def final_confirm(callback: CallbackQuery, button: Button, dialog_manager: DialogManager):
    stmt = insert(words).values(
        chat_id=dialog_manager.dialog_data['chat'],
        banned_words=dialog_manager.dialog_data['banned_words'],
        punishment=dialog_manager.dialog_data['punishment'],
        ban_time=dialog_manager.dialog_data['ban_time']
    )
    await dialog_manager.middleware_data['connection'].execute(stmt)
    await dialog_manager.middleware_data['connection'].commit()