from __future__ import annotations

from marketing_bot.generation.openai_client import generate_marketing_text
from marketing_bot.generation.templates import EMAIL_TEMPLATE, render_prompt
from marketing_bot.main import _split_email


def test_offline_generation_returns_mock_email():
    ctx = {
        "segment_name": "champions",
        "product_name": "Pro Widget 3000",
        "goal": "Drive conversions for summer sale",
        "offer": "20% off for 72 hours",
        "tone": "professional",
    }
    prompt = render_prompt(EMAIL_TEMPLATE, ctx)
    content = generate_marketing_text(prompt, max_tokens=100)
    subject, body = _split_email(content)
    assert subject
    assert "MOCK" in subject or "Marketing Bot" in body
