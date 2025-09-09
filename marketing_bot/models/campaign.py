from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"


class CampaignType(str, Enum):
    EMAIL = "email"
    SOCIAL = "social"
    BOTH = "both"


class Campaign(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    campaign_type: CampaignType
    segment_name: str
    product_name: str
    goal: str
    offer: str
    tone: str = "professional"
    platform: str = "twitter"
    status: CampaignStatus = CampaignStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class CampaignResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    campaign_id: UUID
    customer_id: str
    content_type: str  # email, social
    content: str
    sent_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "sent"  # sent, failed, bounced
    metrics: Optional[dict] = None  # opens, clicks, conversions
