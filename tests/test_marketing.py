from __future__ import annotations

from datetime import date

import pandas as pd

from revops.analytics.marketing import channel_performance, marketing_kpis, trend_timeseries
from revops.analytics.utils import FilterSet


def test_marketing_kpis_total_spend_positive(marketing_df):
    kpis = marketing_kpis(marketing_df, FilterSet())
    assert kpis["total_spend"] > 0
    assert kpis["total_leads"] > 0


def test_channel_performance_respects_filters(marketing_df):
    first_channel = marketing_df["channel"].iloc[0]
    filters = FilterSet(channels=[first_channel])
    channels = channel_performance(marketing_df, filters)
    assert channels["channel"].unique().tolist() == [first_channel]


def test_trend_timeseries_weekly_rollup(marketing_df):
    filters = FilterSet(start_date=date(2024, 1, 1), end_date=date(2024, 3, 31))
    trends = trend_timeseries(marketing_df, filters)
    assert (trends["date"].diff().dropna().unique() >= pd.Timedelta(days=7)).all()
    assert set(trends.columns) == {"date", "leads", "mqls", "sqls"}
