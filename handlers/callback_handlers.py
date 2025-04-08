from aiogram import Router
from aiogram.types import CallbackQuery

from database.db import choose_model

router = Router()


@router.callback_query()
async def process_model_selection(callback_query: CallbackQuery):
    selected_model = (
        callback_query.data
    )  # получаем выбранную модель (например, "gpt-4o")
    user_id = callback_query.from_user.id
    await choose_model(user_id=user_id, model=selected_model)
    await callback_query.answer(
        f"Выбрана модель: *{selected_model}*", parse_mode="Markdown"
    )
    await callback_query.message.answer(
        f"Выбрана модель: *{selected_model}*",
        parse_mode="Markdown",
    )
    await callback_query.message.delete()
