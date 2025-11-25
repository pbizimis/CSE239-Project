import uuid
from typing import List

from pydantic import BaseModel

from app.campaigns.schema import CampaignSummary
from app.stores.models import StoreState


class CreateStoreRequest(BaseModel):
    name: str
    url: str


class CreateStoreResponse(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    setup_job_id: uuid.UUID


class StoreSummary(BaseModel):
    id: uuid.UUID
    name: str
    url: str
    status: StoreState
    job_id: uuid.UUID | None


class StoreDataResponse(BaseModel):
    currentStore: StoreSummary
    stores: List[StoreSummary]
    campaigns: List[CampaignSummary]


class StoresResponse(BaseModel):
    stores: List[StoreSummary]
