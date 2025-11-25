import json

from rq import get_current_job


def update_job_progress(message: str, events_id: str | None):
    job = get_current_job()
    if job is None:
        raise

    r = job.connection
    if events_id is None:
        events_id = job.id

    progress = {"progress": message}

    r.xadd(
        f"job:{events_id}:events",
        {"data": json.dumps(progress, default=str)},
    )
