import uuid
from pydantic import BaseModel

from app.campaigns.models import CampaignState


class CampaignSummary(BaseModel):
    id: uuid.UUID
    name: str


class CreateCampaignRequest(BaseModel):
    name: str
    url: str
    store_id: uuid.UUID


class CreateCampaignResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    store_id: uuid.UUID
    setup_job_id: uuid.UUID
