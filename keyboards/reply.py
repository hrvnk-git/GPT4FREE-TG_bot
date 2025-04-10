from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Выбрать модель"),
            KeyboardButton(text="Очистить историю"),
        ],
        [
            KeyboardButton(text="Мой ID"),
        ],
    ],
    resize_keyboard=True,
)
