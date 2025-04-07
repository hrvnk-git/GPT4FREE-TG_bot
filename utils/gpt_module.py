from dotenv import load_dotenv
from g4f.client import AsyncClient

from config import prompt
from database.db import get_model, load_history, save_message

load_dotenv()

HISTORY_MAX_LEN = 30  # При использовании chat.completions и DB


class ChatGPT:
    """Класс ChatGPT для взаимодействия с gpt4free"""

    def __init__(self, user_id: int, user_text: str):
        self.client = AsyncClient()
        self.user_id = user_id
        self.user_text = user_text

    async def generate_text(self) -> str:
        user_history = await load_history(self.user_id, HISTORY_MAX_LEN)
        user_history.append({"role": "user", "content": self.user_text})
        messages = [{"role": "system", "content": prompt}] + user_history
        completion = await self.client.chat.completions.create(
            model=await get_model(self.user_id),
            messages=messages,
        )
        response_text = str(completion.choices[0].message.content)
        await save_message(self.user_id, "user", self.user_text)
        await save_message(self.user_id, "assistant", response_text)
        return response_text

    async def receive_photo(self, url: str) -> str:
        """Обрабатывает фото с добавлением контекста сообщения."""
        if self.user_text:
            user_text = self.user_text
        else:
            user_text = "Что на фото?"
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": url,
                            },
                        },
                    ],
                }
            ],
        )
        response_text = str(response.choices[0].message.content)
        await save_message(self.user_id, "user", user_text)
        await save_message(self.user_id, "assistant", response_text)

        return response_text
