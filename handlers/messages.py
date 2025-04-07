import os

from aiogram import Bot, F, Router
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionSender
from dotenv import load_dotenv
from loguru import logger

from middlewares.middlewares import (
    AuthorizedUserMiddleware,
    ProcessingLockMiddleware,
    RateLimitMiddleware,
)
from utils.gpt_module import ChatGPT
from utils.speach_to_text import speech_to_text

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

router = Router()
router.message.middleware(ProcessingLockMiddleware())
router.message.middleware(RateLimitMiddleware())
router.message.middleware(AuthorizedUserMiddleware())


@router.message(F.text)
async def any_message(message: Message, bot: Bot) -> None:
    async with ChatActionSender(bot=bot, chat_id=message.chat.id, action="typing"):
        try:
            answer = await ChatGPT(
                user_id=message.from_user.id, user_text=message.text
            ).generate_text()
            await message.answer(answer)
        except Exception as e:
            logger.error(f"Error: {e}")
            await message.answer("Произошла ошибка при обработке текста.")


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot) -> None:
    async with ChatActionSender(bot=bot, chat_id=message.chat.id, action="typing"):
        try:
            photo = await bot.get_file(message.photo[-1].file_id)
            url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo.file_path}"
            answer = await ChatGPT(
                user_id=message.from_user.id, user_text=message.caption
            ).receive_photo(url)
            await message.answer(answer)
        except Exception as e:
            logger.error(f"Error: {e}")
            await message.answer("Произошла ошибка при обработке фото.")


@router.message(F.voice)
async def send_text_message_on_voice(message: Message, bot: Bot) -> None:
    async with ChatActionSender(bot=bot, chat_id=message.chat.id, action="typing"):
        user_id = message.from_user.id
        try:
            file_link = await bot.get_file(message.voice.file_id)
            await bot.download_file(file_link.file_path, f"{user_id}_voice.ogg")
            text = speech_to_text(path=f"{user_id}_voice.ogg")
            answer = await ChatGPT(user_id=user_id, user_text=text).generate_text()
            await message.answer(answer, parse_mode="Markdown")
        except Exception as e:
            logger.error(f"Error: {e}")
            await message.answer("Произошла ошибка при обработке голосового сообщения.")
        finally:
            os.remove(f"{user_id}_voice.ogg")
            os.remove(f"{user_id}_voice.wav")
