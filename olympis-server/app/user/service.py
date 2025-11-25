from typing import Any, Dict

from fastapi.exceptions import ValidationException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.exceptions import ResourceNotFoundError
from app.logger import get_logger

from .models import User, UserMetaData, UserProfile
from .schema import GetUser

logger = get_logger(__name__)


async def get_user_db(auth_payload: Dict[str, Any], session: AsyncSession) -> GetUser:
    external_id = auth_payload["sub"]
    logger.info(f"Fetching user from database with external_id: {external_id}")

    try:
        row = await session.execute(
            select(User.id, User.external_id).where(User.external_id == external_id)
        )
        found = row.one_or_none()

        if not found:
            logger.warning(f"User not found with external_id: {external_id}")
            raise ResourceNotFoundError("User not found")

        uid, ext = found
        logger.info(f"User found with id: {uid}")
        return GetUser(id=uid, external_id=ext)

    except SQLAlchemyError:
        logger.exception(f"Error fetching user with external_id: {external_id}")
        raise


async def create_user_db(external_id: str, email: str, session: AsyncSession) -> User:
    logger.info(f"Creating new user with external_id: {external_id}, email: {email}")

    try:
        user = User(
            external_id=external_id,
            profile=UserProfile(email=email),
            user_meta=UserMetaData(),
        )

        async with session.begin():
            session.add(user)

        logger.info(f"User created successfully with id: {user.id}")
        return user
    except IntegrityError as e:
        logger.exception(
            f"Integrity error creating user with external_id: {external_id}"
        )
        raise ValidationException(
            "User with external id " + external_id + " could not be created."
        ) from e
    except Exception:
        logger.exception(
            f"Unexpected error creating user with external_id: {external_id}"
        )
        raise
