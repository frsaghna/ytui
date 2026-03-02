import asyncio
from typing import Optional, List, Callable, Coroutine
from .models import DownloadJob, DownloadStatus

class DownloadQueue:
    def __init__(self, on_update: Callable[[DownloadJob], None]):
        self._queue: List[DownloadJob] = []
        self._current_job: Optional[DownloadJob] = None
        self._on_update = on_update
        self._running = False

    def add_job(self, job: DownloadJob):
        self._queue.append(job)
        self._on_update(job)

    def get_all(self) -> List[DownloadJob]:
        return self._queue

    def get_current(self) -> Optional[DownloadJob]:
        return self._current_job

    async def start(self, runner_callback: Callable[[DownloadJob], Coroutine]):
        if self._running:
            return
        
        self._running = True
        while self._running:
            # Find next pending job
            next_job = None
            for job in self._queue:
                if job.status == DownloadStatus.PENDING:
                    next_job = job
                    break
            
            if next_job:
                self._current_job = next_job
                await runner_callback(next_job)
                self._current_job = None
            else:
                await asyncio.sleep(1)

    def stop(self):
        self._running = False
