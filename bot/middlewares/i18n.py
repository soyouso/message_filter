from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from fluentogram import TranslatorHub
from sqlalchemy import select
from bot.db import users


class TranslatorRunnerMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:

        user: User = data.get('event_from_user')

        if user is None:
            return await handler(event, data)

        hub: TranslatorHub = data.get('_translator_hub')
        stmt = select(users.c.language).select_from(users).where(users.c.telegram_id == user.id)
        lang = list(await data['connection'].execute(stmt))
        print(user.language_code)
        if lang:
            data['i18n'] = hub.get_translator_by_locale(locale=lang[0][0])
            print(1)
        else:
            print(2)
            data['i18n'] = hub.get_translator_by_locale(locale=user.language_code)
        return await handler(event, data)

