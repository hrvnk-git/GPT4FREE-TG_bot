from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="GPT-4", callback_data="gpt-4o"),
            InlineKeyboardButton(text="o3-mini", callback_data="o3-mini"),
        ],
        [
            InlineKeyboardButton(text="Claude-sonnet-3.7", callback_data="Claude-sonnet-3.7"),
            InlineKeyboardButton(text="DeepSeek-R1", callback_data="DeepSeek-R1"),
        ],
    ]
)
