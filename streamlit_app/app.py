"""Streamlit entrypoint for the RevOps Control Center dashboard."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd
import plotly.express as px
import streamlit as st

# Ensure project root and src directory are importable when running via `streamlit run`
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"

for path in (ROOT_DIR, SRC_DIR):
    str_path = str(path)
    if str_path not in sys.path:
        sys.path.insert(0, str_path)

from revops.analytics.marketing import (
    channel_performance,
    funnel_breakdown,
    marketing_kpis,
    trend_timeseries,
)
from revops.analytics.pipeline import owner_performance, pipeline_kpis, stage_distribution, stuck_deals
from revops.analytics.revenue import churn_reasons, mrr_waterfall, revenue_kpis, segment_breakdown
from revops.analytics.utils import FilterSet
from revops.ai.insights import generate_insights
from revops.data import get_marketing_df, get_pipeline_df, get_revenue_df
from streamlit_app.theme import (
    AVAILABLE_THEMES,
    DEFAULT_THEME_NAME,
    DEFAULT_PLOTLY_CONFIG,
    apply_theme,
)

st.set_page_config(page_title="RevOps Control Center", layout="wide")


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Return cached marketing, pipeline, and revenue datasets."""
    return (
        get_marketing_df().copy(),
        get_pipeline_df().copy(),
        get_revenue_df().copy(),
    )


def build_filters(marketing_df: pd.DataFrame) -> FilterSet:
    """Render global filters in the sidebar and return the current selection."""
    all_dates = pd.to_datetime(marketing_df["date"]).dt.date
    min_date, max_date = all_dates.min(), all_dates.max()

    st.sidebar.markdown(
        """
        <div class="sidebar-title">Signal Controls</div>
        <p class="sidebar-subtitle">Tune cohorts, regions, and activity windows to reframe performance narratives.</p>
        """,
        unsafe_allow_html=True,
    )

    start = st.sidebar.date_input(
        "Start date",
        value=min_date,
        min_value=min_date,
        max_value=max_date,
        key="global_start",
    )
    end = st.sidebar.date_input(
        "End date",
        value=max_date,
        min_value=min_date,
        max_value=max_date,
        key="global_end",
    )

    segments = sorted(marketing_df["segment"].unique())
    selected_segments = st.sidebar.multiselect(
        "Segments",
        options=segments,
        default=segments,
        key="segments_filter",
    )

    channels = sorted(marketing_df["channel"].unique())
    selected_channels = st.sidebar.multiselect(
        "Channels",
        options=channels,
        default=channels[:4],
        key="channels_filter",
    )

    geo = sorted(marketing_df["geo"].unique())
    selected_geo = st.sidebar.multiselect(
        "Regions",
        options=geo,
        default=geo,
        key="geo_filter",
    )

    return FilterSet(
        start_date=start if isinstance(start, date) else min_date,
        end_date=end if isinstance(end, date) else max_date,
        segments=selected_segments or None,
        channels=selected_channels or None,
        geo=selected_geo or None,
    )


def select_theme() -> str:
    """Render a sidebar selector and apply the chosen brand theme."""

    options = list(AVAILABLE_THEMES.keys())
    default_index = st.session_state.get("theme_index", options.index(DEFAULT_THEME_NAME))
    default_index = max(0, min(default_index, len(options) - 1))

    theme_name = st.sidebar.selectbox(
        "Visual theme",
        options=options,
        index=default_index,
        key="theme_selector",
        help="Switch between modern dark, light, and the original neon styling.",
    )

    st.session_state["theme_index"] = options.index(theme_name)
    apply_theme(theme_name)
    st.sidebar.caption("Theme changes apply instantly for this session.")
    st.sidebar.divider()
    return theme_name


def render_metric_grid(metrics: Sequence[tuple[str, str]], columns: int = 3) -> None:
    """Render Streamlit metrics in responsive rows of the specified width."""

    for index in range(0, len(metrics), columns):
        chunk = metrics[index : index + columns]
        column_group = st.columns(columns)
        for idx, column in enumerate(column_group):
            if idx < len(chunk):
                label, value = chunk[idx]
                column.metric(label, value)
            else:
                column.empty()


def render_marketing_tab(marketing_df: pd.DataFrame, filters: FilterSet) -> None:
    """Display marketing KPIs, charts, and tabular insights."""
    st.subheader("Marketing Funnel Overview")

    kpis = marketing_kpis(marketing_df, filters)
    render_metric_grid(
        [
            ("Total Spend", f"${kpis['total_spend']:,.0f}"),
            ("Leads", f"{kpis['total_leads']:,}"),
            ("MQLs", f"{kpis['total_mqls']:,}"),
            ("SQLs", f"{kpis['total_sqls']:,}"),
            ("Avg CAC", f"${kpis['avg_cac']:,.0f}"),
            ("Avg ROI", f"{kpis['avg_roi']:.1f}%"),
        ]
    )

    channel_data = channel_performance(marketing_df, filters)
    funnel_data = funnel_breakdown(marketing_df, filters)
    trends = trend_timeseries(marketing_df, filters)

    left, right = st.columns(2)

    channel_chart = px.bar(
        channel_data,
        x="channel",
        y="spend",
        color="roi_percentage",
        title="Channel Spend vs ROI",
        labels={"roi_percentage": "ROI %"},
    )
    channel_chart.update_layout(
        xaxis_title="",
        yaxis_title="Spend (USD)",
        coloraxis_colorbar=dict(title="ROI %"),
    )
    channel_chart.update_traces(marker=dict(line=dict(color="rgba(255,255,255,0.12)", width=1)))
    left.plotly_chart(channel_chart, config=DEFAULT_PLOTLY_CONFIG)

    funnel_chart = px.funnel(funnel_data, x="count", y="stage", title="Funnel Breakdown")
    funnel_chart.update_layout(xaxis_title="Volume", yaxis_title="", margin=dict(t=70, l=60, r=30))
    right.plotly_chart(funnel_chart, config=DEFAULT_PLOTLY_CONFIG)

    trend_chart = px.area(
        trends,
        x="date",
        y=["leads", "mqls", "sqls"],
        title="Weekly Performance Trends",
    )
    trend_chart.update_layout(yaxis_title="Volume", xaxis_title="Week")
    st.plotly_chart(trend_chart, config=DEFAULT_PLOTLY_CONFIG)

    st.dataframe(channel_data, width="stretch")


def render_pipeline_tab(pipeline_df: pd.DataFrame, filters: FilterSet) -> None:
    """Display pipeline health, stage distribution, and rep performance."""
    st.subheader("Sales Pipeline Health")

    kpis = pipeline_kpis(pipeline_df, filters)
    render_metric_grid(
        [
            ("Total Pipeline", f"${kpis['total_pipeline']:,.0f}"),
            ("Weighted Pipeline", f"${kpis['weighted_pipeline']:,.0f}"),
            ("Avg Deal Size", f"${kpis['avg_deal_size']:,.0f}"),
            ("Win Rate", f"{kpis['win_rate']:.1f}%"),
            ("Velocity", f"${kpis['velocity']:,.0f}/day"),
        ]
    )

    stages = stage_distribution(pipeline_df, filters)
    stage_chart = px.bar(
        stages,
        x="stage",
        y="amount",
        color="deals",
        title="Stage Distribution",
    )
    stage_chart.update_layout(xaxis_title="", yaxis_title="Pipeline Amount (USD)")
    stage_chart.update_traces(marker=dict(line=dict(color="rgba(255,255,255,0.1)", width=1)))
    st.plotly_chart(stage_chart, config=DEFAULT_PLOTLY_CONFIG)

    owners = owner_performance(pipeline_df, filters)
    owner_chart = px.bar(
        owners,
        x="owner",
        y="total_amount",
        color="win_rate",
        title="Rep Performance",
        labels={"total_amount": "Total Amount", "win_rate": "Win Rate %"},
    )
    owner_chart.update_layout(xaxis_title="", yaxis_title="Total Closed (USD)", legend=dict(title="Win Rate %"))
    st.plotly_chart(owner_chart, config=DEFAULT_PLOTLY_CONFIG)

    stuck = stuck_deals(pipeline_df, filters=filters)
    st.markdown("### Stuck Deals (>45 days, $50k+)")
    stuck_table = stuck[["deal_id", "owner", "stage", "amount", "days_in_stage"]].copy()
    if not stuck_table.empty:
        stuck_table["amount"] = stuck_table["amount"].map(lambda value: f"${value:,.0f}")
    st.dataframe(stuck_table, width="stretch")


def render_revenue_tab(revenue_df: pd.DataFrame, filters: FilterSet) -> None:
    """Display revenue retention metrics and churn analysis."""
    st.subheader("Revenue & Retention")

    kpis = revenue_kpis(revenue_df, filters)
    render_metric_grid(
        [
            ("Total MRR", f"${kpis['total_mrr']:,.0f}"),
            ("Total ARR", f"${kpis['total_arr']:,.0f}"),
            ("Avg NRR", f"{kpis['avg_nrr']:.1f}%"),
            ("Churn Rate", f"{kpis['churn_rate']:.1f}%"),
        ],
        columns=2,
    )

    segments = segment_breakdown(revenue_df, filters)
    segment_chart = px.treemap(
        segments,
        path=["segment"],
        values="mrr",
        color="expansion",
        title="MRR by Segment",
    )
    segment_chart.update_layout(margin=dict(t=70, l=0, r=0, b=0))
    st.plotly_chart(segment_chart, config=DEFAULT_PLOTLY_CONFIG)

    waterfall = mrr_waterfall(revenue_df, filters)
    waterfall_chart = px.bar(
        waterfall,
        x="period",
        y=["starting_mrr", "new_mrr", "expansion_mrr", "contraction_mrr", "churn_mrr", "ending_mrr"],
        title="MRR Waterfall",
    )
    waterfall_chart.update_layout(barmode="relative", xaxis_title="", yaxis_title="MRR (USD)")
    st.plotly_chart(waterfall_chart, config=DEFAULT_PLOTLY_CONFIG)

    churn = churn_reasons(revenue_df, filters)
    st.markdown("### Churn Reasons")
    churn_table = churn.copy()
    if not churn_table.empty:
        if "churn_mrr" in churn_table:
            churn_table["churn_mrr"] = churn_table["churn_mrr"].map(lambda v: f"${v:,.0f}")
        if "share" in churn_table:
            churn_table["share"] = churn_table["share"].map(lambda v: f"{v:.1f}%")
    st.dataframe(churn_table, width="stretch")


def render_ai_tab(
    marketing_df: pd.DataFrame,
    pipeline_df: pd.DataFrame,
    revenue_df: pd.DataFrame,
    filters: FilterSet,
) -> None:
    """Display automated insights with confidence indicators."""
    st.subheader("AI Co-Pilot Insights")

    insights = generate_insights(
        marketing_df=marketing_df,
        pipeline_df=pipeline_df,
        revenue_df=revenue_df,
        filters=filters,
    )

    for insight in insights:
        with st.container():
            st.markdown(
                f"""
                <div class="insight-card insight-card--{insight.category.lower()}">
                    <span class="insight-chip">{insight.category.upper()}</span>
                    <p class="insight-message">{insight.message}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.progress(insight.confidence)
            if insight.data_points:
                st.json(insight.data_points)
            st.divider()


def main() -> None:
    """Application entry point."""

    theme_name = select_theme()
    marketing_df, pipeline_df, revenue_df = load_data()
    filters = build_filters(marketing_df)

    st.markdown(
        f"""
        <div class="hero-header">
            <div>
                <p class="hero-eyebrow">RevOps Control Center</p>
                <h1>AI-assisted revenue intelligence</h1>
                <p class="hero-subtitle">Monitor acquisition, pipeline velocity, and retention in a single panoramic workspace powered by automated insights.</p>
                <p class="hero-theme">Active theme · {theme_name}</p>
            </div>
            <div class="hero-badge">
                <span class="hero-badge__pulse"></span>
                <div>
                    <span class="hero-badge__label">Live Sync</span>
                    <span class="hero-badge__meta">Synthetic data refreshed daily</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    marketing_tab, pipeline_tab, revenue_tab, ai_tab = st.tabs(
        ["Marketing", "Pipeline", "Revenue", "AI Co-Pilot"]
    )

    with marketing_tab:
        render_marketing_tab(marketing_df, filters)

    with pipeline_tab:
        render_pipeline_tab(pipeline_df, filters)

    with revenue_tab:
        render_revenue_tab(revenue_df, filters)

    with ai_tab:
        render_ai_tab(marketing_df, pipeline_df, revenue_df, filters)


if __name__ == "__main__":
    main()
