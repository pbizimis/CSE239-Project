import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.campaigns.models import Campaign
from app.exceptions import ResourceNotFoundError, UnauthorizedError
from app.jobs.models import Job
from app.logger import get_logger
from app.stores.models import Store, StoreMetaData, StoreState
from app.user.models import AssociationUserStore, StoreRole

from .schema import (
    CampaignSummary,
    CreateStoreRequest,
    CreateStoreResponse,
    StoreDataResponse,
    StoreSummary,
)

logger = get_logger(__name__)


async def get_stores_db(user_id: uuid.UUID, session: AsyncSession) -> list[StoreSummary]:
    logger.info(f"Getting all stores for user: {user_id}")

    try:
        stores_query = (
            select(AssociationUserStore)
            .where(AssociationUserStore.user_id == user_id)
            .options(selectinload(AssociationUserStore.store))
        )
        stores_result = await session.execute(stores_query)
        store_associations = stores_result.scalars().all()

        store_summaries = []
        for assoc in store_associations:
            store: Store = assoc.store
            store_summaries.append(
                StoreSummary(
                    id=store.id,
                    name=store.name,
                    url=store.url,
                    status=store.status,
                    job_id=store.job_id,
                )
            )

        logger.info(f"Found {len(store_summaries)} stores for user: {user_id}")
        return store_summaries

    except Exception:
        logger.exception(f"Error getting stores for user: {user_id}")
        raise


async def get_store_data_for_user(
    user_id: uuid.UUID, store_id: uuid.UUID, session: AsyncSession
) -> StoreDataResponse:
    logger.info(f"Getting store data for user: {user_id}, store: {store_id}")

    try:
        stores = await get_stores_db(user_id, session)
        if not stores:
            logger.warning(f"User {user_id} has no stores")
            raise ResourceNotFoundError("No stores found for user")

        selected_store = next((store for store in stores if store.id == store_id), None)
        if selected_store is None:
            logger.warning(
                f"Store {store_id} not found or not accessible for user {user_id}"
            )
            raise ResourceNotFoundError("Store not found")

        logger.info(f"Fetching campaigns for store: {store_id}")
        campaigns_query = (
            select(Campaign)
            .where(Campaign.store_id == store_id)
            .order_by(Campaign.created_at.desc())
        )
        campaigns_result = await session.execute(campaigns_query)
        campaigns = campaigns_result.scalars().all()

        campaign_summaries = [
            CampaignSummary(
                id=campaign.id,
                name=campaign.name,
            )
            for campaign in campaigns
        ]

        logger.info(f"Store data prepared successfully for user: {user_id}")
        return StoreDataResponse(
            currentStore=selected_store,
            stores=stores,
            campaigns=campaign_summaries,
        )
    except Exception:
        logger.exception(
            f"Error getting store data for user: {user_id}, store: {store_id}"
        )
        raise


async def create_store(
    user_id: uuid.UUID, store_data: CreateStoreRequest, session: AsyncSession
) -> CreateStoreResponse:
    logger.info(
        f"Creating new store for user: {user_id}, store name: {store_data.name}"
    )

    try:
        setup_job = Job()
        session.add(setup_job)
        await session.flush()
        logger.info(f"Job created with id: {setup_job.id}")

        new_store = Store(
            name=store_data.name,
            url=store_data.url,
            status=StoreState.setup,
            job_id=setup_job.id,
        )
        session.add(new_store)
        await session.flush()
        logger.info(
            f"Store created with id: {new_store.id}, linked to job: {setup_job.id}"
        )

        user_store_association = AssociationUserStore(
            user_id=user_id, store_id=new_store.id, role=StoreRole.owner
        )
        session.add(user_store_association)
        logger.info(f"User {user_id} associated as owner of store {new_store.id}")

        await session.commit()
        logger.info(f"Store {new_store.id} created successfully for user {user_id}")

        # Return the created store as StoreSummary and the job ID
        return CreateStoreResponse(
            id=new_store.id,
            name=new_store.name,
            url=new_store.url,
            setup_job_id=setup_job.id,
        )
    except Exception:
        logger.exception(f"Error creating store for user: {user_id}")
        await session.rollback()
        raise


async def delete_store(
    user_id: uuid.UUID, store_id: uuid.UUID, session: AsyncSession
) -> None:
    logger.info(f"Deleting store {store_id} for user: {user_id}")

    try:
        # Check if the store exists and user has permission
        association_query = select(AssociationUserStore).where(
            AssociationUserStore.user_id == user_id,
            AssociationUserStore.store_id == store_id,
        )
        association_result = await session.execute(association_query)
        association = association_result.scalar_one_or_none()

        if not association:
            logger.warning(f"User {user_id} does not have access to store {store_id}")
            raise ResourceNotFoundError(f"Store {store_id} not found")

        if association.role != StoreRole.owner:
            logger.warning(f"User {user_id} is not owner of store {store_id}")
            raise UnauthorizedError("Only store owners can delete stores")

        # Get the store object
        store_query = select(Store).where(Store.id == store_id)
        store_result = await session.execute(store_query)
        store = store_result.scalar_one_or_none()

        if not store:
            logger.warning(f"Store {store_id} not found")
            raise ResourceNotFoundError(f"Store {store_id} not found")

        # Delete the store using ORM (this will trigger cascades)
        logger.info(f"Deleting store {store_id}")
        await session.delete(store)

        await session.commit()
        logger.info(f"Store {store_id} deleted successfully by user {user_id}")

    except (ResourceNotFoundError, UnauthorizedError):
        await session.rollback()
        raise
    except Exception:
        logger.exception(f"Error deleting store {store_id} for user {user_id}")
        await session.rollback()
        raise


async def complete_store_setup(store_id: uuid.UUID, extracted_data: dict, session: AsyncSession) -> None:
    logger.info(f"Completing setup for store: {store_id}")
    logger.info(f"Extracted data to save {extracted_data}")

    try:
        store_query = select(Store).where(Store.id == store_id).options(selectinload(Store.store_meta))
        store_result = await session.execute(store_query)
        store = store_result.scalar_one_or_none()

        if not store:
            logger.warning(f"Store {store_id} not found")
            raise ResourceNotFoundError(f"Store {store_id} not found")

        logger.info(f"Setting store {store_id} status to active")
        store.status = StoreState.active
        store.job_id = None

        if store.store_meta:
            logger.info(f"Updating existing metadata for store {store_id}")
            store.store_meta.data = extracted_data
        else:
            logger.info(f"Creating new metadata for store {store_id}")
            store_metadata = StoreMetaData(store_id=store_id, data=extracted_data)
            session.add(store_metadata)
            store.store_meta = store_metadata


        await session.commit()
        logger.info(f"Store setup completed successfully for store {store_id}")

    except ResourceNotFoundError:
        await session.rollback()
        raise
    except Exception:
        logger.exception(f"Error completing store setup for store {store_id}")
        await session.rollback()
        raise
