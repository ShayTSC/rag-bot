import json
import logging
from typing import AsyncGenerator, Dict

from .config import settings
from .embeddings.pdf_embedder import PDFEmbedder
from .llm.aliyun_llm import AliyunLLM
from .llm.local_llm import LocalLLM
from .queue.task_queue import TaskQueue

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.local_llm = LocalLLM()
        self.aliyun_llm = AliyunLLM()
        self.embedder = PDFEmbedder()
        self.task_queue = TaskQueue()

    async def initialize(self):
        # Load models
        if settings.USE_LOCAL_MODEL:
            self.local_llm.load_model()
        else:
            self.aliyun_llm.load_model()

        self.embedder.load_model()

        # Start task queue
        await self.task_queue.start_workers()

    async def ensure_embeddings(self, pdf_path: str):
        """Ensure PDF is embedded and wait for completion"""
        if not self.embedder.has_embeddings():
            logger.info("No embeddings found. Processing PDF...")
            future = await self.task_queue.enqueue(self.embedder.process_pdf, pdf_path)
            # Wait for embedding to complete
            await future
            logger.info("PDF processing completed")
        else:
            logger.info("Embeddings already exist")

    def process_query(self, query: str):
        if not self.embedder.has_embeddings():
            raise ValueError("No embeddings available. Please process a PDF first.")

        # Get relevant context from vector store
        relevant_chunks = self.embedder.search_similar(query, limit=3)
        context = "\n".join(relevant_chunks)

        # Create prompt
        prompt = f"""<|im_start|>system
You are a helpful AI assistant that answers questions based on the company handbook.
Only use the information provided in the context below. If you cannot find the answer
in the context, say "I cannot find information about this in the handbook."

Here is the relevant section from the handbook:
---
{context}
---
<|im_end|>
<|im_start|>user
Based on the handbook section above, {query}
<|im_end|>
<|im_start|>assistant"""

        # Use local LLM or fallback to Aliyun
        try:
            if settings.USE_LOCAL_MODEL:
                for chunk in self.local_llm.generate(prompt):
                    yield chunk
            else:
                for chunk in self.aliyun_llm.generate(prompt):
                    yield chunk
        except Exception as e:
            if settings.USE_LOCAL_MODEL:
                # Fallback to Aliyun
                for chunk in self.aliyun_llm.generate(prompt):
                    yield chunk
            raise e

    async def shutdown(self):
        await self.task_queue.stop_workers()
