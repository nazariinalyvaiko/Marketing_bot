from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv
from marketing_bot.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


@dataclass
class SocialPost:
	platform: str
	content: str
	account: str | None = None

def send_social_post(post: SocialPost) -> None:
	"""Stub social post sender (dry-run). Replace with platform-specific Selenium flows."""
	dry_run = os.getenv("SENDER_DRY_RUN", "true").lower() == "true"
	if dry_run:
		logger.info(f"[dry-run] Social post to platform={post.platform} account={post.account or 'default'}\n{post.content}")
		return
	logger.warning("Real social posting not implemented. Set SENDER_DRY_RUN=true to suppress this warning.")
