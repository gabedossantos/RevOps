from __future__ import annotations

from typing import Dict, Optional

import pandas as pd

from .utils import FilterSet, _safe_divide


def pipeline_kpis(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> Dict[str, float]:
    filtered = filters.apply(df, date_column="created_at") if filters else df

    open_deals = filtered[filtered["status"] == "Open"]
    closed_won = filtered[filtered["stage"] == "Closed_Won"]
    closed_lost = filtered[filtered["stage"] == "Closed_Lost"]

    total_pipeline = float(open_deals["amount"].sum())
    weighted_pipeline = float(open_deals["expected_value"].sum())
    avg_deal_size = float(filtered["amount"].mean()) if not filtered.empty else 0.0
    win_rate = _safe_divide(len(closed_won), len(closed_won) + len(closed_lost))

    avg_days = open_deals["days_in_stage"].replace(0, pd.NA).dropna()
    avg_days_value = float(avg_days.mean()) if not avg_days.empty else 1.0
    velocity = _safe_divide(open_deals["expected_value"].sum(), avg_days_value or 1.0)

    return {
        "total_pipeline": total_pipeline,
        "weighted_pipeline": weighted_pipeline,
        "avg_deal_size": avg_deal_size,
        "win_rate": win_rate * 100,
        "velocity": float(velocity),
    }


def stage_distribution(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df, date_column="created_at") if filters else df
    return (
        filtered.groupby("stage")
        .agg(deals=("deal_id", "count"), amount=("amount", "sum"))
        .reset_index()
        .sort_values("amount", ascending=False)
    )


def owner_performance(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df, date_column="created_at") if filters else df
    grouped = (
        filtered.groupby("owner")
        .agg(
            deals=("deal_id", "count"),
            total_amount=("amount", "sum"),
            won_deals=("stage", lambda x: (x == "Closed_Won").sum()),
            lost_deals=("stage", lambda x: (x == "Closed_Lost").sum()),
            avg_cycle=("days_in_stage", "mean"),
        )
        .reset_index()
    )
    grouped["win_rate"] = grouped.apply(
        lambda row: _safe_divide(row["won_deals"], row["won_deals"] + row["lost_deals"]) * 100,
        axis=1,
    )
    return grouped.sort_values("total_amount", ascending=False)


def stuck_deals(
    df: pd.DataFrame,
    *,
    filters: Optional[FilterSet] = None,
    stage_threshold: int = 45,
    min_amount: float = 50000,
) -> pd.DataFrame:
    filtered = filters.apply(df, date_column="created_at") if filters else df
    candidates = filtered[filtered["status"] == "Open"]
    stuck = candidates[
        (candidates["days_in_stage"] >= stage_threshold)
        & (candidates["amount"] >= min_amount)
    ]
    return stuck.sort_values("days_in_stage", ascending=False)


__all__ = [
    "FilterSet",
    "pipeline_kpis",
    "stage_distribution",
    "owner_performance",
    "stuck_deals",
]
