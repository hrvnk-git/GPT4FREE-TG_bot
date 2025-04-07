import os

import g4f.Provider
from dotenv import load_dotenv
from g4f.client import AsyncClient

from config import prompt
from database.db import load_history, save_message

load_dotenv()

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HISTORY_MAX_LEN = 30  # При использовании chat.completions и DB


class ChatGPT:
    """Класс ChatGPT для взаимодействия с API OpenAI"""

    def __init__(self):
        self.client = AsyncClient()

    async def generate_text(self, user_text, user_id: int) -> str:
        user_history = await load_history(user_id, HISTORY_MAX_LEN)
        user_history.append({"role": "user", "content": user_text})
        messages = [{"role": "system", "content": prompt}] + user_history
        completion = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
        )
        response_text = str(completion.choices[0].message.content)
        await save_message(user_id, "user", user_text)
        await save_message(user_id, "assistant", response_text)
        return response_text

    # async def generate_voice(self, user_id: int, voice):
    #     """Транскрибирует голосовое сообщение и генерирует голосовой ответ."""
    #     transcript = await self.client.audio.transcriptions.create(
    #         model="gpt-4o-mini-transcribe", file=voice
    #     )
    #     answer = await self.generate_text(transcript.text, user_id)
    #     speech_file_path = Path(__file__).parent.parent / f"{user_id}_speech.ogg"
    #     async with self.client.audio.speech.with_streaming_response.create(
    #         model="gpt-4o-mini-tts",
    #         voice="shimmer",
    #         input=answer,
    #         instructions=instructions,
    #         response_format="opus",
    #         speed=0.25,
    #     ) as response:
    #         await response.stream_to_file(speech_file_path)
    #     return FSInputFile(speech_file_path), answer

    async def generate_text_on_voice(self, user_id: int, voice) -> str:
        """Транскрибирует голосовое сообщение и генерирует текстовый ответ."""
        # transcript = await self.client.chat.create(
        #     model="gpt-4o-mini-transcribe", file=voice
        # )
        # return await self.generate_text(transcript.text, user_id)

        response = await self.client.chat.completions.create(
            messages="Transcribe this audio",
            provider=g4f.Provider.Microsoft_Phi_4,
            media=[[voice, "audio.ogg"]],
            modalities=["text"],
        )
        return response.choices[0].message.content

    async def receive_photo(
        self, user_id: int, message_text: str | None, url: str
    ) -> str:
        """Обрабатывает фото с добавлением контекста сообщения."""
        if message_text:
            message_text = message_text
        else:
            message_text = "Что на фото?"
        response = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message_text},
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
        await save_message(user_id, "user", message_text)
        await save_message(user_id, "assistant", response_text)

        return response_text


gpt_client = ChatGPT()
