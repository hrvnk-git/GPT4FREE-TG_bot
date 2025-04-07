# GPT-Telegram_bot

Telegram бот с использованием GPT4FREE.

## Описание

Этот бот позволяет пользователям общаться с ChatGPT прямо в Telegram бесплатно без API, а с использованием GPT4FREE библиотеки. 

## Возможности

- Отправка текстовых сообщений в ChatGPT
- Работа с фото
- Поддержка системных промптов
- Сохранение истории диалогов

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/hrvnk-git/GPT4FREE-TG_bot.git
cd GPT4FREE-TG_bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` на основе `.env example` и заполните необходимые переменные окружения, где AUTHORIZED_USER_ID это админ бота(только он может добавлять пользователей):
```
BOT_TOKEN=your_telegram_bot_token
AUTHORIZED_USER_ID=your_tg_id
```


4. Запустите бота:
```bash
python main.py
```

## Docker

Для запуска в Docker:

```bash
docker compose up -d
```

## Команды бота

- `/start` - Начать диалог с ботом
- `/add 12345612` - Добавить пользователя в бот по tg_id
- `/clear` - Очистить историю диалога
- `/id` - Узнать свой tg_id
