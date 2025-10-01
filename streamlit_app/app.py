"""Streamlit entrypoint for the RevOps Control Center dashboard."""

from __future__ import annotations

from datetime import date
from html import escape
from textwrap import dedent
from pathlib import Path
from typing import Optional, Sequence

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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


def apply_compact_margins(
    figure,
    *,
    top: int = 60,
    bottom: int = 32,
    left: int = 24,
    right: int = 18,
) -> None:
    """Tighten Plotly layout margins and enforce transparent backgrounds."""

    figure.update_layout(
        margin=dict(t=top, b=bottom, l=left, r=right),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
    )



# --- Marketing Table with Tooltips and Extra Columns ---
MARKETING_COLUMN_TOOLTIPS = {
    "channel": "The marketing channel (e.g., Email, Social, Paid Search).",
    "spend": "Total spend for this channel (in USD).",
    "leads": "Number of leads generated by this channel.",
    "mqls": "Marketing Qualified Leads: leads that meet marketing’s qualification criteria.",
    "sqls": "Sales Qualified Leads: leads that meet sales’ qualification criteria.",
    "opportunities": "Number of sales opportunities created from this channel.",
    "cpl": "Cost per lead (Spend divided by Leads).",
    "cac": "Customer Acquisition Cost: total spend divided by number of customers acquired.",
    "avg_cac": "Average Customer Acquisition Cost for this channel across the filtered period.",
    "avg_roi": "Average Return on Investment generated by this channel over the selected date range.",
    "roi_percentage": "Return on Investment (ROI) percentage.",
    "closed_won": "Total deals closed-won attributed to this channel.",
    "conversion_rate": "Percentage of leads that converted to closed-won deals.",
}

MARKETING_COLUMN_DEFINITIONS: list[tuple[str, str]] = [
    ("channel", "Channel"),
    ("spend", "Spend"),
    ("leads", "Leads"),
    ("mqls", "MQLs"),
    ("sqls", "SQLs"),
    ("opportunities", "Opportunities"),
    ("closed_won", "Closed Won"),
    ("cpl", "CPL"),
    ("cac", "CAC"),
    ("avg_cac", "Avg CAC"),
    ("avg_roi", "Avg ROI"),
    ("roi_percentage", "ROI %"),
    ("conversion_rate", "Conversion %"),
]

DEFAULT_MARKETING_COLUMNS: list[str] = [
    "channel",
    "spend",
    "leads",
    "mqls",
    "sqls",
    "opportunities",
    "cpl",
    "cac",
    "avg_cac",
    "avg_roi",
    "roi_percentage",
]


def render_marketing_table(df: pd.DataFrame, visible_columns: Optional[Sequence[str]] = None) -> None:
    data = df.copy()

    required_columns = {
        "mqls",
        "sqls",
        "opportunities",
        "closed_won",
        "cpl",
        "cac",
        "avg_cac",
        "avg_roi",
        "roi_percentage",
        "conversion_rate",
    }
    for column in required_columns:
        if column not in data.columns:
            data[column] = 0

    column_labels = {key: label for key, label in MARKETING_COLUMN_DEFINITIONS}
    if visible_columns is None:
        column_keys = DEFAULT_MARKETING_COLUMNS
    else:
        column_keys = [key for key in visible_columns if key in column_labels]
        if not column_keys:
            column_keys = DEFAULT_MARKETING_COLUMNS

    data = data[[key for key in column_keys if key in data.columns]]

    def format_cell(key: str, value) -> str:
        if pd.isna(value):
            return "—"
        if key in {"spend", "cpl", "cac", "avg_cac"}:
            return f"${value:,.0f}"
        if key in {"avg_roi", "roi_percentage", "conversion_rate"}:
            return f"{value:.1f}%"
        if key in {"leads", "mqls", "sqls", "opportunities", "closed_won"}:
            return f"{int(value):,}"
        return str(value)

    header_html: list[str] = []
    for key in data.columns:
        label = column_labels.get(key, key.replace("_", " ").title())
        tooltip = MARKETING_COLUMN_TOOLTIPS.get(key, "")
        safe_label = escape(label)
        if tooltip:
            safe_tooltip = escape(tooltip)
            header_html.append(
                (
                    "<th class='marketing-th' title='{tooltip}'>"
                    "<span class='marketing-th__content'>"
                    "<span class='marketing-th__label'>{label}</span>"
                    "<span class='tooltip-icon' title='{tooltip}'>{icon}</span>"
                    "</span>"
                    "</th>"
                ).format(label=safe_label, tooltip=safe_tooltip, icon="&#9432;")
            )
        else:
            header_html.append(
                (
                    "<th class='marketing-th'>"
                    "<span class='marketing-th__content'>{label}</span>"
                    "</th>"
                ).format(label=safe_label)
            )

    body_rows: list[str] = []
    for _, row in data.iterrows():
        cells = []
        for key in data.columns:
            value = format_cell(key, row.get(key, ""))
            cells.append(f"<td class='marketing-td'>{escape(value)}</td>")
        body_rows.append(f"<tr>{''.join(cells)}</tr>")

    table_html = dedent(
        f"""
        <div class='marketing-table__card'>
            <div class='marketing-table__wrapper'>
                <table class='marketing-table'>
                    <thead>
                        <tr>{''.join(header_html)}</tr>
                    </thead>
                    <tbody>
                        {''.join(body_rows)}
                    </tbody>
                </table>
            </div>
        </div>
        """
    ).strip()

    st.markdown(
        dedent(
            """
            <style>
            .marketing-table__card {
                background: var(--brand-surface);
                border: 1px solid var(--brand-border);
                border-radius: var(--brand-radius);
                padding: 0.75rem 0.75rem 0.5rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(18px);
                width: 100%;
                max-width: 100%;
                margin: 0;
                overflow: hidden;
            }
            .marketing-table__wrapper {
                overflow-x: auto;
                width: 100%;
                margin: 0;
                padding-bottom: 0.25rem;
            }
            .marketing-table {
                width: 100%;
                min-width: 960px;
                border-collapse: collapse;
                border-spacing: 0;
            }
            .marketing-th,
            .marketing-td {
                text-align: center;
                vertical-align: middle;
                padding: 8px 12px;
                border-bottom: 1px solid rgba(148, 163, 184, 0.18);
            }
            .marketing-th {
                font-weight: 600;
                white-space: nowrap;
            }
            .marketing-th__content {
                display: inline-flex;
                align-items: center;
                gap: 4px;
            }
            .marketing-th__label {
                display: inline-block;
            }
            .tooltip-icon {
                font-size: 0.68em;
                line-height: 1;
                display: inline-flex;
                align-items: center;
                color: #94a3b8;
                margin-left: 2px;
                cursor: help;
            }
            .marketing-td {
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .marketing-table tbody tr:nth-child(even) {
                background: rgba(148, 163, 184, 0.08);
            }
            .marketing-table tbody tr:hover {
                background: rgba(99, 102, 241, 0.12);
            }
            </style>
            """
        ),
        unsafe_allow_html=True,
    )

    st.markdown(table_html, unsafe_allow_html=True)

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
    funnel_area_data = funnel_data.copy()
    funnel_area_data["value"] = funnel_area_data["count"].astype(float)
    stage_order = {
        "Leads": 0,
        "MQLs": 1,
        "SQLs": 2,
        "Opportunities": 3,
        "Closed Won": 4,
    }
    funnel_area_data["order"] = funnel_area_data["stage"].map(stage_order).fillna(99)
    funnel_area_data.sort_values("order", inplace=True)
    top_value = funnel_area_data["value"].max() or 1.0
    min_ratio = 0.26
    closed_won_mask = funnel_area_data["stage"] == "Closed Won"
    closed_won_actual = (
        float(funnel_area_data.loc[closed_won_mask, "value"].iloc[0])
        if closed_won_mask.any()
        else 0.0
    )
    desired_closed_won_display = (
        max(closed_won_actual, min_ratio * top_value)
        if closed_won_mask.any()
        else 0.0
    )

    offset = 0.0
    if closed_won_mask.any() and closed_won_actual >= 0:
        offset = max(desired_closed_won_display - closed_won_actual, 0.0)

    funnel_area_data["display_value"] = funnel_area_data["value"] + offset
    if closed_won_mask.any():
        funnel_area_data.loc[closed_won_mask, "display_value"] = desired_closed_won_display
    total_display = float(funnel_area_data["display_value"].sum()) or 1.0
    total_actual = float(funnel_area_data["value"].sum()) or 1.0
    funnel_area_data["display_share"] = funnel_area_data["display_value"] / total_display
    funnel_area_data["actual_share"] = funnel_area_data["value"] / total_actual
    funnel_area_data.reset_index(drop=True, inplace=True)

    stage_palette = {
        "Leads": "#c7d2fe",
        "MQLs": "#a5b4fc",
        "SQLs": "#7dd3fc",
        "Opportunities": "#38bdf8",
        "Closed Won": "#0ea5e9",
    }
    gradient_colors = [stage_palette.get(stage, "#38bdf8") for stage in funnel_area_data["stage"]]
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
    apply_compact_margins(channel_chart, top=70)
    left.plotly_chart(channel_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

    funnel_chart = go.Figure(
        go.Funnelarea(
            labels=funnel_area_data["stage"],
            values=funnel_area_data["display_value"],
            customdata=funnel_area_data[["value", "actual_share"]].to_numpy(),
            texttemplate="<b>%{label}</b><br>%{customdata[0]:,.0f}",
            textposition="inside",
            opacity=0.9,
            baseratio=0.7,
            marker=dict(
                colors=gradient_colors,
                line=dict(color="rgba(15, 23, 42, 0.28)", width=1.6),
            ),
            insidetextfont=dict(color="rgba(15, 23, 42, 0.78)", size=13),
            hovertemplate=(
                "<b>%{label}</b><br>"
                "%{customdata[0]:,.0f} records<br>"
                "%{customdata[1]:.1%} of total"
                "<extra></extra>"
            ),
        )
    )
    funnel_chart.update_layout(
        title="Funnel Momentum",
        uniformtext=dict(mode="show", minsize=12),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.15,
            x=0.5,
            xanchor="center",
        ),
    )
    apply_compact_margins(funnel_chart, top=58, left=26, right=26, bottom=16)
    right.plotly_chart(funnel_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

    trend_chart = px.area(
        trends,
        x="date",
        y=["leads", "mqls", "sqls"],
        title="Weekly Performance Trends",
    )
    trend_chart.update_layout(yaxis_title="Volume", xaxis_title="Week")
    apply_compact_margins(trend_chart, top=64, bottom=32)
    st.plotly_chart(trend_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

    st.markdown("### Channel Performance Table")

    column_options = {label: key for key, label in MARKETING_COLUMN_DEFINITIONS}
    default_labels = [label for key, label in MARKETING_COLUMN_DEFINITIONS if key in DEFAULT_MARKETING_COLUMNS]
    selected_labels = st.multiselect(
        "Columns",
        options=list(column_options.keys()),
        default=default_labels,
        key="marketing_table_columns",
        help="Choose which columns appear in the marketing table."
    )
    selected_keys = [column_options[label] for label in selected_labels if label in column_options]

    render_marketing_table(channel_data, visible_columns=selected_keys)


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
    apply_compact_margins(stage_chart, top=68)
    st.plotly_chart(stage_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

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
    apply_compact_margins(owner_chart, top=68)
    st.plotly_chart(owner_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

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
    apply_compact_margins(segment_chart, top=70, left=8, right=8, bottom=16)
    st.plotly_chart(segment_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

    waterfall = mrr_waterfall(revenue_df, filters)
    waterfall_chart = px.bar(
        waterfall,
        x="period",
        y=["starting_mrr", "new_mrr", "expansion_mrr", "contraction_mrr", "churn_mrr", "ending_mrr"],
        title="MRR Waterfall",
    )
    waterfall_chart.update_layout(barmode="relative", xaxis_title="", yaxis_title="MRR (USD)")
    apply_compact_margins(waterfall_chart, top=70)
    st.plotly_chart(waterfall_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

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
