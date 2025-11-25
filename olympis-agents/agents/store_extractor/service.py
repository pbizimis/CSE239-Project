import logging
import time
import traceback

from rq import get_current_job

from agents.shared.utils import update_job_progress

logger = logging.getLogger(__name__)


def extract_store_data(html: str | None = None, events_id: str | None = None):
    try:
        update_job_progress("Extracting data", events_id)
        job = get_current_job()
        if job is None:
            raise

        if html is None:
            dependencies = job.fetch_dependencies()
            html = dependencies[0].result

        result = {"agent": 1}
        time.sleep(4)

        return result
    except Exception:
        logger.error("extract_store_data failed:\n%s", traceback.format_exc())
        raise  # preserve failure status for RQ
