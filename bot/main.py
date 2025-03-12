import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, Update
from environs import Env


logging.basicConfig(level=logging.INFO)

env = Env()
env.read_env()
bot = Bot(token=env('BOT_TOKEN'))
dp = Dispatcher()

router = Router()

def my_filter(message: Message):
    return 'кра' in message.text

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добавьте этого бота в группу для фильтрации неугодных сообщений')


@router.message(F.text, my_filter)
async def deleting_stol(message: Message):
    await message.delete()

@router.chat_join_request()
async def ggg(update: Update):
    print(1)
    print(update.model_dump_json(indent=5, exclude_none=True))


dp.include_router(router)


dp.run_polling(bot)