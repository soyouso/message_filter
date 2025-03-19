from dataclasses import dataclass
from environs import Env
from pydantic import PostgresDsn


@dataclass
class TgBot:
    token: str


@dataclass
class Db:
    dsn: PostgresDsn
    is_echo: bool


@dataclass
class NatsConfig:
    servers: list[str]


@dataclass
class Config:
    tg_bot: TgBot
    db: Db
    nats: NatsConfig


def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env()
    return Config(
        tg_bot=TgBot(token=env('BOT_TOKEN')),
        db=Db(dsn=str(env('DSN')), is_echo=bool(env('DSN_IS_ECHO'))),
        nats=NatsConfig(servers=env.list('NATS_SERVERS'))
    )