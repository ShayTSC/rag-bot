from typing import Dict, List

import numpy as np
from PyPDF2 import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from ..config import settings


class PDFEmbedder:
    def __init__(self):
        self.model = None
        self.client = QdrantClient(host=settings.QDRANT_HOST, port=settings.QDRANT_PORT)
        self._ensure_collection()

    def has_embeddings(self) -> bool:
        """Check if collection has any points"""
        collection_info = self.client.get_collection(settings.QDRANT_COLLECTION)
        return collection_info.points_count > 0

    def _ensure_collection(self):
        """Ensure the collection exists with proper configuration"""
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if settings.QDRANT_COLLECTION not in collection_names:
            self.client.create_collection(
                collection_name=settings.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=settings.QDRANT_VECTOR_SIZE, distance=Distance.COSINE
                ),
            )

    def load_model(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        if settings.DEVICE == "cuda":
            self.model.to("cuda")
        elif settings.DEVICE == "mps":
            self.model.to("mps")

    def process_pdf(self, pdf_path: str):
        with open(pdf_path, "rb") as file:
            pdf_reader = PdfReader(file)
            texts = []
            for page in pdf_reader.pages:
                texts.append(page.extract_text())

        # Split texts into chunks
        chunks = self._split_into_chunks(texts)
        embeddings = self.model.encode(chunks, normalize_embeddings=True)

        # Store in Qdrant
        points = [
            PointStruct(id=i, vector=embedding.tolist(), payload={"text": chunk})
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings))
        ]

        # Upsert in batches to handle large documents
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i : i + batch_size]
            self.client.upsert(collection_name=settings.QDRANT_COLLECTION, points=batch)

    def search_similar(self, query: str, limit: int = 3) -> List[str]:
        query_embedding = self.model.encode([query], normalize_embeddings=True)

        search_result = self.client.search(
            collection_name=settings.QDRANT_COLLECTION,
            query_vector=query_embedding[0].tolist(),
            limit=limit,
        )

        return [hit.payload["text"] for hit in search_result]

    def _split_into_chunks(self, texts: List[str], chunk_size: int = 512) -> List[str]:
        chunks = []
        for text in texts:
            words = text.split()
            current_chunk = []
            current_size = 0

            for word in words:
                if current_size + len(word) > chunk_size:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = [word]
                    current_size = len(word)
                else:
                    current_chunk.append(word)
                    current_size += len(word) + 1

            if current_chunk:
                chunks.append(" ".join(current_chunk))

        return chunks
