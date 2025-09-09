from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from marketing_bot.models.campaign import Campaign, CampaignResult, CampaignStatus
from marketing_bot.utils.logger import get_logger

logger = get_logger(__name__)


class CampaignRepository:
    """Simple file-based repository for campaigns and results."""
    
    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.campaigns_file = self.data_dir / "campaigns.json"
        self.results_file = self.data_dir / "campaign_results.json"
        
        # Initialize files if they don't exist
        if not self.campaigns_file.exists():
            self.campaigns_file.write_text("[]")
        if not self.results_file.exists():
            self.results_file.write_text("[]")

    async def create(self, campaign: Campaign) -> Campaign:
        """Create a new campaign."""
        campaigns = self._load_campaigns()
        campaigns.append(campaign.model_dump())
        self._save_campaigns(campaigns)
        logger.info(f"Created campaign: {campaign.name} ({campaign.id})")
        return campaign

    async def get_by_id(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID."""
        campaigns = self._load_campaigns()
        for campaign_data in campaigns:
            if campaign_data["id"] == str(campaign_id):
                return Campaign(**campaign_data)
        return None

    async def list(self, status: Optional[CampaignStatus] = None) -> List[Campaign]:
        """List campaigns, optionally filtered by status."""
        campaigns = self._load_campaigns()
        result = [Campaign(**data) for data in campaigns]
        
        if status:
            result = [c for c in result if c.status == status]
        
        return result

    async def update(self, campaign: Campaign) -> Campaign:
        """Update an existing campaign."""
        campaigns = self._load_campaigns()
        for i, campaign_data in enumerate(campaigns):
            if campaign_data["id"] == str(campaign.id):
                campaigns[i] = campaign.model_dump()
                break
        self._save_campaigns(campaigns)
        logger.info(f"Updated campaign: {campaign.name} ({campaign.id})")
        return campaign

    async def save_results(self, results: List[CampaignResult]) -> None:
        """Save campaign results."""
        existing_results = self._load_results()
        new_results = [result.model_dump() for result in results]
        existing_results.extend(new_results)
        self._save_results(existing_results)
        logger.info(f"Saved {len(results)} campaign results")

    async def get_results(self, campaign_id: UUID) -> List[CampaignResult]:
        """Get results for a specific campaign."""
        results = self._load_results()
        campaign_results = [
            CampaignResult(**data) for data in results 
            if data["campaign_id"] == str(campaign_id)
        ]
        return campaign_results

    def _load_campaigns(self) -> List[dict]:
        """Load campaigns from file."""
        try:
            return json.loads(self.campaigns_file.read_text())
        except Exception as e:
            logger.error(f"Failed to load campaigns: {e}")
            return []

    def _save_campaigns(self, campaigns: List[dict]) -> None:
        """Save campaigns to file."""
        try:
            self.campaigns_file.write_text(json.dumps(campaigns, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to save campaigns: {e}")

    def _load_results(self) -> List[dict]:
        """Load results from file."""
        try:
            return json.loads(self.results_file.read_text())
        except Exception as e:
            logger.error(f"Failed to load results: {e}")
            return []

    def _save_results(self, results: List[dict]) -> None:
        """Save results to file."""
        try:
            self.results_file.write_text(json.dumps(results, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to save results: {e}")
