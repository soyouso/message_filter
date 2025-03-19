from aiogram.types import User
from aiogram_dialog import DialogManager
from fluentogram import TranslatorRunner
from sqlalchemy import select
from bot.db import users, chats, words, banned


async def get_i18n(event_from_user: User, i18n: TranslatorRunner, dialog_manager: DialogManager, **kwargs):
    return {'hello_user': i18n.hello.user(),
            'select_chat': i18n.select.chat(),
            'add_bot': i18n.add.bot(),
            'change_lang': i18n.change.lang(),
            'choose_lang': i18n.choose.lang(),
            'yours_chats': i18n.yours.chats(),
            'back': i18n.back(),
            'input_words': i18n.input.words(),
            'choose_punishment': i18n.choose.punishment(),
            'delete_messages': i18n.delete.messages(),
            'ban_user': i18n.ban.user(),
            'confirm': i18n.confirm(),
            'add_ban_words': i18n.add.ban.words(),
            'remove_ban_words': i18n.remove.ban.words(),
            'show_ban_list': i18n.show.ban.list(),
            'banned_ids_list': i18n.banned.ids.list(),
            'banned_people_window': i18n.banned.people.window(),
            'your_ban_list': i18n.your.ban.list(),
            'choose_user_ban_time': i18n.choose.user.ban.time(),
            'five_min': i18n.five.min(),
            'thirty_min': i18n.thirty.min(),
            'one_hour': i18n.one.hour(),
            'one_day': i18n.one.day(),
            'seven_days': i18n.seven.days(),
            'thirty_days': i18n.thirty.days(),
            'forever': i18n.forever(),
            }


async def get_languages(dialog_manager: DialogManager, i18n: TranslatorRunner, event_from_user: User, **kwargs):
    stmt_select = select(users.c.language).select_from(users).where(users.c.telegram_id == event_from_user.id)
    selected = list(await dialog_manager.middleware_data['connection'].execute(stmt_select))[0][0]
    await dialog_manager.find('choose_lang').set_checked(selected)
    languages = [(i18n.english(), 'en'), (i18n.russian(), 'ru')]
    return {"languages": languages}


async def get_chats(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    stmt = select(chats.c.chat_title, chats.c.chat_id).select_from(chats).where(chats.c.telegram_id == event_from_user.id)
    chats_of_user = await dialog_manager.middleware_data['connection'].execute(stmt)
    return {'chats_of_user': chats_of_user}


async def get_words_ban_list(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    stmt = select(words.c.banned_words, words.c.id).select_from(words).where(words.c.chat_id == dialog_manager.dialog_data['chat'])
    words_ban_list = await dialog_manager.middleware_data['connection'].execute(stmt)
    return {'words_ban_list': words_ban_list}


async def get_users_ban_list(event_from_user: User, dialog_manager: DialogManager, **kwargs):
    stmt = select(banned.c.banned_name, banned.c.banned_id).select_from(banned).where(banned.c.chat_id == dialog_manager.dialog_data['chat'])
    users_ban_list = await dialog_manager.middleware_data['connection'].execute(stmt)
    return {'users_ban_list': users_ban_list}


async def getter_str_chat(dialog_manager: DialogManager, i18n: TranslatorRunner, **kwargs):
    return {'choose_chat_action': i18n.choose.chat.action(chat='<b>' + dialog_manager.dialog_data['chat_name'] + '</b>')}


async def getter_for_fifth(event_from_user: User, dialog_manager: DialogManager,
                           i18n: TranslatorRunner, **kwargs):
    return {'full_confirm': i18n.full.confirm(banned_words='<b>' + dialog_manager.dialog_data['banned_words'] + '</b>',
                                              punishment='<u>' + i18n.get(dialog_manager.dialog_data.get('punishment').replace('_', '-')) + '</u>')}