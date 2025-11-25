import uuid

from fastapi import APIRouter, Request
from rq import Queue

from app.db.dependencies import DatabaseDependency
from app.logger import get_logger
from app.stores.jobs import get_store_metadata
from app.user.dependencies import UserDependency

from .schema import (
    CreateStoreRequest,
    CreateStoreResponse,
    StoreDataResponse,
    StoresResponse,
)
from .service import create_store, delete_store, get_store_data_for_user, get_stores_db

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{store_id}/data", response_model=StoreDataResponse)
async def get_store_data(
    store_id: str, user: UserDependency, session: DatabaseDependency
) -> StoreDataResponse:
    logger.info(
        f"Store data requested for user: {user.id}, store_id: {store_id}"
    )
    try:
        store_uuid = uuid.UUID(store_id)
    except ValueError:
        logger.warning(f"Invalid store_id format: {store_id}")
        raise ValueError("Invalid store ID format")

    try:
        result = await get_store_data_for_user(user.id, store_uuid, session)
        logger.info(
            f"Store data retrieved successfully for user: {user.id}, store_id: {store_id}"
        )
        return result
    except Exception:
        logger.exception(
            f"Error getting store data for user: {user.id}, store_id: {store_id}"
        )
        raise


@router.get("/", response_model=StoresResponse)
async def get_stores(
    user: UserDependency, session: DatabaseDependency
) -> StoresResponse:
    logger.info(f"Stores requested for user: {user.id}")
    try:
        stores = await get_stores_db(user.id, session)
        logger.info(f"Stores retrieved successfully for user: {user.id}")
        return StoresResponse(stores=stores)
    except Exception:
        logger.exception(f"Error getting stores for user: {user.id}")
        raise


@router.post("/", response_model=CreateStoreResponse)
async def create_new_store(
    request: Request,
    store_data: CreateStoreRequest,
    user: UserDependency,
    session: DatabaseDependency,
) -> CreateStoreResponse:
    logger.info(
        f"Store creation requested by user: {user.id}, store name: {store_data.name}"
    )

    store = await create_store(user.id, store_data, session)

    # TODO change https addition
    q: Queue = request.app.state.app_state.queue
    q.enqueue(
        get_store_metadata,
        "https://" + store_data.url,
        store.id,
        store.setup_job_id,
        job_id=str(store.setup_job_id),
    )

    logger.info(f"Queued metadata job {store.setup_job_id} for store {store.id}")

    return store


@router.delete("/{store_id}")
async def delete_store_endpoint(
    store_id: str,
    user: UserDependency,
    session: DatabaseDependency,
) -> dict:
    logger.info(f"Store deletion requested by user: {user.id}, store_id: {store_id}")

    try:
        store_uuid = uuid.UUID(store_id)
    except ValueError:
        logger.warning(f"Invalid store_id format: {store_id}")
        raise ValueError("Invalid store ID format")

    await delete_store(user.id, store_uuid, session)

    return {"message": "Store deleted successfully", "store_id": store_id}
