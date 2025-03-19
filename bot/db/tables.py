from sqlalchemy import MetaData, Table, Column, BIGINT, String, TIMESTAMP



metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('telegram_id', BIGINT, primary_key=True),
    Column('first_name', String),
    Column('last_name', String),
    Column('language', String),
    Column('started_at', TIMESTAMP)
)


chats = Table(
    'chats',
    metadata,
    Column('id', BIGINT, primary_key=True, autoincrement=True),
    Column('telegram_id', BIGINT),
    Column('chat_id', BIGINT),
    Column('chat_title', String)
)


words = Table(
    'words',
    metadata,
    Column('id', BIGINT, primary_key=True, autoincrement=True),
    Column('chat_id', BIGINT),
    Column('banned_words', String),
    Column('punishment', String),
    Column('ban_time', BIGINT, default=0)
)


banned = Table(
    'banned',
    metadata,
    Column('id', BIGINT, primary_key=True, autoincrement=True),
    Column('chat_id', BIGINT),
    Column('banned_id', BIGINT),
    Column('banned_name', String)
)