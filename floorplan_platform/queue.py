from __future__ import annotations

import os
from typing import Optional

try:
    from rq import Queue
    from redis import Redis
except ImportError:  # pragma: no cover - optional dependency
    Queue = None
    Redis = None

from floorplan_platform.tasks import process_job


def get_queue() -> Optional["Queue"]:
    if Queue is None or Redis is None:
        return None
    redis_url = os.environ.get("FLOORPLAN_REDIS_URL", "redis://localhost:6379/0")
    return Queue(connection=Redis.from_url(redis_url))


def enqueue(job_id: str, track: str, scale: float) -> str:
    queue = get_queue()
    if queue is None:
        process_job(job_id=job_id, track=track, scale=scale)
        return "inline"
    queue.enqueue(process_job, job_id=job_id, track=track, scale=scale)
    return "queued"
