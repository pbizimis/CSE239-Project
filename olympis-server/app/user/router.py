from fastapi import APIRouter

from app.logger import get_logger
from app.user.dependencies import UserDependency
from app.user.schema import GetUser

logger = get_logger(__name__)
router = APIRouter()


@router.get("/profile", response_model=GetUser)
async def read_profile(user: UserDependency):
    logger.info(f"Profile requested for user: {user.id}")
    try:
        return user
    except Exception as e:
        logger.exception(f"Error retrieving profile for user: {user.id}")
        raise
