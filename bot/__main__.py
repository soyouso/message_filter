import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from bot.db import metadata
from bot.handlers import commands_router, others_router
from bot.middlewares import TranslatorRunnerMiddleware, DbEngineMiddleware, TrackAllUsersMiddleware
from bot.config_data import load_config, Config
from bot.dialogs import first_dialog
from aiogram_dialog import setup_dialogs
from sqlalchemy.ext.asyncio import create_async_engine
from bot.utils import create_translator_hub
from bot.storage.nats_storage import NatsStorage
from bot.utils.nats_connect import connect_to_nats
from fluentogram import TranslatorHub

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def main() -> None:

    config: Config = load_config()

    nc, js = await connect_to_nats(servers=config.nats.servers)
    storage: NatsStorage = await NatsStorage(nc=nc, js=js).create_storage()

    engine = create_async_engine(
        url=config.db.dsn,
        echo=config.db.is_echo
    )


    async with engine.begin() as conn:
        await conn.run_sync(metadata.drop_all)
        await conn.run_sync(metadata.create_all)


    bot = Bot(token=config.tg_bot.token,
              default=DefaultBotProperties(parse_mode='HTML'))

    dp = Dispatcher(db_engine=engine, storage=storage)

    translator_hub: TranslatorHub = create_translator_hub()

    dp.include_router(commands_router)
    dp.include_router(others_router)
    dp.include_router(first_dialog)

    dp.update.middleware(DbEngineMiddleware(engine))
    dp.message.outer_middleware(TrackAllUsersMiddleware())
    dp.update.middleware(TranslatorRunnerMiddleware())

    setup_dialogs(dp)

    try:
        await dp.start_polling(bot, _translator_hub=translator_hub)
    except Exception as e:
        logger.exception(e)
    finally:
        await nc.close()
        logger.info('Connection to NATS closed')

asyncio.run(main())
