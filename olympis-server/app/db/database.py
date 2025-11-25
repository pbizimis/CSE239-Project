import asyncio
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncGenerator

from pydantic_core import MultiHostUrl
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config import (
    DB_ECHO,
    POSTGRES_DB,
    POSTGRES_PASSWORD,
    POSTGRES_PORT,
    POSTGRES_SERVER,
    POSTGRES_USER,
)
from app.logger import get_logger

logger = get_logger(__name__)


@dataclass(slots=True)
class Database:
    engine: AsyncEngine
    session_maker: async_sessionmaker[AsyncSession]


def _build_db_uri() -> MultiHostUrl:
    logger.info("Building database URI")
    return MultiHostUrl.build(
        scheme="postgresql+asyncpg",
        username=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_SERVER,
        port=int(POSTGRES_PORT),
        path=POSTGRES_DB,
    )


def init_database() -> Database:
    logger.info("Initializing database connection")
    try:
        db_uri = str(_build_db_uri())
        logger.info(
            f"Connecting to database at {POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
        )

        engine = create_async_engine(db_uri, echo=DB_ECHO, future=True)
        session_maker = async_sessionmaker(
            bind=engine, class_=AsyncSession, expire_on_commit=False
        )

        logger.info("Database connection established successfully")
        return Database(engine=engine, session_maker=session_maker)
    except Exception:
        logger.exception("Failed to initialize database connection")
        raise


# database connection for the queue worker
_queue_lock = asyncio.Lock()
_queue_db: Database | None = None


async def get_queue_db_session_maker():
    global _queue_db
    if _queue_db is None:
        async with _queue_lock:
            if _queue_db is None:
                logger.info("Creating RQ worker database engine")
                _queue_db = init_database()
    return _queue_db


@asynccontextmanager
async def get_queue_database_session() -> AsyncGenerator[AsyncSession, None]:
    try:
        database: Database = await get_queue_db_session_maker()
        async with database.session_maker() as async_session:
            logger.info("Database session created successfully")
            yield async_session
            logger.info("Database session closed")
    except Exception:
        logger.exception("Error managing database session")
        raise
