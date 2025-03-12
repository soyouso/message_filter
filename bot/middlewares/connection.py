from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import AsyncEngine


class DbEngineMiddleware(BaseMiddleware):
    def __init__(self, engine: AsyncEngine):
        super().__init__()
        self.engine = engine

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.engine.connect() as conn:
            data['engine'] = conn
            return await handler(event, data)