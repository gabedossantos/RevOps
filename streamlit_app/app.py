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
import streamlit.components.v1 as components
from plotly.subplots import make_subplots
import numpy as np

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
                    "<th class='marketing-th'>"
                    "<span class='marketing-th__content'>"
                    "<span class='marketing-th__label'>{label}</span>"
                    "<span class='tooltip-icon' role='img' aria-label='{tooltip}' tabindex='0' data-tooltip='{tooltip}'>{icon}</span>"
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
                overflow: visible;
                position: relative;
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
                position: relative;
                overflow: visible;
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
                position: relative;
                overflow: visible;
                z-index: 1;
            }
            .marketing-table tr {
                position: relative;
                overflow: visible;
            }
            .marketing-table thead {
                position: relative;
                z-index: 2;
                overflow: visible;
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
                position: relative;
                z-index: 2;
                transition: color 0.18s ease;
            }
            .tooltip-icon:hover,
            .tooltip-icon:focus-visible {
                color: #6366f1;
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

    components.html(
        dedent(
            """
            <script>
            (function() {
                const parentWindow = window.parent;
                if (!parentWindow || !parentWindow.document) {
                    return;
                }
                const parentDoc = parentWindow.document;
                const state = parentWindow.__marketingTooltipState || (parentWindow.__marketingTooltipState = {});

                const ensureStyle = () => {
                    const styleId = "marketing-tooltip-style";
                    if (!parentDoc.getElementById(styleId)) {
                        const styleTag = parentDoc.createElement("style");
                        styleTag.id = styleId;
                        styleTag.textContent = `
                        .marketing-tooltip-shell {
                            position: fixed;
                            z-index: 99999;
                            pointer-events: none;
                            opacity: 0;
                            transform: translate(-50%, -8px) scale(0.98);
                            transition: opacity 0.18s ease, transform 0.18s ease;
                            max-width: min(320px, 72vw);
                            padding: 10px 14px;
                            border-radius: 10px;
                            background: rgba(15, 23, 42, 0.96);
                            color: #f8fafc;
                            font-size: 0.75rem;
                            line-height: 1.4;
                            box-shadow: 0 18px 32px rgba(15, 23, 42, 0.45);
                            backdrop-filter: blur(8px);
                            border: 1px solid rgba(148, 163, 184, 0.35);
                        }
                        .marketing-tooltip-shell[data-visible="true"] {
                            opacity: 1;
                            transform: translate(-50%, -12px) scale(1);
                        }
                        .marketing-tooltip-shell[data-position="bottom"] {
                            transform: translate(-50%, 12px) scale(0.98);
                        }
                        .marketing-tooltip-shell[data-position="bottom"][data-visible="true"] {
                            transform: translate(-50%, 8px) scale(1);
                        }
                        .marketing-tooltip-shell::after {
                            content: "";
                            position: absolute;
                            left: 50%;
                            transform: translateX(-50%);
                            border-style: solid;
                        }
                        .marketing-tooltip-shell[data-position="top"]::after {
                            bottom: -10px;
                            border-width: 10px 8px 0 8px;
                            border-color: rgba(15, 23, 42, 0.96) transparent transparent transparent;
                        }
                        .marketing-tooltip-shell[data-position="bottom"]::after {
                            top: -10px;
                            border-width: 0 8px 10px 8px;
                            border-color: transparent transparent rgba(15, 23, 42, 0.96) transparent;
                        }
                        `;
                        parentDoc.head.appendChild(styleTag);
                    }
                };

                const ensureTooltipElement = () => {
                    if (!state.tooltipEl) {
                        const tooltipEl = parentDoc.createElement("div");
                        tooltipEl.className = "marketing-tooltip-shell";
                        tooltipEl.setAttribute("role", "tooltip");
                        tooltipEl.setAttribute("data-visible", "false");
                        tooltipEl.style.left = "50%";
                        tooltipEl.style.top = "0";
                        parentDoc.body.appendChild(tooltipEl);
                        state.tooltipEl = tooltipEl;
                    }
                    return state.tooltipEl;
                };

                const setPosition = (icon) => {
                    const tooltipEl = ensureTooltipElement();
                    if (!icon || !tooltipEl) {
                        return;
                    }
                    const rect = icon.getBoundingClientRect();
                    const tooltipRect = tooltipEl.getBoundingClientRect();
                    let left = rect.left + rect.width / 2;
                    left = Math.max(16, Math.min(left, parentWindow.innerWidth - 16));
                    let top = rect.top - tooltipRect.height - 12;
                    let position = "top";
                    if (top < 12) {
                        top = rect.bottom + 12;
                        position = "bottom";
                    }
                    tooltipEl.setAttribute("data-position", position);
                    tooltipEl.style.left = `${left}px`;
                    tooltipEl.style.top = `${top}px`;
                };

                const hideTooltip = () => {
                    const tooltipEl = ensureTooltipElement();
                    tooltipEl.setAttribute("data-visible", "false");
                    if (state.activeIcon) {
                        delete state.activeIcon.dataset.tooltipActive;
                    }
                    state.activeIcon = null;
                };

                const showTooltip = (icon) => {
                    if (!icon) {
                        return;
                    }
                    const tooltipEl = ensureTooltipElement();
                    const text = icon.getAttribute("data-tooltip");
                    if (!text) {
                        return;
                    }
                    tooltipEl.textContent = text;
                    tooltipEl.setAttribute("data-visible", "true");
                    icon.dataset.tooltipActive = "true";
                    state.activeIcon = icon;
                    setPosition(icon);
                };

                if (!parentWindow.__marketingTooltipSetup) {
                    parentWindow.__marketingTooltipSetup = true;
                    ensureStyle();
                    ensureTooltipElement();

                    const getIconFromEvent = (event) => {
                        const target = event.target;
                        if (!target) {
                            return null;
                        }
                        return target.closest('.tooltip-icon[data-tooltip]');
                    };

                    parentDoc.addEventListener("pointerenter", (event) => {
                        const icon = getIconFromEvent(event);
                        if (!icon) {
                            return;
                        }
                        showTooltip(icon);
                    }, true);

                    parentDoc.addEventListener("focusin", (event) => {
                        const icon = getIconFromEvent(event);
                        if (!icon) {
                            return;
                        }
                        showTooltip(icon);
                    }, true);

                    parentDoc.addEventListener("pointermove", () => {
                        if (state.activeIcon) {
                            setPosition(state.activeIcon);
                        }
                    }, true);

                    parentDoc.addEventListener("pointerleave", (event) => {
                        if (!state.activeIcon) {
                            return;
                        }
                        const nextTarget = event.relatedTarget && event.relatedTarget.closest?.('.tooltip-icon[data-tooltip]');
                        if (nextTarget === state.activeIcon) {
                            return;
                        }
                        hideTooltip();
                    }, true);

                    parentDoc.addEventListener("focusout", (event) => {
                        if (!state.activeIcon) {
                            return;
                        }
                        const nextTarget = event.relatedTarget && event.relatedTarget.closest?.('.tooltip-icon[data-tooltip]');
                        if (nextTarget === state.activeIcon) {
                            return;
                        }
                        hideTooltip();
                    }, true);

                    parentDoc.addEventListener("keydown", (event) => {
                        if (event.key === "Escape") {
                            hideTooltip();
                        }
                    }, true);

                    parentWindow.addEventListener("scroll", () => {
                        if (state.activeIcon) {
                            setPosition(state.activeIcon);
                        }
                    }, true);

                    parentWindow.addEventListener("resize", () => {
                        if (state.activeIcon) {
                            setPosition(state.activeIcon);
                        }
                    });

                    const ObserverCtor = parentWindow.MutationObserver || window.MutationObserver;
                    if (ObserverCtor) {
                        const observer = new ObserverCtor(() => {
                            if (state.activeIcon && !parentDoc.contains(state.activeIcon)) {
                                hideTooltip();
                            }
                        });
                        observer.observe(parentDoc.body, { childList: true, subtree: true });
                        state.observer = observer;
                    }
                } else {
                    ensureStyle();
                    ensureTooltipElement();
                }

                const pendingIcons = parentDoc.querySelectorAll('.tooltip-icon[data-tooltip]:not([data-tooltip-enhanced="true"])');
                pendingIcons.forEach((icon) => {
                    icon.dataset.tooltipEnhanced = "true";
                    icon.setAttribute("tabindex", icon.getAttribute("tabindex") || "0");
                });
            })();
            </script>
            """
        ),
        height=0,
        width=0,
    )

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
    st.markdown("### MRR Momentum Bridge")
    if waterfall.empty:
        st.info("No MRR data available for the selected filters.")
    else:
        periods = waterfall["period"].tolist()
        default_index = max(len(periods) - 1, 0)
        selected_period = st.selectbox(
            "Select period",
            options=periods,
            index=default_index,
            key="mrr_bridge_period",
            help="View how each motion contributed to MRR change for a specific month.",
        )

        period_row = waterfall[waterfall["period"] == selected_period].iloc[0]
        starting = float(period_row["starting_mrr"])
        ending = float(period_row["ending_mrr"])
        new_mrr_value = float(period_row["new_mrr"])
        expansion = float(period_row["expansion_mrr"])
        contraction = float(period_row["contraction_mrr"])
        churn = float(period_row["churn_mrr"])
        net_change = ending - starting

        contribution_labels = ["New MRR", "Expansion", "Contraction", "Churn"]
        contribution_values = [
            new_mrr_value,
            expansion,
            -contraction,
            -churn,
        ]

        contribution_colors = ["#22c55e" if value >= 0 else "#f87171" for value in contribution_values]

        def format_currency(value: float, *, show_sign: bool = False) -> str:
            sign = "+" if value >= 0 else "-"
            formatted = f"${abs(value):,.0f}"
            return f"{sign}{formatted}" if show_sign else formatted

        bridge = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=False,
            row_heights=[0.42, 0.58],
            vertical_spacing=0.12,
            specs=[[{"type": "bar"}], [{"type": "bar"}]],
        )

        bridge.add_trace(
            go.Bar(
                name="Starting",
                x=[starting],
                y=["Starting MRR"],
                orientation="h",
                marker=dict(color="#93c5fd"),
                text=[format_currency(starting)],
                textposition="outside",
                hovertemplate="Starting MRR<br>%{x:$,.0f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        bridge.add_trace(
            go.Bar(
                name="Ending",
                x=[ending],
                y=["Ending MRR"],
                orientation="h",
                marker=dict(color="#4f46e5"),
                text=[format_currency(ending)],
                textposition="outside",
                hovertemplate="Ending MRR<br>%{x:$,.0f}<extra></extra>",
            ),
            row=1,
            col=1,
        )

        bridge.add_annotation(
            dict(
                xref="paper",
                yref="y1",
                x=1.02,
                y="Ending MRR",
                align="left",
                text=f"Net Δ {format_currency(net_change, show_sign=True)}",
                font=dict(color="#0f172a", size=13),
                showarrow=False,
            )
        )

        bridge.add_trace(
            go.Bar(
                x=contribution_labels,
                y=contribution_values,
                marker=dict(color=contribution_colors),
                text=[format_currency(val, show_sign=True) for val in contribution_values],
                textposition="outside",
                hovertemplate="%{x}<br>%{y:$,.0f}<extra></extra>",
            ),
            row=2,
            col=1,
        )

        contribution_axis_limit = max(abs(value) for value in contribution_values) or 1
        bridge.update_yaxes(
            title_text="MRR (USD)",
            row=2,
            col=1,
            range=[-1.15 * contribution_axis_limit, 1.15 * contribution_axis_limit],
        )
        bridge.update_yaxes(showgrid=False, row=1, col=1)
        bridge.update_xaxes(showgrid=False, row=1, col=1)
        bridge.update_xaxes(title_text="Growth Motions", row=2, col=1)

        bridge.update_layout(
            barmode="overlay",
            bargap=0.3,
            hovermode="closest",
            showlegend=False,
            margin=dict(t=70, b=32, l=60, r=20),
            height=540,
            title=dict(text=f"MRR Bridge · {selected_period}", x=0.02),
        )

        st.plotly_chart(bridge, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

        st.caption(
            f"Starting MRR of {format_currency(starting)} shifted by {format_currency(net_change, show_sign=True)} to {format_currency(ending)} after new, expansion, contraction, and churn movements."
        )

        contribution_history = waterfall.copy()
        contribution_history = contribution_history.assign(
            New=contribution_history["new_mrr"],
            Expansion=contribution_history["expansion_mrr"],
            Contraction=-contribution_history["contraction_mrr"],
            Churn=-contribution_history["churn_mrr"],
            Net=(contribution_history["ending_mrr"] - contribution_history["starting_mrr"]),
        )
        contribution_history = contribution_history[["period", "New", "Expansion", "Contraction", "Churn", "Net"]]

        trend_melt = contribution_history.melt(id_vars="period", var_name="Motion", value_name="Amount")
        period_order = contribution_history["period"].tolist()

        trend_chart = px.line(
            trend_melt,
            x="period",
            y="Amount",
            color="Motion",
            markers=True,
            category_orders={"period": period_order},
            title="Contribution Trends",
            labels={"Amount": "MRR Change (USD)", "period": "Period"},
        )
        trend_chart.update_layout(legend=dict(title="Motion", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        trend_chart.update_yaxes(tickprefix="$", separatethousands=True)
        apply_compact_margins(trend_chart, top=70, bottom=32)
        st.plotly_chart(trend_chart, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

        recent_history = contribution_history.copy()
        recent_history["Period"] = recent_history["period"]
        display_history = recent_history[["Period", "New", "Expansion", "Contraction", "Churn", "Net"]].tail(6)
        styled_history = display_history.set_index("Period").apply(
            lambda column: column.map(lambda amount: f"${amount:,.0f}")
        )
        st.dataframe(styled_history, use_container_width=True)

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



def render_revenue_new_tab(revenue_df: pd.DataFrame) -> None:
    import plotly.graph_objects as go
    # import numpy as np
    st.subheader("Revenue Cohort Analysis")

    # --- Cohort Heatmap ---
    # Try to build cohort matrix from data, else fallback to sample
    df = revenue_df.copy()
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['churn_date'] = pd.to_datetime(df['churn_date'], errors='coerce')
    df['cohort'] = df['start_date'].dt.to_period('M').astype(str)
    # Only use customers with a start_date
    df = df[~df['start_date'].isna()]
    # Build retention matrix: for each cohort, what % remain each month
    cohorts = sorted(df['cohort'].unique())
    max_months = 12
    month_labels = [f"M{i}" for i in range(max_months)]
    def months_between(start, end):
        return (end.year - start.year) * 12 + (end.month - start.month)
    retention_matrix = []
    for cohort in cohorts:
        cohort_df = df[df['cohort'] == cohort].copy()
        if cohort_df.empty:
            retention_matrix.append([np.nan]*max_months)
            continue
        cohort_start = pd.to_datetime(cohort + '-01')
        cohort_df['months_since'] = cohort_df['churn_date'].fillna(pd.Timestamp.today()).apply(
            lambda d: months_between(cohort_start, d)
        )
        base_count = len(cohort_df)
        row = []
        for m in range(max_months):
            still_active = ((cohort_df['churned_flag'] == False) | (cohort_df['months_since'] >= m)).sum()
            pct = 100 * still_active / base_count if base_count else np.nan
            row.append(round(pct, 1))
        retention_matrix.append(row)

    # If not enough data, fallback to sample
    if np.isnan(np.array(retention_matrix)).all():
        cohorts = [
            "2022-10", "2022-11", "2022-12", "2023-01", "2023-02", "2023-03",
            "2023-04", "2023-05", "2023-06", "2023-07", "2023-08", "2023-09",
            "2023-10", "2023-11", "2023-12", "2024-01", "2024-02", "2024-03"
        ]
        retention_matrix = [
            [100, 85, 78, 72, 68, 65, 62, 59, 56, 54, 52, 50],
            [100, 88, 81, 75, 71, 68, 65, 62, 59, 57, 55, 53],
            [100, 82, 75, 69, 65, 62, 59, 56, 53, 51, 49, 47],
            [100, 90, 83, 77, 73, 70, 67, 64, 61, 59, 57, 55],
            [100, 86, 79, 73, 69, 66, 63, 60, 57, 55, 53, 51],
            [100, 89, 82, 76, 72, 69, 66, 63, 60, 58, 56, 54],
            [100, 84, 77, 71, 67, 64, 61, 58, 55, 53, 51, 49],
            [100, 87, 80, 74, 70, 67, 64, 61, 58, 56, 54, 52],
            [100, 85, 78, 72, 68, 65, 62, 59, 56, 54, 52, 50],
            [100, 88, 81, 75, 71, 68, 65, 62, 59, 57, 55, 53],
            [100, 83, 76, 70, 66, 63, 60, 57, 54, 52, 50, 48],
            [100, 86, 79, 73, 69, 66, 63, 60, 57, 55, 53, 51],
            [100, 91, 84, 78, 74, 71, 68, 65, 62, 60, 58, 56],
            [100, 87, 80, 74, 70, 67, 64, 61, 58, 56, 54, 52],
            [100, 84, 77, 71, 67, 64, 61, 58, 55, 53, 51, 49],
            [100, 89, 82, 76, 72, 69, 66, 63, 60, 58, 56, 54],
            [100, 85, 78, 72, 68, 65, 62, 59, 56, 54, 52, 50],
            [100, 88, 81, 75, 71, 68, 65, 62, 59, 57, 55, 53]
        ]

    fig = go.Figure(data=go.Heatmap(
        z=retention_matrix,
        x=month_labels,
        y=cohorts,
        colorscale='Blues',
        reversescale=False,
        showscale=True,
        colorbar=dict(title="Retention %"),
        hovertemplate='Cohort: %{y}<br>Month: %{x}<br>Retention: %{z}%<extra></extra>'
    ))
    fig.update_layout(
        title='Revenue Cohort Analysis',
        xaxis_title='Months Since',
        yaxis_title='Cohort',
    )
    fig.update_xaxes(side='bottom')
    fig.update_yaxes(autorange='reversed')
    st.plotly_chart(fig, use_container_width=True)

    # --- Summary Table ---
    st.markdown("### Revenue Data Summary")
    # Unique segments/plans
    st.write("**Unique segments:**", sorted(df['segment'].dropna().unique()))
    st.write("**Unique plans:**", sorted(df['plan'].dropna().unique()))
    # Churn rate
    churn_rate = df['churned_flag'].mean()
    st.write(f"**Churn rate:** {churn_rate:.2%}")
    # Date ranges
    st.write(f"**Start dates range:** {df['start_date'].min().date()} to {df['start_date'].max().date()}")
    if df['churn_date'].notna().any():
        st.write(f"**Churn dates range:** {df['churn_date'].min().date()} to {df['churn_date'].max().date()}")
    # Churn reasons
    st.write("**Churn reasons:**")
    st.dataframe(df['churn_reason'].value_counts().reset_index().rename(columns={'index':'Reason','churn_reason':'Count'}))
    # MRR by segment/plan
    st.write("**MRR by segment:**")
    st.dataframe(df.groupby('segment')['mrr'].agg(['count','mean','sum']))
    st.write("**MRR by plan:**")
    st.dataframe(df.groupby('plan')['mrr'].agg(['count','mean','sum']))
    # Active/churned
    active_customers = df[df['churned_flag'] == False]
    st.write(f"**Active customers:** {len(active_customers)}")
    st.write(f"**Churned customers:** {len(df[df['churned_flag'] == True])}")
    # NRR stats
    st.write("**NRR statistics:**")
    st.write(f"Mean NRR: {df['nrr'].mean():.3f}")
    st.write(f"Median NRR: {df['nrr'].median():.3f}")
    st.write(f"NRR > 1.0 (growing customers): {(df['nrr'] > 1.0).sum()}")
    st.write(f"NRR = 1.0 (flat customers): {(df['nrr'] == 1.0).sum()}")
    st.write(f"NRR < 1.0 (contracting/churned customers): {(df['nrr'] < 1.0).sum()}")


def render_waterfall_chart_tab(revenue_df: pd.DataFrame) -> None:
    import plotly.graph_objects as go

    st.subheader("Segment Waterfall Dashboard")

    if revenue_df.empty:
        st.info("No revenue data available to render segment performance.")
        return

    segment_map = {
        "ENT": "Enterprise",
        "MM": "Mid-Market",
        "SMB": "SMB",
    }

    df = revenue_df.copy()
    df["segment_label"] = df["segment"].map(segment_map).fillna(df["segment"].astype(str))

    grouped = (
        df.groupby("segment_label")
        .agg(
            mrr_sum=("mrr", "sum"),
            customer_count=("customer_id", "nunique"),
            nrr_mean=("nrr", "mean"),
            churn_rate=("churned_flag", "mean"),
            expansion_total=("expansion_mrr", "sum"),
            contraction_total=("contraction_mrr", "sum"),
            new_total=("new_mrr", "sum"),
        )
        .reset_index()
    )

    if grouped.empty:
        st.info("Segment aggregation returned no records.")
        return

    grouped.sort_values("mrr_sum", ascending=False, inplace=True)

    segments = grouped["segment_label"].tolist()
    mrr_millions = grouped["mrr_sum"].div(1_000_000).round(3).tolist()
    nrr_percent = grouped["nrr_mean"].fillna(0).mul(100).round(1).tolist()
    churn_percent = grouped["churn_rate"].fillna(0).mul(100).round(1).tolist()
    customer_count = grouped["customer_count"].astype(int).tolist()

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            x=segments,
            y=mrr_millions,
            name="MRR ($M)",
            customdata=customer_count,
            hovertemplate=(
                "<b>%{x}</b><br>MRR: $%{y:.2f}M<br>Customers: %{customdata}<extra></extra>"
            ),
            marker_color="#1FB8CD",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=segments,
            y=nrr_percent,
            mode="lines+markers",
            name="NRR (%)",
            line=dict(color="#DB4545", width=3),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>NRR: %{y:.1f}%<extra></extra>",
            yaxis="y2",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=segments,
            y=churn_percent,
            mode="lines+markers",
            name="Churn (%)",
            line=dict(color="#2E8B57", width=3),
            marker=dict(size=8),
            hovertemplate="<b>%{x}</b><br>Churn: %{y:.1f}%<extra></extra>",
            yaxis="y2",
        )
    )

    fig.update_layout(
        title="Segment Performance Dashboard",
        xaxis_title="Segment",
        yaxis=dict(title="MRR ($ millions)", rangemode="tozero"),
        yaxis2=dict(title="Rate (%)", overlaying="y", side="right", rangemode="tozero"),
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="center", x=0.5),
        margin=dict(t=70, b=40, l=60, r=60),
        hovermode="x unified",
    )

    fig.update_traces(cliponaxis=False)

    st.plotly_chart(fig, config=DEFAULT_PLOTLY_CONFIG, use_container_width=True)

    st.markdown("### Segment Summary Table")
    summary = grouped.assign(
        mrr_sum=lambda d: d["mrr_sum"].map(lambda value: f"${value:,.0f}"),
        expansion_total=lambda d: d["expansion_total"].map(lambda value: f"${value:,.0f}"),
        contraction_total=lambda d: d["contraction_total"].map(lambda value: f"${value:,.0f}"),
        new_total=lambda d: d["new_total"].map(lambda value: f"${value:,.0f}"),
        nrr_mean=lambda d: d["nrr_mean"].map(lambda value: f"{value:.3f}"),
        churn_rate=lambda d: d["churn_rate"].map(lambda value: f"{value:.2%}"),
    )
    summary = summary.rename(
        columns={
            "segment_label": "Segment",
            "mrr_sum": "Total MRR",
            "customer_count": "Customers",
            "nrr_mean": "Avg NRR",
            "churn_rate": "Churn Rate",
            "expansion_total": "Expansion MRR",
            "contraction_total": "Contraction MRR",
            "new_total": "New MRR",
        }
    )
    summary_display = summary[
        [
            "Segment",
            "Customers",
            "Total MRR",
            "New MRR",
            "Expansion MRR",
            "Contraction MRR",
            "Avg NRR",
            "Churn Rate",
        ]
    ]
    st.dataframe(summary_display, use_container_width=True)


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

    marketing_tab, pipeline_tab, revenue_tab, revenue_new_tab, waterfall_tab, ai_tab = st.tabs(
        ["Marketing", "Pipeline", "Revenue", "Revenue New", "Waterfall Chart", "AI Co-Pilot"]
    )

    with marketing_tab:
        render_marketing_tab(marketing_df, filters)

    with pipeline_tab:
        render_pipeline_tab(pipeline_df, filters)

    with revenue_tab:
        render_revenue_tab(revenue_df, filters)

    with revenue_new_tab:
        render_revenue_new_tab(revenue_df)

    with waterfall_tab:
        render_waterfall_chart_tab(revenue_df)

    with ai_tab:
        render_ai_tab(marketing_df, pipeline_df, revenue_df, filters)


if __name__ == "__main__":
    main()
