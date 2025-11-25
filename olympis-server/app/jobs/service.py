import json
import uuid

from rq import get_current_job
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import BaseError, ResourceNotFoundError
from app.jobs.models import Job
from app.logger import get_logger

logger = get_logger(__name__)


def update_job_progress(event_dict: dict, events_id: uuid.UUID | None = None):
    job = get_current_job()
    if job is None:
        raise BaseError(message="No job found")

    r = job.connection

    if events_id is None:
        events_id = job.id

    r.xadd(
        f"job:{events_id}:events",
        {"data": json.dumps(event_dict, default=str)},
    )


async def delete_job(job_id: uuid.UUID, session: AsyncSession) -> None:
    logger.info(f"Deleting job: {job_id}")

    try:
        job_query = select(Job).where(Job.id == job_id)
        job_result = await session.execute(job_query)
        job = job_result.scalar_one_or_none()

        if not job:
            logger.warning(f"Job {job_id} not found")
            raise ResourceNotFoundError(f"Job {job_id} not found")

        logger.info(f"Deleting job {job_id}")
        await session.delete(job)

        await session.commit()
        logger.info(f"Job {job_id} deleted successfully")

    except ResourceNotFoundError:
        await session.rollback()
        raise
    except Exception:
        logger.exception(f"Error deleting job {job_id}")
        await session.rollback()
        raise
