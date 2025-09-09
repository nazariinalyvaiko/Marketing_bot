from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import UUID

from marketing_bot.utils.logger import get_logger

logger = get_logger(__name__)


class MetricsTracker:
    """Track campaign metrics and performance."""

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.metrics_file = self.data_dir / "metrics.json"

        if not self.metrics_file.exists():
            self.metrics_file.write_text("[]")

    async def track_campaign_execution(
        self,
        campaign_id: UUID,
        customer_id: str,
        success: bool,
        error: Optional[str] = None,
    ) -> None:
        """Track campaign execution metrics."""
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "campaign_id": str(campaign_id),
            "customer_id": customer_id,
            "success": success,
            "error": error,
        }

        metrics = self._load_metrics()
        metrics.append(metric)
        self._save_metrics(metrics)

        logger.info(
            f"Tracked execution: campaign={campaign_id}, customer={customer_id}, success={success}"
        )

    async def track_content_generation(
        self,
        campaign_id: UUID,
        content_type: str,
        generation_time_ms: int,
        success: bool,
    ) -> None:
        """Track content generation performance."""
        metric = {
            "timestamp": datetime.utcnow().isoformat(),
            "campaign_id": str(campaign_id),
            "content_type": content_type,
            "generation_time_ms": generation_time_ms,
            "success": success,
        }

        metrics = self._load_metrics()
        metrics.append(metric)
        self._save_metrics(metrics)

    async def get_campaign_metrics(self, campaign_id: UUID) -> dict:
        """Get metrics for a specific campaign."""
        metrics = self._load_metrics()
        campaign_metrics = [m for m in metrics if m["campaign_id"] == str(campaign_id)]

        total_executions = len(campaign_metrics)
        successful_executions = len(
            [m for m in campaign_metrics if m.get("success", False)]
        )
        success_rate = (
            (successful_executions / total_executions * 100)
            if total_executions > 0
            else 0
        )

        return {
            "campaign_id": str(campaign_id),
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": round(success_rate, 2),
            "metrics": campaign_metrics,
        }

    def _load_metrics(self) -> list:
        """Load metrics from file."""
        try:
            return json.loads(self.metrics_file.read_text())
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            return []

    def _save_metrics(self, metrics: list) -> None:
        """Save metrics to file."""
        try:
            self.metrics_file.write_text(json.dumps(metrics, indent=2, default=str))
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
