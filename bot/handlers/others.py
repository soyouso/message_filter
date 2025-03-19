from aiogram import Router, F, Bot
from aiogram.types import Message, ChatMemberUpdated
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncEngine
from bot.db import chats, words, banned
from bot.filters import NotNeededMessages
from datetime import timedelta


others_router = Router()


@others_router.my_chat_member()
async def add_to_chat(my_chat_member: ChatMemberUpdated, db_engine: AsyncEngine):
    if len(my_chat_member.model_dump(exclude_none=True, exclude_defaults=True)["new_chat_member"]) == 2:
        stmt = delete(chats).where(chats.c.chat_id == my_chat_member.chat.id,
                                    chats.c.telegram_id == my_chat_member.from_user.id)
    else:
        stmt = insert(chats).values(
            telegram_id=my_chat_member.from_user.id,
            chat_id=my_chat_member.chat.id,
            chat_title=my_chat_member.chat.title
        )

    async with db_engine.connect() as conn:
        await conn.execute(stmt)
        await conn.commit()


@others_router.message(F.text, NotNeededMessages())
async def handler_for_banned_words(message: Message, bot: Bot, db_engine: AsyncEngine):
    stmt_select = select(words.c.punishment, words.c.ban_time).select_from(words).where(words.c.chat_id == message.chat.id)
    stmt_insert = insert(banned).values(
        chat_id=message.chat.id,
        banned_id=message.from_user.id,
        banned_name=message.from_user.last_name if message.from_user.last_name else message.from_user.first_name
    )
    async with db_engine.connect() as conn:
        res = list(await conn.execute(stmt_select))
        punishment, ban_time = str(res[0][0]), int(res[0][1])
    await message.delete()
    if punishment == 'ban_user':
        await bot.ban_chat_member(chat_id=message.chat.id, user_id=message.from_user.id, until_date=timedelta(minutes=ban_time))
        async with db_engine.connect() as conn:
            await conn.execute(stmt_insert)
            await conn.commit()
