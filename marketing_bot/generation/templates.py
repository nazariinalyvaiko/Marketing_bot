from __future__ import annotations

from typing import Any, Dict
from jinja2 import Template

EMAIL_TEMPLATE = Template(
	"""
	Write a high-converting marketing email for the following campaign.
	- Product: {{ product_name }}
	- Segment: {{ segment_name }}
	- Goal: {{ goal }}
	- Offer: {{ offer }}
	- Tone: {{ tone }}
	- Constraints: 120-180 words, include clear CTA and subject line.

	Return as:
	Subject: <subject line>
	Body:
	<email body>
	""".strip()
)

SOCIAL_POST_TEMPLATE = Template(
	"""
	Create a social media post for {{ platform }} about {{ product_name }} targeting {{ segment_name }}.
	Goal: {{ goal }}
	Offer: {{ offer }}
	Tone: {{ tone }}
	Constraints: 40-80 words, include one emoji and a short CTA.
	Include 3 hashtags.
	""".strip()
)


def render_prompt(template: Template, context: Dict[str, Any]) -> str:
	return template.render(**context)
