from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

import keyboards.inline as ikb
import keyboards.reply as kb
from database.db import (
    add_authorized_user,
    delete_history,
    get_web_search,
    set_web_search,
)
from middlewares.middlewares import (
    AuthorizedUserMiddleware,
    ProcessingLockMiddleware,
    RateLimitMiddleware,
)

# отдельный роутер для команды /id
id_router = Router()
id_router.message.middleware(ProcessingLockMiddleware())
id_router.message.middleware(RateLimitMiddleware())


@id_router.message(F.text == "Мой ID")
@id_router.message(Command("id"))
async def cmd_id(message: Message) -> None:
    await message.answer(f"Ваш ID: `{message.from_user.id}`", parse_mode="Markdown")  # type: ignore


router = Router()
router.message.middleware(ProcessingLockMiddleware())
router.message.middleware(RateLimitMiddleware())
router.message.middleware(AuthorizedUserMiddleware())


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    await message.answer(
        "Привет! Я бесплатный AI-бот, который может отвечать на текстовые и голосовые сообщения,"
        " а так же могу работать с фото и искать информацию в интернете.",
        reply_markup=kb.main,
    )


@router.message(F.text == "Выбрать модель")
@router.message(Command("models"))
async def send_model_list(message: Message) -> None:
    await message.answer("Выберите модель:", reply_markup=ikb.settings)
    await message.delete()


@router.message(F.text == "Очистить историю")
@router.message(Command("clear"))
async def cmd_delete_history(message: Message) -> None:
    await delete_history(message.from_user.id)  # type: ignore
    await message.answer("*Контекст разговора очищен. Начат новый разговор.*", parse_mode="Markdown")


@router.message(F.text == "Поиск в интернете")
async def cmd_use_internet(message: Message) -> None:
    user_id = message.from_user.id # type: ignore
    websearch_status = await get_web_search(user_id)
    if websearch_status:
        await set_web_search(user_id, False)
        await message.answer("*Поиск в интернете выключен.*", parse_mode="Markdown")
    else:
        await set_web_search(user_id, True)
        await message.answer("*Поиск в интернете включен.*", parse_mode="Markdown")


@router.message(Command("add"))
async def cmd_add(message: Message) -> None:
    args = message.text.split(maxsplit=1)[1:] # type: ignore
    if not args:
        await message.answer("Пожалуйста, укажите id после команды /add.")
        return
    user_id = int(args[0].strip())
    try:
        await add_authorized_user(user_id)
        await message.answer("Пользователь добавлен в базу данных.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении пользователя: {e}")
