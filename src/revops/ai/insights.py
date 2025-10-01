from __future__ import annotations

from typing import List, Optional

import pandas as pd
from pydantic import BaseModel

from ..analytics.marketing import channel_performance, marketing_kpis
from ..analytics.pipeline import pipeline_kpis, stuck_deals
from ..analytics.revenue import churn_reasons, revenue_kpis
from ..analytics.utils import FilterSet


class Insight(BaseModel):
    category: str
    message: str
    confidence: float
    data_points: Optional[dict] = None


def _normalize_confidence(value: float) -> float:
    return max(0.05, min(value, 0.95))


def marketing_insights(marketing_df: pd.DataFrame, filters: Optional[FilterSet] = None) -> List[Insight]:
    kpis = marketing_kpis(marketing_df, filters)
    channels = channel_performance(marketing_df, filters)

    insights: List[Insight] = []

    if not channels.empty:
        best_channel = channels.iloc[0]
        insights.append(
            Insight(
                category="marketing",
                message=(
                    f"{best_channel['channel']} is driving the highest spend (${best_channel['spend']:,.0f}) "
                    f"with ROI {best_channel['roi_percentage']:.1f}%. Consider reallocating budget toward it."),
                confidence=_normalize_confidence(best_channel["roi_percentage"] / 500),
                data_points={
                    "channel": best_channel["channel"],
                    "roi": best_channel["roi_percentage"],
                    "spend": best_channel["spend"],
                },
            )
        )

        low_conversion = channels.sort_values("conversion_rate").iloc[0]
        insights.append(
            Insight(
                category="marketing",
                message=(
                    f"{low_conversion['channel']} has the lowest lead→close conversion ({low_conversion['conversion_rate']:.1f}%). "
                    "Review campaign targeting or nurturing flows."),
                confidence=0.4,
                data_points={
                    "channel": low_conversion["channel"],
                    "conversion_rate": low_conversion["conversion_rate"],
                },
            )
        )

    if kpis.get("avg_cac", 0) > 0 and kpis.get("avg_roi", 0) < 200:
        insights.append(
            Insight(
                category="marketing",
                message="Average ROI is trending below 200%. Investigate messaging and segmentation to improve efficiency.",
                confidence=0.35,
            )
        )

    return insights


def pipeline_insights(pipeline_df: pd.DataFrame, filters: Optional[FilterSet] = None) -> List[Insight]:
    kpis = pipeline_kpis(pipeline_df, filters)
    stuck = stuck_deals(pipeline_df, filters=filters)

    insights: List[Insight] = []

    if kpis["win_rate"] < 20:
        insights.append(
            Insight(
                category="pipeline",
                message=(
                    f"Win rate at {kpis['win_rate']:.1f}% is below target. Prioritize coaching and deal reviews for late-stage opportunities."),
                confidence=0.45,
            )
        )

    if not stuck.empty:
        total_stuck = stuck["amount"].sum()
        insights.append(
            Insight(
                category="pipeline",
                message=(
                    f"{len(stuck)} deals worth ${total_stuck:,.0f} have been stuck over 45 days. Escalate executive support."),
                confidence=_normalize_confidence(min(0.9, total_stuck / 5_000_000)),
                data_points={
                    "deal_ids": stuck["deal_id"].head(5).tolist(),
                    "total_amount": total_stuck,
                },
            )
        )

    if kpis["velocity"] < 1000:
        insights.append(
            Insight(
                category="pipeline",
                message="Pipeline velocity is low relative to expected value. Re-evaluate stage progression criteria and SLA adherence.",
                confidence=0.3,
            )
        )

    return insights


def revenue_insights(revenue_df: pd.DataFrame, filters: Optional[FilterSet] = None) -> List[Insight]:
    kpis = revenue_kpis(revenue_df, filters)
    churn = churn_reasons(revenue_df, filters)

    insights: List[Insight] = []

    if kpis["churn_rate"] > 5:
        insights.append(
            Insight(
                category="revenue",
                message=(
                    f"Churn rate at {kpis['churn_rate']:.1f}% exceeds comfort threshold. Implement renewal playbooks for at-risk segments."),
                confidence=0.5,
            )
        )

    if not churn.empty:
        top_reason = churn.iloc[0]
        insights.append(
            Insight(
                category="revenue",
                message=(
                    f"Primary churn driver: {top_reason['churn_reason']} ({top_reason['count']} accounts). "
                    "Collaborate with product and success teams on targeted remediation."),
                confidence=0.55,
                data_points={
                    "segment": top_reason["segment"],
                    "reason": top_reason["churn_reason"],
                    "count": int(top_reason["count"]),
                },
            )
        )

    if kpis["avg_nrr"] < 105:
        insights.append(
            Insight(
                category="revenue",
                message="Net revenue retention below 105%. Expand account growth programs and monitor contraction trends closely.",
                confidence=0.35,
            )
        )

    return insights


def generate_insights(
    *,
    marketing_df: pd.DataFrame,
    pipeline_df: pd.DataFrame,
    revenue_df: pd.DataFrame,
    filters: Optional[FilterSet] = None,
) -> List[Insight]:
    insights: List[Insight] = []
    insights.extend(marketing_insights(marketing_df, filters))
    insights.extend(pipeline_insights(pipeline_df, filters))
    insights.extend(revenue_insights(revenue_df, filters))
    return insights


__all__ = [
    "Insight",
    "marketing_insights",
    "pipeline_insights",
    "revenue_insights",
    "generate_insights",
]
