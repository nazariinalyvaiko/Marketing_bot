from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from marketing_bot.utils.logger import get_logger

logger = get_logger(__name__)


@dataclass(frozen=True)
class RfmConfig:
    recency_bins: int = 5
    frequency_bins: int = 5
    monetary_bins: int = 5


SegmentLabel = Literal[
    "champions",
    "loyal",
    "potential_loyalist",
    "new_customers",
    "promising",
    "needs_attention",
    "about_to_sleep",
    "at_risk",
    "hibernating",
    "lost",
]


def score_rfm(df: pd.DataFrame, cfg: RfmConfig = RfmConfig()) -> pd.DataFrame:
    """Compute RFM scores and labels.

    DataFrame requires columns: customer_id, recency_days, frequency, monetary_value
    """
    required = {"customer_id", "recency_days", "frequency", "monetary_value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")

    logger.debug("Scoring RFM...")
    out = df.copy()
    # Lower recency is better → invert rank by using qcut on negative recency
    out["R"] = (
        pd.qcut(-out["recency_days"], cfg.recency_bins, labels=False, duplicates="drop")
        + 1
    )
    out["F"] = (
        pd.qcut(out["frequency"], cfg.frequency_bins, labels=False, duplicates="drop")
        + 1
    )
    out["M"] = (
        pd.qcut(
            out["monetary_value"], cfg.monetary_bins, labels=False, duplicates="drop"
        )
        + 1
    )
    out["RFM_Score"] = out[["R", "F", "M"]].sum(axis=1)
    out["segment"] = out.apply(_label_segment, axis=1)
    return out


def _label_segment(row: pd.Series) -> SegmentLabel:
    # Simple heuristic mapping
    if row["R"] >= 4 and row["F"] >= 4 and row["M"] >= 4:
        return "champions"
    if row["R"] >= 4 and row["F"] >= 3:
        return "loyal"
    if row["R"] >= 3 and row["F"] >= 3:
        return "potential_loyalist"
    if row["R"] >= 4 and row["F"] <= 2:
        return "new_customers"
    if row["R"] == 3 and row["F"] <= 2:
        return "promising"
    if row["R"] == 3 and row["F"] == 3:
        return "needs_attention"
    if row["R"] == 2 and row["F"] >= 3:
        return "about_to_sleep"
    if row["R"] == 2 and row["F"] <= 2:
        return "at_risk"
    if row["R"] == 1 and row["F"] >= 2:
        return "hibernating"
    return "lost"
