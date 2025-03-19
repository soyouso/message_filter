from typing import Callable, Awaitable, Dict, Any, cast

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message
from cachetools import TTLCache
from sqlalchemy.dialects.postgresql import insert
from bot.db import users


class TrackAllUsersMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.cache = TTLCache(
            maxsize=1000,
            ttl=60 * 60 * 6,
        )

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        event = cast(Message, event)
        user_id = event.from_user.id

        if user_id not in self.cache:
            stmt = insert(users).values(
                telegram_id=event.from_user.id,
                first_name=event.from_user.first_name,
                last_name=event.from_user.last_name,
                language=event.from_user.language_code,
                started_at=event.date.now()
            )
            update_stmt = stmt.on_conflict_do_update(
                index_elements=['telegram_id'],
                set_={
                    'first_name': event.from_user.first_name,
                    'last_name': event.from_user.last_name
                }
            )
            await data['connection'].execute(update_stmt)
            await data['connection'].commit()
            self.cache[user_id] = None
        return await handler(event, data)