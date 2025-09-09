from __future__ import annotations

import asyncio
import uuid
from pathlib import Path
from typing import Dict, Optional

from marketing_bot.database.email_database import EmailDatabase
from marketing_bot.metrics.tracker import MetricsTracker
from marketing_bot.senders.email_sender import EmailMessage, send_email
from marketing_bot.utils.logger import get_logger

logger = get_logger(__name__)


class EmailCampaignService:
    """Service for managing email campaigns and bulk sending."""

    def __init__(self, data_dir: Path = Path("data")):
        self.db = EmailDatabase(data_dir)
        self.metrics = MetricsTracker(data_dir)

    async def create_campaign(
        self,
        name: str,
        subject: str,
        body: str,
        segment: str,
        preview_only: bool = True,
    ) -> str:
        """Create a new email campaign."""
        campaign_id = str(uuid.uuid4())

        # Save campaign to database
        self.db.save_campaign(
            campaign_id=campaign_id,
            name=name,
            subject=subject,
            body=body,
            segment=segment,
        )

        logger.info(f"Created campaign: {name} (ID: {campaign_id})")
        return campaign_id

    async def send_campaign(
        self, campaign_id: str, max_emails: Optional[int] = None, dry_run: bool = True
    ) -> Dict[str, int]:
        """Send campaign to all contacts in the segment."""
        try:
            # Get campaign details
            campaigns_df = self.db.get_campaigns()
            campaign = campaigns_df[campaigns_df["campaign_id"] == campaign_id]

            if campaign.empty:
                raise ValueError(f"Campaign {campaign_id} not found")

            campaign_data = campaign.iloc[0]
            segment = campaign_data["segment"]
            subject = campaign_data["subject"]
            body = campaign_data["body"]

            # Get contacts for this segment
            contacts = self.db.get_contacts_by_segment(segment)

            if not contacts:
                logger.warning(f"No contacts found for segment: {segment}")
                return {"sent": 0, "success": 0, "failed": 0}

            # Limit contacts if max_emails specified
            if max_emails:
                contacts = contacts[:max_emails]

            logger.info(
                f"Sending campaign to {len(contacts)} contacts in segment '{segment}'"
            )

            sent_count = 0
            success_count = 0
            failed_count = 0

            # Send emails
            for contact in contacts:
                try:
                    # Create email message
                    msg = EmailMessage(
                        subject=subject,
                        body=body,
                        to=contact.email,
                        from_name=contact.name or "Marketing Bot",
                    )

                    # Send email
                    send_email(msg)
                    sent_count += 1
                    success_count += 1

                    # Track metrics
                    await self.metrics.track_campaign_execution(
                        campaign_id=campaign_id,
                        customer_id=contact.customer_id or contact.email,
                        success=True,
                    )

                    logger.info(f"Sent email to {contact.email}")

                    # Small delay to avoid overwhelming the server
                    if not dry_run:
                        await asyncio.sleep(0.1)

                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send email to {contact.email}: {e}")

                    # Track failed execution
                    await self.metrics.track_campaign_execution(
                        campaign_id=campaign_id,
                        customer_id=contact.customer_id or contact.email,
                        success=False,
                        error=str(e),
                    )

            # Update campaign statistics
            self._update_campaign_stats(campaign_id, sent_count, success_count)

            result = {
                "sent": sent_count,
                "success": success_count,
                "failed": failed_count,
            }

            logger.info(f"Campaign completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Failed to send campaign: {e}")
            return {"sent": 0, "success": 0, "failed": 0}

    def _update_campaign_stats(
        self, campaign_id: str, sent_count: int, success_count: int
    ) -> None:
        """Update campaign statistics in database."""
        try:
            campaigns_df = self.db.get_campaigns()
            if not campaigns_df.empty:
                mask = campaigns_df["campaign_id"] == campaign_id
                campaigns_df.loc[mask, "sent_count"] = sent_count
                campaigns_df.loc[mask, "success_count"] = success_count
                campaigns_df.to_csv(self.db.campaigns_file, index=False)
        except Exception as e:
            logger.error(f"Failed to update campaign stats: {e}")

    def get_campaign_stats(self) -> Dict[str, any]:
        """Get overall campaign statistics."""
        try:
            campaigns_df = self.db.get_campaigns()
            if campaigns_df.empty:
                return {"total_campaigns": 0, "total_sent": 0, "total_success": 0}

            total_campaigns = len(campaigns_df)
            total_sent = campaigns_df["sent_count"].sum()
            total_success = campaigns_df["success_count"].sum()

            return {
                "total_campaigns": total_campaigns,
                "total_sent": total_sent,
                "total_success": total_success,
                "success_rate": (
                    (total_success / total_sent * 100) if total_sent > 0 else 0
                ),
            }
        except Exception as e:
            logger.error(f"Failed to get campaign stats: {e}")
            return {"total_campaigns": 0, "total_sent": 0, "total_success": 0}

    def get_contact_stats(self) -> Dict[str, int]:
        """Get contact statistics by segment."""
        return self.db.get_contact_count_by_segment()
