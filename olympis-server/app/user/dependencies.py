from typing import Annotated

from fastapi import Depends

from app.db.dependencies import AuthDependency, DatabaseDependency
from app.logger import get_logger
from app.user.schema import GetUser
from app.user.service import create_user_db, get_user_db

logger = get_logger(__name__)


async def get_user_dp(
    auth_payload: AuthDependency,
    session: DatabaseDependency,
):
    logger.info(f"Getting user dependency for auth payload: {auth_payload.get('sub')}")

    try:
        user = await get_user_db(auth_payload, session)
        logger.info(f"User dependency resolved: {user.id}")
        return user
    except Exception:
        await session.rollback()

        clerk_id = "testuser"
        email = "testuser@gmail.com"
        await create_user_db(clerk_id, email, session)
        user = await get_user_db(auth_payload, session)
        logger.info(f"User dependency resolved: {user.id}")
        return user


UserDependency = Annotated[GetUser, Depends(get_user_dp)]
