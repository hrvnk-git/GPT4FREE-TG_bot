from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Выбрать модель"),
            KeyboardButton(text="Поиск в интернете"),
        ],
        [
            KeyboardButton(text="Мой ID"),
            KeyboardButton(text="Очистить историю"),
        ],
    ],
    resize_keyboard=True,
)
