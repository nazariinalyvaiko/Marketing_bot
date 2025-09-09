from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

import pandas as pd
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from marketing_bot.metrics.tracker import MetricsTracker
from marketing_bot.repositories.campaign_repository import CampaignRepository
from marketing_bot.services.campaign_service import CampaignService
from marketing_bot.utils.logger import get_logger

logger = get_logger(__name__)

app = FastAPI(
    title="Marketing Bot API",
    description="Advanced marketing automation with AI-powered content generation",
    version="2.0.0",
)


# Dependency injection
def get_campaign_repo() -> CampaignRepository:
    return CampaignRepository()


def get_metrics_tracker() -> MetricsTracker:
    return MetricsTracker()


def get_campaign_service(
    repo: CampaignRepository = Depends(get_campaign_repo),
    metrics: MetricsTracker = Depends(get_metrics_tracker),
) -> CampaignService:
    return CampaignService(repo, metrics)


# Request/Response models
class CampaignCreateRequest(BaseModel):
    name: str
    campaign_type: str
    segment_name: str
    product_name: str
    goal: str
    offer: str
    tone: str = "professional"
    platform: str = "twitter"


class CampaignExecuteRequest(BaseModel):
    customer_data: List[Dict[str, Any]]


class SegmentRequest(BaseModel):
    customers: List[Dict[str, Any]]


class GenerateRequest(BaseModel):
    segment_name: str
    product_name: str
    goal: str
    offer: str
    tone: str = "professional"
    platform: str = "twitter"
    kind: str = "both"
    model: Optional[str] = None
    max_tokens: int = 300


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "version": "2.0.0"}


@app.get("/metrics")
def get_metrics(
    metrics: MetricsTracker = Depends(get_metrics_tracker),
) -> Dict[str, Any]:
    """Get system metrics."""
    return {"message": "Metrics endpoint - implement as needed"}


@app.post("/campaigns")
async def create_campaign(
    request: CampaignCreateRequest,
    service: CampaignService = Depends(get_campaign_service),
):
    """Create a new campaign."""
    try:
        from marketing_bot.models.campaign import Campaign, CampaignType

        campaign = Campaign(
            name=request.name,
            campaign_type=CampaignType(request.campaign_type),
            segment_name=request.segment_name,
            product_name=request.product_name,
            goal=request.goal,
            offer=request.offer,
            tone=request.tone,
            platform=request.platform,
        )

        result = await service.create_campaign(campaign)
        return {
            "campaign": result.model_dump(),
            "message": "Campaign created successfully",
        }

    except Exception as e:
        logger.error(f"Failed to create campaign: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/campaigns")
async def list_campaigns(
    status: Optional[str] = None,
    service: CampaignService = Depends(get_campaign_service),
):
    """List campaigns."""
    try:
        from marketing_bot.models.campaign import CampaignStatus

        status_filter = CampaignStatus(status) if status else None
        campaigns = await service.list_campaigns(status_filter)
        return {"campaigns": [c.model_dump() for c in campaigns]}

    except Exception as e:
        logger.error(f"Failed to list campaigns: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/campaigns/{campaign_id}/execute")
async def execute_campaign(
    campaign_id: UUID,
    request: CampaignExecuteRequest,
    service: CampaignService = Depends(get_campaign_service),
):
    """Execute a campaign."""
    try:
        results = await service.execute_campaign(campaign_id, request.customer_data)
        return {
            "results": [r.model_dump() for r in results],
            "message": f"Campaign executed for {len(results)} customers",
        }

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to execute campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/segment")
def segment(req: SegmentRequest) -> List[Dict[str, Any]]:
    """Legacy segmentation endpoint."""
    try:
        from marketing_bot.segmentation.rfm import score_rfm

        df = pd.DataFrame(req.customers)
        scored = score_rfm(df)
        return scored.to_dict(orient="records")

    except Exception as e:
        logger.error(f"Segmentation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/generate")
def generate(req: GenerateRequest) -> Dict[str, Any]:
    """Legacy generation endpoint."""
    try:
        from marketing_bot.generation.openai_client import generate_marketing_text
        from marketing_bot.generation.templates import (
            EMAIL_TEMPLATE,
            SOCIAL_POST_TEMPLATE,
            render_prompt,
        )

        ctx = req.model_dump()
        email_content = None
        social_content = None

        if req.kind in ("email", "both"):
            email_prompt = render_prompt(EMAIL_TEMPLATE, ctx)
            email_content = generate_marketing_text(
                email_prompt, model=req.model, max_tokens=req.max_tokens
            )

        if req.kind in ("social", "both"):
            social_prompt = render_prompt(SOCIAL_POST_TEMPLATE, ctx)
            social_content = generate_marketing_text(
                social_prompt, model=req.model, max_tokens=req.max_tokens
            )

        return {"email": email_content, "social": social_content}

    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
