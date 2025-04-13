import asyncio
import os

from aiogram import Bot, F, Router, flags
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionMiddleware
from dotenv import load_dotenv
from loguru import logger

from database.db import get_model, get_web_search
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
router.message.middleware(ChatActionMiddleware())


@router.message(F.text)
@flags.chat_action("typing")
async def any_message(message: Message) -> None:
    try:
        user_id = message.from_user.id
        websearch_status = await get_web_search(user_id)
        model = await get_model(user_id)
        answer = ""
        if websearch_status:
            answer = await ChatGPT(
                user_id=user_id,
                user_text=message.text,
                model=model,
            ).generate_text_with_web()
        if not websearch_status:
            answer = await ChatGPT(
                user_id=user_id,
                user_text=message.text,
                model=model,
            ).generate_text()
        logger.info(f"Answer: {answer}")
        if len(answer) <= 4096:
            await message.answer(answer, parse_mode="Markdown")
        else:
            for i in range(0, len(answer), 4096):
                await message.answer(answer[i : i + 4096])
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке текста.")


@router.message(F.photo)
@flags.chat_action("typing")
async def handle_photo(message: Message, bot: Bot) -> None:
    try:
        photo = await bot.get_file(message.photo[-1].file_id)
        url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{photo.file_path}"
        answer = await ChatGPT(
            user_id=message.from_user.id,
            user_text=message.caption,
        ).answer_on_photo(url)
        if len(answer) <= 4096:
            await message.answer(answer, parse_mode="Markdown")
        else:
            for i in range(0, len(answer), 4096):
                await message.answer(answer[i : i + 4096])
    except Exception as e:
        logger.error(f"Error: {e}")
        await message.answer("Произошла ошибка при обработке фото.")


@router.message(F.voice)
@flags.chat_action("typing")
async def send_text_message_on_voice(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id
    websearch_status = await get_web_search(user_id)
    model = await get_model(user_id)
    answer = ""
    attempt = 0
    while attempt < 3:
        try:
            file_link = await bot.get_file(message.voice.file_id)
            await bot.download_file(file_link.file_path, f"{user_id}_voice.ogg")
            text = speech_to_text(path=f"{user_id}_voice.ogg")
            if websearch_status:
                answer = await ChatGPT(
                    user_id=user_id,
                    user_text=text,
                    model=model,
                ).generate_text_with_web()
            if not websearch_status:
                answer = await ChatGPT(
                    user_id=user_id,
                    user_text=text,
                    model=model,
                ).generate_text()
            await message.answer(f"```Текст:\n{text}```", parse_mode="Markdown")
            if len(answer) <= 4096:
                await message.answer(answer, parse_mode="Markdown")
            else:
                for i in range(0, len(answer), 4096):
                    await message.answer(answer[i : i + 4096])
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            attempt += 1
            await asyncio.sleep(3)
            if attempt == 3:
                await message.answer(
                    "Произошла ошибка при обработке голосового сообщения."
                )
        finally:
            os.remove(f"{user_id}_voice.ogg")
            os.remove(f"{user_id}_voice.wav")
