from __future__ import annotations

from revops.analytics.revenue import churn_reasons, mrr_waterfall, revenue_kpis
from revops.analytics.utils import FilterSet


def test_revenue_kpis_counts(revenue_df):
    kpis = revenue_kpis(revenue_df, FilterSet())
    assert kpis["total_mrr"] >= 0
    assert 0 <= kpis["churn_rate"] <= 100


def test_mrr_waterfall_columns(revenue_df):
    waterfall = mrr_waterfall(revenue_df, FilterSet())
    expected_cols = {"period", "starting_mrr", "new_mrr", "expansion_mrr", "contraction_mrr", "churn_mrr", "ending_mrr"}
    assert expected_cols <= set(waterfall.columns)
    assert len(waterfall) > 0


def test_churn_reasons_sorted(revenue_df):
    churn = churn_reasons(revenue_df, FilterSet())
    if not churn.empty:
        counts = churn["count"].tolist()
        assert counts == sorted(counts, reverse=True)
