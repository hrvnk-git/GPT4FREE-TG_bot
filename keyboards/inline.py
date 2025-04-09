from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

settings = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="gpt-4o", callback_data="gpt-4o"),
            InlineKeyboardButton(text="gpt-4o-mini", callback_data="gpt-4o-mini"),
        ],
        [
            InlineKeyboardButton(text="o1", callback_data="o1"),
            InlineKeyboardButton(text="o3-mini", callback_data="o3-mini"),
        ],
        [
            InlineKeyboardButton(text="claude-3.7-sonnet", callback_data="claude-3.7-sonnet"),
        ],
    ]
)
