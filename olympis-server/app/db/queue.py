import redis
from rq import Queue

from app.config import REDIS_DB, REDIS_HOST, REDIS_PORT
from app.logger import get_logger

logger = get_logger(__name__)


def init_queue() -> Queue:
    logger.info(
        f"Initializing queue connection to {REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )
    try:
        client = redis.Redis.from_url(
            f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}", decode_responses=False
        )
        queue = Queue(connection=client)
        logger.info("Queue connection established successfully")
        return queue
    except Exception:
        logger.exception("Failed to initialize queue connection")
        raise
