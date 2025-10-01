from __future__ import annotations

from revops.analytics.pipeline import owner_performance, pipeline_kpis, stuck_deals
from revops.analytics.utils import FilterSet


def test_pipeline_kpis_has_expected_keys(pipeline_df):
    kpis = pipeline_kpis(pipeline_df, FilterSet())
    assert set(kpis) == {"total_pipeline", "weighted_pipeline", "avg_deal_size", "win_rate", "velocity"}
    assert kpis["total_pipeline"] >= kpis["weighted_pipeline"]


def test_owner_performance_ranks_by_total_amount(pipeline_df):
    perf = owner_performance(pipeline_df, FilterSet())
    assert not perf.empty
    assert perf.iloc[0]["total_amount"] >= perf.iloc[-1]["total_amount"]


def test_stuck_deals_threshold(pipeline_df):
    stuck = stuck_deals(pipeline_df, filters=FilterSet(), stage_threshold=30, min_amount=20000)
    assert (stuck["days_in_stage"] >= 30).all()
    assert (stuck["amount"] >= 20000).all()
