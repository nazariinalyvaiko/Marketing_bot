from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from marketing_bot.generation.openai_client import generate_marketing_text
from marketing_bot.generation.templates import (
    EMAIL_TEMPLATE,
    SOCIAL_POST_TEMPLATE,
    render_prompt,
)
from marketing_bot.metrics.tracker import MetricsTracker
from marketing_bot.models.campaign import (
    Campaign,
    CampaignResult,
    CampaignStatus,
    CampaignType,
)
from marketing_bot.repositories.campaign_repository import CampaignRepository
from marketing_bot.segmentation.rfm import score_rfm
from marketing_bot.senders.email_sender import EmailMessage, send_email
from marketing_bot.senders.social_sender import SocialPost, send_social_post
from marketing_bot.utils.logger import get_logger

logger = get_logger(__name__)


class CampaignService:
    def __init__(
        self, campaign_repo: CampaignRepository, metrics_tracker: MetricsTracker
    ):
        self.campaign_repo = campaign_repo
        self.metrics_tracker = metrics_tracker

    async def create_campaign(self, campaign: Campaign) -> Campaign:
        """Create a new campaign."""
        logger.info(f"Creating campaign: {campaign.name}")
        return await self.campaign_repo.create(campaign)

    async def get_campaign(self, campaign_id: UUID) -> Optional[Campaign]:
        """Get campaign by ID."""
        return await self.campaign_repo.get_by_id(campaign_id)

    async def list_campaigns(
        self, status: Optional[CampaignStatus] = None
    ) -> List[Campaign]:
        """List campaigns, optionally filtered by status."""
        return await self.campaign_repo.list(status=status)

    async def execute_campaign(
        self, campaign_id: UUID, customer_data: List[dict]
    ) -> List[CampaignResult]:
        """Execute campaign for given customer data."""
        campaign = await self.get_campaign(campaign_id)
        if not campaign:
            raise ValueError(f"Campaign {campaign_id} not found")

        if campaign.status != CampaignStatus.ACTIVE:
            raise ValueError(f"Campaign {campaign_id} is not active")

        logger.info(
            f"Executing campaign {campaign.name} for {len(customer_data)} customers"
        )

        # Segment customers
        import pandas as pd

        df = pd.DataFrame(customer_data)
        scored_customers = score_rfm(df)

        results = []

        # Generate and send content for each customer
        for _, customer in scored_customers.iterrows():
            try:
                customer_results = await self._process_customer(campaign, customer)
                results.extend(customer_results)

                # Track metrics
                await self.metrics_tracker.track_campaign_execution(
                    campaign_id=campaign_id,
                    customer_id=customer["customer_id"],
                    success=True,
                )

            except Exception as e:
                logger.error(
                    f"Failed to process customer {customer['customer_id']}: {e}"
                )
                await self.metrics_tracker.track_campaign_execution(
                    campaign_id=campaign_id,
                    customer_id=customer["customer_id"],
                    success=False,
                    error=str(e),
                )

        # Save results
        await self.campaign_repo.save_results(results)
        return results

    async def _process_customer(
        self, campaign: Campaign, customer: dict
    ) -> List[CampaignResult]:
        """Process a single customer for the campaign."""
        results = []

        # Prepare context
        ctx = {
            "segment_name": customer["segment"],
            "product_name": campaign.product_name,
            "goal": campaign.goal,
            "offer": campaign.offer,
            "tone": campaign.tone,
            "platform": campaign.platform,
        }

        # Generate email content
        if campaign.campaign_type in [CampaignType.EMAIL, CampaignType.BOTH]:
            email_prompt = render_prompt(EMAIL_TEMPLATE, ctx)
            email_content = generate_marketing_text(email_prompt, tone=campaign.tone)

            # Send email
            subject, body = self._split_email(email_content)
            msg = EmailMessage(
                subject=subject,
                body=body,
                to=customer.get("email", f"{customer['customer_id']}@example.com"),
            )
            send_email(msg)

            results.append(
                CampaignResult(
                    campaign_id=campaign.id,
                    customer_id=customer["customer_id"],
                    content_type="email",
                    content=email_content,
                )
            )

        # Generate social content
        if campaign.campaign_type in [CampaignType.SOCIAL, CampaignType.BOTH]:
            social_prompt = render_prompt(SOCIAL_POST_TEMPLATE, ctx)
            social_content = generate_marketing_text(social_prompt, tone=campaign.tone)

            # Send social post
            post = SocialPost(platform=campaign.platform, content=social_content)
            send_social_post(post)

            results.append(
                CampaignResult(
                    campaign_id=campaign.id,
                    customer_id=customer["customer_id"],
                    content_type="social",
                    content=social_content,
                )
            )

        return results

    def _split_email(self, content: str) -> tuple[str, str]:
        """Split email content into subject and body."""
        lines = [line.strip() for line in content.splitlines() if line.strip()]
        subject_line = next(
            (line for line in lines if line.lower().startswith("subject:")), ""
        )
        body_lines = [line for line in lines if not line.lower().startswith("subject:")]
        subject = (
            subject_line.split(":", 1)[1].strip()
            if ":" in subject_line
            else "Your Exclusive Offer"
        )
        body = "\n".join(body_lines)
        return subject, body
