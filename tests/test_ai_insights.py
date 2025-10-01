from __future__ import annotations

from revops.ai.insights import generate_insights
from revops.analytics.utils import FilterSet


def test_generate_insights_returns_messages(marketing_df, pipeline_df, revenue_df):
    insights = generate_insights(
        marketing_df=marketing_df,
        pipeline_df=pipeline_df,
        revenue_df=revenue_df,
        filters=FilterSet(),
    )
    assert len(insights) > 0
    assert all(insight.message for insight in insights)
