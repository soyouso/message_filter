from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode
from bot.dialogs.start.states import FirstDialogSG

commands_router = Router()


@commands_router.message(CommandStart(), F.chat.type == 'private')
async def cmd_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=FirstDialogSG.start, mode=StartMode.RESET_STACK)
