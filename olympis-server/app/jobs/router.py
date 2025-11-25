from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from rq import Queue
import asyncio
import json
import redis
from rq.job import Job

from app.logger import get_logger
from app.user.dependencies import UserDependency

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{job_id}")
async def read_job(job_id: str, request: Request, user: UserDependency):
    logger.info(f"JOB READ {job_id} requested for user: {user.id}")
    q = request.app.state.app_state.queue

    job = Job.fetch(job_id, connection=q.connection)

    return {"status": job.get_status()}


@router.get("/{job_id}/events")
async def read_job_events(job_id: str, request: Request, user: UserDependency):
    r: redis.Redis = request.app.state.app_state.cache._client

    stream = f"job:{job_id}:events"

    async def gen():
        yield "retry: 3000\n\n"

        try:
            existing_messages = await r.xrange(stream)
            logger.info(f"Sending {len(existing_messages)} existing messages for job {job_id}")

            for msg_id, fields in existing_messages:
                raw = None
                if isinstance(fields, dict):
                    raw = fields.get(b"data")
                    if raw is None:
                        raw = fields.get("data")
                if raw is None:
                    continue

                if isinstance(raw, bytes):
                    raw = raw.decode("utf-8", "replace")

                # Ensure it's valid JSON before sending
                try:
                    _ = json.loads(raw)
                except Exception:
                    logger.warning(f"SSE WARN: non-JSON 'data' value: {raw}")
                    continue

                sid = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                yield f"id: {sid}\n"
                yield f"data: {raw}\n\n"

            # Set current to the last message ID, or "$" if no messages exist
            current = existing_messages[-1][0].decode() if existing_messages else "$"

        except Exception as e:
            logger.error(f"Error reading existing messages: {e}")
            current = "$"

        # Then continue streaming new messages
        while True:
            if await request.is_disconnected():
                return

            results = await r.xread({stream: current}, block=15000, count=10)
            if not results:
                yield ": keepalive\n\n"
                continue

            for _name, messages in results:
                for msg_id, fields in messages:
                    raw = None
                    if isinstance(fields, dict):
                        raw = fields.get(b"data")
                        if raw is None:
                            raw = fields.get("data")
                    if raw is None:
                        continue

                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8", "replace")

                    # Ensure it's valid JSON before sending
                    try:
                        _ = json.loads(raw)
                    except Exception:
                        logger.warning(f"SSE WARN: non-JSON 'data' value: {raw}")
                        continue

                    sid = msg_id.decode() if isinstance(msg_id, bytes) else msg_id
                    yield f"id: {sid}\n"
                    yield f"data: {raw}\n\n"
                    current = sid

    return StreamingResponse(
        gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable Nginx buffering
        },
    )
