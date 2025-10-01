from __future__ import annotations

from typing import Dict, Optional

import pandas as pd

from .utils import FilterSet, _safe_divide


def revenue_kpis(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> Dict[str, float]:
    filtered = filters.apply(df, date_column="start_date") if filters else df
    active = filtered[~filtered["churned_flag"]]

    total_mrr = float(active["mrr"].sum())
    total_arr = total_mrr * 12
    avg_nrr = float(active["nrr"].mean()) if not active.empty else 0.0
    churn_rate = _safe_divide(filtered["churned_flag"].sum(), len(filtered)) * 100

    return {
        "total_mrr": total_mrr,
        "total_arr": total_arr,
        "avg_nrr": avg_nrr * 100,
        "churn_rate": churn_rate,
    }


def segment_breakdown(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df, date_column="start_date") if filters else df
    return (
        filtered.groupby("segment")
        .agg(
            customers=("customer_id", "count"),
            mrr=("mrr", "sum"),
            expansion=("expansion_mrr", "sum"),
            contraction=("contraction_mrr", "sum"),
            churned=("churned_flag", "sum"),
        )
        .reset_index()
        .sort_values("mrr", ascending=False)
    )


def mrr_waterfall(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df, date_column="start_date") if filters else df
    data = filtered.copy()
    data["start_date"] = pd.to_datetime(data["start_date"])

    monthly = (
        data.groupby(pd.Grouper(key="start_date", freq="ME"))
        .agg(
            starting_mrr=("mrr", "sum"),
            expansion_mrr=("expansion_mrr", "sum"),
            contraction_mrr=("contraction_mrr", "sum"),
            new_mrr=("new_mrr", "sum"),
            churn_mrr=("mrr", lambda s: s[data.loc[s.index, "churned_flag"]].sum()),
        )
        .reset_index()
    )

    monthly["ending_mrr"] = (
        monthly["starting_mrr"]
        + monthly["expansion_mrr"]
        - monthly["contraction_mrr"]
        + monthly["new_mrr"]
        - monthly["churn_mrr"]
    )
    monthly["period"] = monthly["start_date"].dt.to_period("M").astype(str)

    return monthly[[
        "period",
        "starting_mrr",
        "new_mrr",
        "expansion_mrr",
        "contraction_mrr",
        "churn_mrr",
        "ending_mrr",
    ]]


def churn_reasons(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df, date_column="start_date") if filters else df
    churned = filtered[filtered["churned_flag"] & filtered["churn_reason"].notna()]
    return (
        churned.groupby(["segment", "churn_reason"])
        .agg(count=("customer_id", "count"))
        .reset_index()
        .sort_values("count", ascending=False)
    )


__all__ = [
    "FilterSet",
    "revenue_kpis",
    "segment_breakdown",
    "mrr_waterfall",
    "churn_reasons",
]
