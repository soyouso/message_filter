from aiogram import Router
from aiogram.types import Message
from aiogram.filters import BaseFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from bot.db import words

filter_router = Router()


class NotNeededMessages(BaseFilter):
    async def __call__(self, message: Message, db_engine: AsyncEngine):
        stmt = select(words.c.banned_words).select_from(words).where(words.c.chat_id == message.chat.id)
        async with db_engine.connect() as conn:
            res = await conn.execute(stmt)
            a = list(res)
        if a:
            #if a[0][0]:
            return any([[y in message.text.split() for y in x[0].split()][0] for x in a])



