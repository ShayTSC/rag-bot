from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseLLM(ABC):
    @abstractmethod
    async def generate(self, prompt: str, **kwargs):
        pass

    @abstractmethod
    async def load_model(self):
        pass
