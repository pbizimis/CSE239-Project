from typing import Annotated, Any, AsyncGenerator, Dict

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import Database
from app.logger import get_logger

logger = get_logger(__name__)


async def authenticate_request(request: Request) -> Dict[str, Any] | None:
    logger.info(f"Authenticating request to {request.url.path}")
    return {
        "sub": "testuser",
    }


AuthDependency = Annotated[Dict[str, Any], Depends(authenticate_request)]


async def get_database_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    logger.info("Creating database session")
    try:
        database: Database = request.app.state.app_state.database
        async with database.session_maker() as async_session:
            logger.info("Database session created successfully")
            yield async_session
            logger.info("Database session closed")
    except Exception:
        logger.exception("Error managing database session")
        raise


DatabaseDependency = Annotated[AsyncSession, Depends(get_database_session)]


async def get_storage_session():
    logger.info("Getting storage session")
    pass


# StorageDependency


async def get_cache_session():
    logger.info("Getting cache session")
    pass


# CacheDependency
