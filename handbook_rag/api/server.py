import asyncio
import json
from typing import AsyncGenerator, Optional

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
from fastapi.middleware.cors import CORSMiddleware

from ..bootstrap import RAGService
from ..config import settings

app = FastAPI(title="Handbook RAG API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Add your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
security = HTTPBearer()
rag_service = RAGService()


class QueryRequest(BaseModel):
    query: str
    stream: bool = False


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    stream: bool = False


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != settings.API_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return credentials


@app.on_event("startup")
async def startup_event():
    await rag_service.initialize()


@app.on_event("shutdown")
async def shutdown_event():
    await rag_service.shutdown()


@app.post("/v1/embed")
async def embed_document(
    file: UploadFile = File(...),
    credentials: HTTPAuthorizationCredentials = Depends(verify_token),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are supported")

    # Save uploaded file temporarily
    temp_path = f"temp_{file.filename}"
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Process the PDF and wait for completion
        await rag_service.ensure_embeddings(temp_path)

        return {"status": "success", "message": "Document processing completed"}

    finally:
        import os

        if os.path.exists(temp_path):
            os.remove(temp_path)


def stream_response(query: str):
    try:
        for chunk in rag_service.process_query(query):
            yield f"{json.dumps(chunk)}\n\n"
    except Exception as e:
        error_response = {"error": {"message": str(e), "type": "internal_error"}}
        yield f"data: {json.dumps(error_response)}\n\n"


@app.post("/v1/chat/completions")
async def chat_completions(
    request: ChatRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token),
):
    query = " ".join([msg.content for msg in request.messages if msg.role == "user"])

    return EventSourceResponse(
        stream_response(query),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Transfer-Encoding": "chunked",
        },
    )


@app.post("/query")
async def query(
    request: QueryRequest,
    credentials: HTTPAuthorizationCredentials = Depends(verify_token),
):
    if request.stream:
        return EventSourceResponse(
            stream_response(request.query), media_type="text/event-stream"
        )

    response = await rag_service.process_query(request.query)
    return {"response": response}
