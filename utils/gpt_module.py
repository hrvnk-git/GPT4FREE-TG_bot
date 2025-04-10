import g4f.debug
from dotenv import load_dotenv
from g4f.client import AsyncClient
from g4f.Provider import RetryProvider, PollinationsAI, Blackbox
from loguru import logger

from config import date_now, filter_for_message, prompt
from database.db import get_model, load_history, save_message

g4f.debug.logging = True
load_dotenv()

HISTORY_MAX_LEN = 10


class ChatGPT:
    """Класс ChatGPT для взаимодействия с gpt4free"""

    def __init__(self, user_id: int, user_text: str):
        self.client = AsyncClient(provider=RetryProvider([PollinationsAI, Blackbox], shuffle=False, max_retries=3))
        self.user_id = user_id
        self.user_text = user_text
        self.model = "gpt-4o"

    async def generate_response(
        self,
        messages: list,
        model: str = "gpt-4o",
        web_search: bool = False,
        tool_calls: list | None = None,
        timeout=60
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            web_search=web_search,
            tool_calls=tool_calls,
            timeout=timeout
        )
        return response.choices[0].message.content

    async def generate_text(self) -> str:
        tool_function = [
            {
                "function": {
                    "arguments": {
                        # "query": "Latest advancements in AI",
                        "max_results": 10,
                        "max_words": 2000,
                        "backend": "auto",
                        "add_text": True,
                        "timeout": 10,
                    },
                    "name": "search_tool",
                },
                "type": "function",
            }
        ]
        user_query = [
            {"role": "system", "content": filter_for_message},
            {"role": "user", "content": self.user_text},
        ]
        user_history = await load_history(self.user_id, HISTORY_MAX_LEN)
        user_history.append({"role": "user", "content": self.user_text})
        messages = [{"role": "system", "content": prompt}] + user_history
        answer = ""
        count = 0
        while count < 2:
            try:
                response = await self.generate_response(messages=user_query)
                if response[:5].count("0") == 1:
                    answer = await self.generate_response(
                        messages=messages, model=await get_model(self.user_id)
                    )
                    break
                if response[:5].count("1") == 1:
                    user_query_2 = messages + [
                        {
                            "role": "user",
                            "content": f"{date_now} Сформируй запрос в Google для ответа. Пришли только текст запроса",
                        },
                    ]
                    pre_answer = await self.generate_response(messages=user_query_2)
                    google_query = [{"role": "user", "content": pre_answer}]
                    google_answer = await self.generate_response(
                        messages=google_query, tool_calls=tool_function, web_search=True
                    )
                    user_query_3 = [
                        {"role": "user", "content": self.user_text},
                        {
                            "role": "assistant",
                            "content": google_answer,
                        },
                        {"role": "user", "content": "Удали ссылки на источники"},
                    ]
                    answer = await self.generate_response(
                        messages=user_query_3, model=await get_model(self.user_id)
                    )
                    break
            except Exception as e:
                logger.error(f"Error: {e}")
                count += 1

        await save_message(self.user_id, "user", self.user_text)
        await save_message(self.user_id, "assistant", answer)
        return answer

    async def receive_photo(self, url: str) -> str:
        """Обрабатывает фото с добавлением контекста сообщения."""
        if self.user_text:
            user_text = self.user_text
        else:
            user_text = "Что на фото?"
        response = await self.client.chat.completions.create(
            model="o1",
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
        answer = response.choices[0].message.content
        await save_message(self.user_id, "user", user_text)
        await save_message(self.user_id, "assistant", answer)
        return answer
