import asyncio
import uuid

from rq import Queue, get_current_job
from sqlalchemy import JSON

from app.db.database import get_queue_database_session
from app.jobs.service import delete_job, update_job_progress

from .service import complete_campaign_setup


async def async_save_data(
    store_id: uuid.UUID, setup_job_id: uuid.UUID, extracted_data: JSON
):
    async with get_queue_database_session() as session:
        await complete_campaign_setup(store_id, extracted_data, session)
        await delete_job(setup_job_id, session)


def save_data(store_id: uuid.UUID, setup_job_id: uuid.UUID):
    update_job_progress({"progress": "Saving data"}, events_id=setup_job_id)
    job = get_current_job()
    if job is None:
        raise
    deps = job.fetch_dependencies()
    data = deps[0].result
    asyncio.run(async_save_data(store_id, setup_job_id, data))
    update_job_progress({"status": "done"}, events_id=setup_job_id)


def get_campaign_metadata(url: str, campaign_id: uuid.UUID, setup_job_id: uuid.UUID):
    job = get_current_job()

    if job is None:
        raise

    q_crawler = Queue("crawler", connection=job.connection)
    q_agents = Queue("agents", connection=job.connection)
    q = Queue("default", connection=job.connection)

    job_crawl = q_crawler.enqueue("crawler.get_cleaned_html", url, setup_job_id)
    job_agents = q_agents.enqueue(
        "agents.store_extractor.service.extract_store_data",
        None,
        setup_job_id,
        depends_on=job_crawl,
    )
    q.enqueue(save_data, campaign_id, setup_job_id, depends_on=job_agents)
