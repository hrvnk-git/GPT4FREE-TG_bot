import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv

from database.db import add_authorized_user, init_db
from handlers.commands import id_router, router
from handlers.messages import router as r2

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
AUTHORIZED_USER_ID = os.getenv("AUTHORIZED_USER_ID")


async def main():
    await init_db()
    await add_authorized_user(user_id=int(AUTHORIZED_USER_ID), admin=1)

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_routers(router, id_router, r2)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("bot.log"), logging.StreamHandler()],
    )
    asyncio.run(main())
