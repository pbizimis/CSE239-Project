from enum import Enum
import uuid

from pydantic import BaseModel


class Lang(str, Enum):
    de = "DE"
    en = "EN"


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    onboardingComplete: bool
    businessName: str = ""
    industry: str = ""


class GetUser(BaseModel):
    id: uuid.UUID
    external_id: str
