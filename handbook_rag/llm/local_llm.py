import logging
from pathlib import Path
from typing import AsyncGenerator, List, Optional, Union
import time

from llama_cpp import Llama

from ..config import settings
from .base import BaseLLM

logger = logging.getLogger(__name__)


class ModelManager:
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)

    def find_model_parts(self, pattern: str, total_parts: int) -> List[Path]:
        """Find all parts of the model using the pattern"""
        parts = []
        for i in range(1, total_parts + 1):
            part_path = self.model_dir / pattern.format(i, total_parts)
            if not part_path.exists():
                raise FileNotFoundError(f"Model part not found: {part_path}")
            parts.append(part_path)
        return sorted(parts)

    def get_model_path(self) -> Path:
        """Get the path to the model file or first part if split"""
        if not settings.MODEL_PARTS_PATTERN:
            model_path = Path(settings.LOCAL_MODEL_PATH)
            if not model_path.exists():
                raise FileNotFoundError(f"Model not found: {model_path}")
            return model_path

        # For split models, return the first part
        parts = self.find_model_parts(
            settings.MODEL_PARTS_PATTERN, settings.MODEL_PARTS_COUNT
        )
        return parts[0]


class LocalLLM(BaseLLM):
    def __init__(self):
        self.model = None
        self.model_manager = ModelManager(settings.MODEL_DIR)
        self._setup_device()

    def _setup_device(self):
        if settings.DEVICE == "cuda":
            from llama_cpp.llama_cpp import LlamaCppGpu

            # Parse memory limit
            units = {"GiB": 1024**3, "MiB": 1024**2}
            number = float(settings.MAX_GPU_MEMORY[:-3])
            unit = settings.MAX_GPU_MEMORY[-3:]
            self.gpu_memory = number * units[unit]
        elif settings.DEVICE == "mps":
            # MPS support is built into llama.cpp
            self.gpu_memory = None
        else:
            self.gpu_memory = None

    def load_model(self):
        model_path = self.model_manager.get_model_path()
        logger.info(f"Loading model from: {model_path}")

        model_kwargs = {
            "model_path": str(model_path),
            "n_ctx": settings.MODEL_CONTEXT_LENGTH,
            "n_batch": 512,
            "verbose": True,  # Enable verbose mode for debugging
        }

        if settings.DEVICE == "cuda":
            model_kwargs.update(
                {
                    "n_gpu_layers": settings.MODEL_GPU_LAYERS,
                    "main_gpu": 0,
                    "tensor_split": None,
                    "max_gpu_memory": self.gpu_memory,
                    "split_mode": 1,  # Enable model splitting support
                }
            )
        elif settings.DEVICE == "mps":
            model_kwargs.update(
                {
                    "n_gpu_layers": settings.MODEL_GPU_LAYERS,
                    "use_mmap": True,  # Enable memory mapping
                    "use_mlock": False,
                    "split_mode": 1,  # Enable model splitting support
                }
            )

        self.model = Llama(**model_kwargs)
        logger.info("Model loaded successfully")

    def generate(self, prompt: str, **kwargs):
        # Default parameters for generation
        params = {
            "max_tokens": 512,
            "temperature": 0.7,
            "top_p": 0.95,
            "repeat_penalty": 1.1,
            "top_k": 40,
            "stop": ["</s>", "Human:", "Assistant:"],
            "echo": False,
        }
        params.update(kwargs)

        # Format prompt for Qwen
        formatted_prompt = f"""<|im_start|>system
You are a helpful AI assistant that answers questions based on the given context.
<|im_end|>
<|im_start|>user
{prompt}
<|im_end|>
<|im_start|>assistant"""

        try:
            response_iter = self.model.create_completion(formatted_prompt, stream=True, **params)
            for response in response_iter:
                print(str(response))
                chunk = response["choices"][0]["text"]
                if chunk:
                    yield {
                        "choices": [
                            {
                                "delta": {"content": chunk},
                                "finish_reason": None,
                            }
                        ],
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": "local-model",
                    }
                else:
                    yield {
                        "choices": [
                            {
                                "delta": {},
                                "finish_reason": "stop",
                            }
                        ],
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": "local-model",
                    }
        except Exception as e:
            raise Exception(f"Error generating response: {str(e)}")
