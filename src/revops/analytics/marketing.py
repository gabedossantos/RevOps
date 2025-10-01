from __future__ import annotations

from dataclasses import asdict
from typing import Dict, Optional

import pandas as pd

from .utils import FilterSet, _safe_divide


def marketing_kpis(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> Dict[str, float]:
    filtered = filters.apply(df) if filters else df

    totals = {
        "total_spend": float(filtered["spend"].sum()),
        "total_leads": int(filtered["leads"].sum()),
        "total_mqls": int(filtered["MQLs"].sum()),
        "total_sqls": int(filtered["SQLs"].sum()),
        "avg_cac": float(filtered["CAC"].mean()) if not filtered.empty else 0.0,
        "avg_roi": float(filtered["ROI"].mean()) if not filtered.empty else 0.0,
    }

    return totals


def channel_performance(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df) if filters else df

    grouped = (
        filtered.groupby("channel")
        .agg(
            spend=("spend", "sum"),
            leads=("leads", "sum"),
            mqls=("MQLs", "sum"),
            sqls=("SQLs", "sum"),
            opportunities=("opportunities", "sum"),
            closed_won=("closed_won", "sum"),
            avg_cac=("CAC", "mean"),
            avg_roi=("ROI", "mean"),
        )
        .reset_index()
    )

    grouped["conversion_rate"] = grouped.apply(
        lambda row: _safe_divide(row["closed_won"], row["leads"]) * 100,
        axis=1,
    )
    grouped["roi_percentage"] = grouped["avg_roi"]
    grouped["cac"] = grouped["avg_cac"]

    return grouped.sort_values("spend", ascending=False)


def funnel_breakdown(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df) if filters else df

    totals = {
        "Leads": filtered["leads"].sum(),
        "MQLs": filtered["MQLs"].sum(),
        "SQLs": filtered["SQLs"].sum(),
        "Opportunities": filtered["opportunities"].sum(),
        "Closed Won": filtered["closed_won"].sum(),
    }

    return pd.DataFrame({"stage": totals.keys(), "count": totals.values()})


def trend_timeseries(df: pd.DataFrame, filters: Optional[FilterSet] = None) -> pd.DataFrame:
    filtered = filters.apply(df) if filters else df
    filtered = filtered.copy()
    filtered["date"] = pd.to_datetime(filtered["date"])

    daily = (
        filtered.groupby(pd.Grouper(key="date", freq="W"))
        .agg(
            leads=("leads", "sum"),
            mqls=("MQLs", "sum"),
            sqls=("SQLs", "sum"),
        )
        .reset_index()
    )

    daily["date"] = daily["date"].dt.normalize()
    return daily


__all__ = [
    "FilterSet",
    "marketing_kpis",
    "channel_performance",
    "funnel_breakdown",
    "trend_timeseries",
]
