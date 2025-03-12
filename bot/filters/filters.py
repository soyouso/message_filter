from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from bot.db import chats

filter_router = Router()


class NotNeededMessages(BaseFilter):
    async def __call__(self, message: Message, db_engine: AsyncEngine):
        print(message.model_dump_json(indent=4, exclude_none=True, exclude_defaults=True))
        stmt = select(chats.c.banned_words).select_from(chats).where(chats.c.chat_id == message.chat.id)
        async with db_engine.connect() as conn:
            res = await conn.execute(stmt)
            a = list(res)
        if a:
            if a[0][0]:
                return any(x in message.text.split() for x in a[0][0].split())



