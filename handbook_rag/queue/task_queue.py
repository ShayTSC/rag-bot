import asyncio
from collections import deque
from typing import Any, Callable

from ..config import settings


class TaskQueue:
    def __init__(self):
        self.queue = deque()
        self.workers = []
        self.running = False

    async def enqueue(self, task: Callable, *args, **kwargs) -> asyncio.Future:
        if len(self.queue) >= settings.MAX_QUEUE_SIZE:
            raise ValueError("Queue is full")

        future = asyncio.Future()
        self.queue.append((task, args, kwargs, future))
        return future

    async def start_workers(self):
        self.running = True
        self.workers = [
            asyncio.create_task(self._worker()) for _ in range(settings.WORKERS)
        ]

    async def stop_workers(self):
        self.running = False
        for worker in self.workers:
            worker.cancel()
        self.workers = []

    async def _worker(self):
        while self.running:
            try:
                if not self.queue:
                    await asyncio.sleep(0.1)
                    continue

                task, args, kwargs, future = self.queue.popleft()
                try:
                    if task:
                        if task:
                            result = await task(*args, **kwargs)
                            future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
            except asyncio.CancelledError:
                break
