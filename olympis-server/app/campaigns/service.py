import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.campaigns.models import Campaign, CampaignMetaData, CampaignState
from app.exceptions import ResourceNotFoundError, UnauthorizedError
from app.jobs.models import Job
from app.logger import get_logger
from app.user.models import AssociationUserStore

from .schema import CreateCampaignRequest, CreateCampaignResponse

logger = get_logger(__name__)


async def create_campaign(
    user_id: uuid.UUID,
    store_id: uuid.UUID,
    campaign_data: CreateCampaignRequest,
    session: AsyncSession,
) -> CreateCampaignResponse:
    logger.info(
        f"Creating new campaign for user: {user_id}, store: {store_id}, campaign name: {campaign_data.name}"
    )

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

        setup_job = Job()
        session.add(setup_job)
        await session.flush()
        logger.info(f"Job created with id: {setup_job.id}")

        new_campaign = Campaign(
            name=campaign_data.name,
            url=campaign_data.url,
            status=CampaignState.setup,
            store_id=store_id,
            job_id=setup_job.id,
        )

        session.add(new_campaign)
        await session.commit()
        logger.info(
            f"Campaign {new_campaign.id} created successfully for user {user_id}"
        )

        return CreateCampaignResponse(
            id=new_campaign.id,
            name=new_campaign.name,
            url=new_campaign.url,
            store_id=new_campaign.store_id,
            setup_job_id=setup_job.id,
        )
    except (ResourceNotFoundError, UnauthorizedError):
        await session.rollback()
        raise
    except Exception:
        logger.exception(
            f"Error creating campaign for user: {user_id}, store: {store_id}"
        )
        await session.rollback()
        raise


async def complete_campaign_setup(
    campaign_id: uuid.UUID, extracted_data: dict, session: AsyncSession
) -> None:
    logger.info(f"Completing setup for campaign: {campaign_id}")
    logger.info(f"Extracted data to save {extracted_data}")

    try:
        campaign_query = (
            select(Campaign)
            .where(Campaign.id == campaign_id)
            .options(selectinload(Campaign.campaign_meta))
        )
        campaign_result = await session.execute(campaign_query)
        campaign = campaign_result.scalar_one_or_none()

        if not campaign:
            logger.warning(f"Campaign {campaign_id} not found")
            raise ResourceNotFoundError(f"Campaign {campaign_id} not found")

        campaign.status = CampaignState.active
        campaign.job_id = None

        if campaign.campaign_meta:
            logger.info(f"Updating existing metadata for campaign {campaign_id}")
            campaign.campaign_meta.data = extracted_data
        else:
            logger.info(f"Creating new metadata for campaign {campaign_id}")
            campaign_metadata = CampaignMetaData(
                campaign_id=campaign_id, data=extracted_data
            )
            session.add(campaign_metadata)
            campaign.campaign_meta = campaign_metadata

        await session.commit()
        logger.info(f"Campaign setup completed successfully for campaign {campaign_id}")

    except ResourceNotFoundError:
        await session.rollback()
        raise
    except Exception:
        logger.exception(f"Error completing campaign setup for campaign {campaign_id}")
        await session.rollback()
        raise
