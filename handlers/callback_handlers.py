from aiogram import Router
from aiogram.types import CallbackQuery

from database.db import set_model

router = Router()


@router.callback_query()
async def process_model_selection(callback_query: CallbackQuery):
    selected_model = callback_query.data
    user_id = callback_query.from_user.id
    await set_model(user_id=user_id, model=selected_model)  # type: ignore
    await callback_query.answer(
        f"Выбрана модель: *{selected_model}*", parse_mode="Markdown"
    )
    await callback_query.message.answer(
        f"Выбрана модель: *{selected_model}*",
        parse_mode="Markdown",
    )
    await callback_query.message.delete()  # type: ignore
