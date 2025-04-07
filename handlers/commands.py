from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

import keyboards.inline as ikb
import keyboards.reply as kb

# from ..database.db import delete_response_id
from database.db import add_authorized_user, delete_history
from middlewares.middlewares import (
    AuthorizedUserMiddleware,
    ProcessingLockMiddleware,
    RateLimitMiddleware,
)

# Создаем отдельный роутер для команды /id
id_router = Router()
id_router.message.middleware(ProcessingLockMiddleware())
id_router.message.middleware(RateLimitMiddleware())


@id_router.message(F.text == "Мой ID")
@id_router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await message.answer(f"Ваш ID: `{message.from_user.id}`", parse_mode="Markdown")


router = Router()
router.message.middleware(ProcessingLockMiddleware())
router.message.middleware(RateLimitMiddleware())
router.message.middleware(AuthorizedUserMiddleware())


@router.message(F.text == "Выбрать модель")
@router.message(Command("models"))
async def send_model_list(message: Message) -> None:
    """Отправляет список доступных моделей."""
    await message.answer("Выберите модель:", reply_markup=ikb.settings)
    await message.delete()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бесплатный AI-бот, который может отвечать на текстовые и голосовые сообщения, "
        "а так же могу работать с фото.",
        reply_markup=kb.main,
    )


@router.message(F.text == "Очистить историю")
@router.message(Command("clear"))
async def cmd_delete_history(message: Message) -> None:
    await delete_history(message.from_user.id)  # type: ignore
    await message.answer("История очищена. Начат новый разговор.")


@router.message(Command("add"))
async def cmd_add(message: Message) -> None:
    args = message.text.split(maxsplit=1)[1:]  # Получаем аргументы после команды
    if not args:
        await message.answer("Пожалуйста, укажите id после команды /add.")
        return

    user_id = args[0].strip()
    try:
        await add_authorized_user(user_id)
        await message.answer("Пользователь добавлен в базу данных.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении пользователя: {e}")
