import logging

import g4f.debug
from dotenv import load_dotenv
from g4f.client import AsyncClient
from g4f.Provider import Blackbox, PollinationsAI, RetryProvider

from config import HISTORY_MAX_LEN, prompt
from database.db import load_history, save_history

g4f.debug.logging = True
load_dotenv()

client_bb = AsyncClient(provider=RetryProvider([Blackbox], max_retries=3))
client_polly = AsyncClient(provider=RetryProvider([PollinationsAI], max_retries=3))


class ChatGPT:
    """Класс ChatGPT для взаимодействия с gpt4free"""

    def __init__(self, user_id: int, user_text: str, model: str = "gpt-4o"):
        self.user_id = user_id
        self.user_text = user_text
        self.model = model

    async def generate_response(
        self,
        client: AsyncClient,
        messages: list,
        model: str,
        tool_calls: list | None = None,
        timeout=30,
    ) -> str:
        response = await client.chat.completions.create(
            messages=messages,
            model=model,
            tool_calls=tool_calls,
            timeout=timeout,
        )
        return response.choices[0].message.content

    async def generate_text(self) -> str:
        user_history = await load_history(self.user_id, HISTORY_MAX_LEN)
        user_history.append({"role": "user", "content": self.user_text})
        messages = [{"role": "system", "content": prompt}] + user_history
        answer = await self.generate_response(
            client=client_bb, messages=messages, model=self.model
        )
        await save_history(self.user_id, "user", self.user_text)
        await save_history(self.user_id, "assistant", answer)
        return answer

    async def generate_text_with_web(self) -> str:
        tool_function = [
            {
                "function": {
                    "arguments": {
                        "query": self.user_text,
                        "max_results": 10,
                        "max_words": 3000,
                        "backend": "lite",
                        "add_text": True,
                        "region": "ru-ru",
                        "timeout": 10,
                        "instructions": "Используя предоставленные результаты веб-поиска, "
                        "написать короткий и понятный ответ . Удалить ссылки из текста.",
                    },
                    "name": "search_tool",
                },
                "type": "function",
            }
        ]
        user_history = await load_history(self.user_id, HISTORY_MAX_LEN)
        user_history.append({"role": "user", "content": self.user_text})
        messages = [{"role": "system", "content": prompt}] + user_history
        answer = await self.generate_response(
            client=client_polly,
            messages=messages,
            model="openai",
            tool_calls=tool_function,
        )
        await save_history(self.user_id, "user", self.user_text)
        await save_history(self.user_id, "assistant", answer)
        return answer

    async def answer_on_photo(self, url: str) -> str:
        """Обрабатывает фото с добавлением контекста сообщения."""

        if self.user_text:
            user_text = self.user_text
        else:
            user_text = "Вот фото"
        messages = [
            {
                "role": "system",
                "content": prompt,
                "role": "user",
                "content": [
                    {"type": "text", "text": user_text},
                    {"type": "image_url", "image_url": {"url": url}},
                ],
            }
        ]
        answer = await self.generate_response(
            client=client_polly, messages=messages, model="openai"
        )
        await save_history(self.user_id, "user", user_text)
        await save_history(self.user_id, "assistant", answer)
        return answer
