from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd

from marketing_bot.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EmailContact:
    """Email contact with segmentation data."""

    email: str
    name: Optional[str] = None
    segment: Optional[str] = None
    customer_id: Optional[str] = None
    recency_days: Optional[int] = None
    frequency: Optional[int] = None
    monetary_value: Optional[float] = None


class EmailDatabase:
    """Manage email contacts and campaigns."""

    def __init__(self, data_dir: Path = Path("data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.contacts_file = self.data_dir / "email_contacts.csv"
        self.campaigns_file = self.data_dir / "campaigns.csv"

        # Initialize files if they don't exist
        self._init_files()

    def _init_files(self) -> None:
        """Initialize database files if they don't exist."""
        if not self.contacts_file.exists():
            contacts_df = pd.DataFrame(
                columns=[
                    "email",
                    "name",
                    "segment",
                    "customer_id",
                    "recency_days",
                    "frequency",
                    "monetary_value",
                ]
            )
            contacts_df.to_csv(self.contacts_file, index=False)
            logger.info(f"Created contacts file: {self.contacts_file}")

        if not self.campaigns_file.exists():
            campaigns_df = pd.DataFrame(
                columns=[
                    "campaign_id",
                    "name",
                    "subject",
                    "body",
                    "segment",
                    "created_at",
                    "sent_count",
                    "success_count",
                ]
            )
            campaigns_df.to_csv(self.campaigns_file, index=False)
            logger.info(f"Created campaigns file: {self.campaigns_file}")

    def load_contacts(self) -> List[EmailContact]:
        """Load all contacts from database."""
        try:
            df = pd.read_csv(self.contacts_file)
            contacts = []
            for _, row in df.iterrows():
                contact = EmailContact(
                    email=row["email"],
                    name=row.get("name"),
                    segment=row.get("segment"),
                    customer_id=row.get("customer_id"),
                    recency_days=row.get("recency_days"),
                    frequency=row.get("frequency"),
                    monetary_value=row.get("monetary_value"),
                )
                contacts.append(contact)
            logger.info(f"Loaded {len(contacts)} contacts from database")
            return contacts
        except Exception as e:
            logger.error(f"Failed to load contacts: {e}")
            return []

    def add_contacts_from_csv(
        self, csv_file: Path, segment: Optional[str] = None
    ) -> int:
        """Add contacts from CSV file to database."""
        try:
            df = pd.read_csv(csv_file)

            # Validate required columns
            if "email" not in df.columns:
                raise ValueError("CSV file must contain 'email' column")

            # Add segment if provided
            if segment:
                df["segment"] = segment

            # Load existing contacts
            existing_df = (
                pd.read_csv(self.contacts_file)
                if self.contacts_file.exists()
                else pd.DataFrame()
            )

            # Merge with existing data (avoid duplicates)
            if not existing_df.empty:
                df = pd.concat([existing_df, df], ignore_index=True)
                df = df.drop_duplicates(subset=["email"], keep="last")

            # Save updated contacts
            df.to_csv(self.contacts_file, index=False)

            added_count = (
                len(df) - len(existing_df) if not existing_df.empty else len(df)
            )
            logger.info(f"Added {added_count} contacts to database")
            return added_count

        except Exception as e:
            logger.error(f"Failed to add contacts from CSV: {e}")
            return 0

    def get_contacts_by_segment(self, segment: str) -> List[EmailContact]:
        """Get contacts filtered by segment."""
        contacts = self.load_contacts()
        return [c for c in contacts if c.segment == segment]

    def get_contact_count_by_segment(self) -> Dict[str, int]:
        """Get contact count grouped by segment."""
        contacts = self.load_contacts()
        segment_counts = {}
        for contact in contacts:
            segment = contact.segment or "unknown"
            segment_counts[segment] = segment_counts.get(segment, 0) + 1
        return segment_counts

    def save_campaign(
        self,
        campaign_id: str,
        name: str,
        subject: str,
        body: str,
        segment: str,
        sent_count: int = 0,
        success_count: int = 0,
    ) -> None:
        """Save campaign to database."""
        try:
            import datetime

            campaign_data = {
                "campaign_id": campaign_id,
                "name": name,
                "subject": subject,
                "body": body,
                "segment": segment,
                "created_at": datetime.datetime.now().isoformat(),
                "sent_count": sent_count,
                "success_count": success_count,
            }

            # Load existing campaigns
            if self.campaigns_file.exists():
                campaigns_df = pd.read_csv(self.campaigns_file)
            else:
                campaigns_df = pd.DataFrame()

            # Add new campaign
            new_campaign_df = pd.DataFrame([campaign_data])
            campaigns_df = pd.concat([campaigns_df, new_campaign_df], ignore_index=True)

            # Save updated campaigns
            campaigns_df.to_csv(self.campaigns_file, index=False)
            logger.info(f"Saved campaign: {name} (ID: {campaign_id})")

        except Exception as e:
            logger.error(f"Failed to save campaign: {e}")

    def get_campaigns(self) -> pd.DataFrame:
        """Get all campaigns from database."""
        try:
            if self.campaigns_file.exists():
                return pd.read_csv(self.campaigns_file)
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Failed to load campaigns: {e}")
            return pd.DataFrame()
