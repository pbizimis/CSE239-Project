import uuid

from fastapi import APIRouter, Request
from rq import Queue

from app.db.dependencies import DatabaseDependency
from app.logger import get_logger
from app.user.dependencies import UserDependency

from .jobs import get_campaign_metadata
from .schema import CreateCampaignRequest, CreateCampaignResponse
from .service import create_campaign

logger = get_logger(__name__)
router = APIRouter()


@router.get("/{store_id}")
async def get_campaigns(
    store_id: str, user: UserDependency, session: DatabaseDependency
):
    logger.info(f"Campaign data requested for store: {store_id} by user: {user.id}")
    try:
        # TODO: Implement actual campaign fetching logic
        logger.info(f"Processing campaign request for store: {store_id}")
        return {"S_ID": store_id}
    except Exception:
        logger.exception(f"Error getting campaigns for store: {store_id}")
        raise


@router.post("/", response_model=CreateCampaignResponse)
async def create_new_campaign(
    request: Request,
    campaign_data: CreateCampaignRequest,
    user: UserDependency,
    session: DatabaseDependency,
) -> CreateCampaignResponse:
    logger.info(
        f"Campaign creation requested by user: {user.id}, campaign name: {campaign_data.name}, store: {campaign_data.store_id}"
    )

    try:
        store_uuid = uuid.UUID(str(campaign_data.store_id))
    except ValueError:
        logger.warning(f"Invalid store_id format: {campaign_data.store_id}")
        raise ValueError("Invalid store ID format")

    campaign = await create_campaign(user.id, store_uuid, campaign_data, session)

    # TODO change https addition
    q: Queue = request.app.state.app_state.queue
    q.enqueue(
        get_campaign_metadata,
        "https://" + campaign_data.url,
        campaign.id,
        campaign.setup_job_id,
        job_id=str(campaign.setup_job_id),
    )

    logger.info(f"Queued metadata job {campaign.setup_job_id} for store {campaign.id}")

    return campaign
