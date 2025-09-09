from __future__ import annotations

from pathlib import Path
from typing import Optional

import click
import pandas as pd
from dotenv import load_dotenv

from marketing_bot.generation.openai_client import generate_marketing_text
from marketing_bot.generation.templates import (EMAIL_TEMPLATE,
                                                SOCIAL_POST_TEMPLATE,
                                                render_prompt)
from marketing_bot.segmentation.rfm import score_rfm
from marketing_bot.senders.email_sender import EmailMessage, send_email
from marketing_bot.senders.social_sender import SocialPost, send_social_post
from marketing_bot.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)


@click.group()
def cli() -> None:
    """Marketing Bot CLI"""
    pass


@cli.command()
@click.option(
    "--customers-csv",
    type=click.Path(exists=True, path_type=Path),
    default=Path("data/customers.csv"),
)
@click.option(
    "--top-n", type=int, default=5, help="Top N customers per segment to preview"
)
@click.option("--show", is_flag=True, help="Print sample of scored data")
def segment(customers_csv: Path, top_n: int, show: bool) -> None:
    """Run RFM segmentation and save to data/segmented.csv"""
    df = pd.read_csv(customers_csv)
    scored = score_rfm(df)
    out_path = customers_csv.parent / "segmented.csv"
    scored.to_csv(out_path, index=False)
    logger.info(f"Saved segmented data to {out_path}")
    if show:
        for seg, grp in scored.groupby("segment"):
            logger.info(f"Segment={seg} count={len(grp)}")
            logger.info(grp.head(top_n).to_string(index=False))


@cli.command()
@click.option("--segment-name", type=str, default="champions")
@click.option("--product-name", type=str, default="Pro Widget 3000")
@click.option("--goal", type=str, default="Drive conversions for summer sale")
@click.option("--offer", type=str, default="20% off for 72 hours")
@click.option(
    "--tone",
    type=click.Choice(["friendly", "professional", "playful", "urgent"]),
    default="professional",
)
@click.option("--to", "to_email", type=str, default="customer@example.com")
@click.option("--platform", type=str, default="twitter")
@click.option("--preview", is_flag=True, help="Preview only without sending")
@click.option("--kind", type=click.Choice(["email", "social", "both"]), default="both")
@click.option("--model", type=str, default=None)
@click.option("--max-tokens", type=int, default=300)
def generate(
    segment_name: str,
    product_name: str,
    goal: str,
    offer: str,
    tone: str,
    to_email: str,
    platform: str,
    preview: bool,
    kind: str,
    model: Optional[str],
    max_tokens: int,
) -> None:
    """Generate email/social content and optionally send (dry-run by default)."""
    ctx = {
        "segment_name": segment_name,
        "product_name": product_name,
        "goal": goal,
        "offer": offer,
        "tone": tone,
        "platform": platform,
    }
    if kind in ("email", "both"):
        email_prompt = render_prompt(EMAIL_TEMPLATE, ctx)
        email_content = generate_marketing_text(
            email_prompt, model=model, max_tokens=max_tokens
        )
        subject, body = _split_email(email_content)
        logger.info(f"Email Subject: {subject}")
        if preview:
            logger.info(body)
        else:
            send_email(EmailMessage(subject=subject, body=body, to=to_email))
    if kind in ("social", "both"):
        social_prompt = render_prompt(SOCIAL_POST_TEMPLATE, ctx)
        social_content = generate_marketing_text(
            social_prompt, model=model, max_tokens=max_tokens
        )
        if preview:
            logger.info(social_content)
        else:
            send_social_post(SocialPost(platform=platform, content=social_content))


def _split_email(content: str) -> tuple[str, str]:
    lines = [line.strip("\n") for line in content.splitlines() if line.strip()]
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


if __name__ == "__main__":
    cli()
