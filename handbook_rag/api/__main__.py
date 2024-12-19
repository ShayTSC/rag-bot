import uvicorn

from handbook_rag.config import settings
from handbook_rag.api.server import app


def main():
    uvicorn.run(
        "handbook_rag.api.server:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )


if __name__ == "__main__":
    main()
