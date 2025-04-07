import asyncio
import os

from aiogram import Bot, F, Router
from aiogram.types import Message
from dotenv import load_dotenv
from loguru import logger

from middlewares.middlewares import (
    ProcessingLockMiddleware,
    RateLimitMiddleware,
    AuthorizedUserMiddleware,
)
from utils.gpt_module import gpt_client

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

router = Router()
router.message.middleware(ProcessingLockMiddleware())
router.message.middleware(RateLimitMiddleware())
router.message.middleware(AuthorizedUserMiddleware())


@router.message(F.text)
async def any_message(message: Message, bot: Bot) -> None:
    typing_task = asyncio.create_task(keep_typing(message, bot))
    try:
        answer = await gpt_client.generate_text(
            user_id=message.from_user.id,
            user_text=message.text,
        )
        await message.answer(answer, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке текста.")
    finally:
        typing_task.cancel()


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot) -> None:
    typing_task = asyncio.create_task(keep_typing(message, bot))
    try:
        user_id = message.from_user.id
        message_text = message.caption

        photo = await bot.get_file(message.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo.file_path}"
        answer = await gpt_client.receive_photo(user_id, message_text, url)
        await message.answer(answer)
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке фото.")
    finally:
        typing_task.cancel()


@router.message(F.voice)
async def send_text_message_on_voice(message: Message, bot: Bot) -> None:
    typing_task = asyncio.create_task(keep_typing(message, bot))
    user_id = message.from_user.id
    try:
        file_link = await bot.get_file(message.voice.file_id)
        await bot.download_file(file_link.file_path, f"{user_id}_voice.ogg")
        with open(f"{user_id}_voice.ogg", "rb") as voice_file:
            answer = await gpt_client.generate_text_on_voice(
                user_id=user_id,
                voice=voice_file,
            )
        await message.answer(answer, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке голосового сообщения.")
    finally:
        typing_task.cancel()
        os.remove(f"{user_id}_voice.ogg")


async def keep_typing(message: Message, bot: Bot) -> None:
    """Функция для имитации действия "печатает..." в чате."""
    while True:
        await bot.send_chat_action(message.chat.id, action="typing")
        await asyncio.sleep(4)
