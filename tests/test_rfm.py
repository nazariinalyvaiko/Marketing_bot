from __future__ import annotations

import pandas as pd

from marketing_bot.segmentation.rfm import score_rfm


def test_score_rfm_outputs_columns():
    df = pd.DataFrame(
        [
            {
                "customer_id": "A",
                "recency_days": 5,
                "frequency": 10,
                "monetary_value": 1000,
            },
            {
                "customer_id": "B",
                "recency_days": 30,
                "frequency": 3,
                "monetary_value": 200,
            },
            {
                "customer_id": "C",
                "recency_days": 100,
                "frequency": 1,
                "monetary_value": 50,
            },
        ]
    )
    res = score_rfm(df)
    for col in ["R", "F", "M", "RFM_Score", "segment"]:
        assert col in res.columns
    assert len(res) == 3
