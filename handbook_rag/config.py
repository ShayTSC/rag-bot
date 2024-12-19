from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Device settings
    DEVICE: str = "mps"  # "cuda", "mps", or "cpu"
    MAX_GPU_MEMORY: str = "8GiB"

    # API settings
    API_TOKEN: str = "your-secret-token"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # LLM settings
    LOCAL_MODEL_PATH: str = "./models/qwen2.5-7b"
    MODEL_DIR: str = "./models"
    MODEL_PARTS_PATTERN: Optional[str] = None
    MODEL_PARTS_COUNT: Optional[int] = None
    SPLIT_MODE: int = 1  # Enable model splitting
    USE_LOCAL_MODEL: bool = True
    MODEL_CONTEXT_LENGTH: int = 2048
    MODEL_GPU_LAYERS: int = -1  # -1 means all layers

    # Aliyun fallback settings
    ALIYUN_DASHSCOPE_API_KEY: Optional[str] = None

    # Embedding settings
    EMBEDDING_MODEL: str = "BAAI/bge-small-en"

    # Queue settings
    MAX_QUEUE_SIZE: int = 100
    WORKERS: int = 2

    # Vector store settings
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_COLLECTION: str = "handbook"
    QDRANT_VECTOR_SIZE: int = 384  # BGE-small-en embedding size

    class Config:
        env_file = ".env"


settings = Settings()
