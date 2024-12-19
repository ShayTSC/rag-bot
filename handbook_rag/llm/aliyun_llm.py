import os
from typing import AsyncGenerator
from openai import OpenAI

from ..config import settings
from .base import BaseLLM


class AliyunLLM(BaseLLM):
    async def generate(self, prompt: str, **kwargs) -> AsyncGenerator[str, None]:
        try:
            response = await self.client.chat.completions.create(
                model="qwen-max",  # or your specific Aliyun model
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                temperature=0.7,
                max_tokens=2048,
                **kwargs,
            )

            async for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise Exception(f"Error generating response from Aliyun: {str(e)}")

    async def load_model(self):
        self.client = OpenAI(
            api_key=settings.ALIYUN_DASHSCOPE_API_KEY,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
