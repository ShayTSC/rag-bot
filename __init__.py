import asyncio

from handbook_rag.bootstrap import RAGService


async def main():
    service = RAGService()
    await service.initialize()

    # Process PDF first
    await service.task_queue.enqueue(service.embedder.process_pdf, "data/handbook.pdf")

    # Query the handbook
    response = await service.process_query(
        "How many days can I leave the office?"
    )
    print(response)

    await service.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
