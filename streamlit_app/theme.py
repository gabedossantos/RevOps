"""Brand theming utilities for the RevOps Streamlit experience."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


@dataclass(frozen=True)
class BrandTheme:
    """Brand system for the RevOps Control Center UI."""

    key: str = "default"
    font_family: str = "'Inter', 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"
    gradient_background: str = "linear-gradient(140deg, #05070f 0%, #0b1728 45%, #25113c 100%)"
    sidebar_background: str = "rgba(10, 17, 34, 0.75)"
    surface_color: str = "rgba(15, 23, 42, 0.55)"
    surface_border: str = "rgba(99, 102, 241, 0.25)"
    overlay_shadow: str = "0px 32px 80px rgba(15, 23, 42, 0.45)"
    text_color: str = "#E2E8F0"
    muted_text: str = "#94A3B8"
    accent_primary: str = "#6366F1"
    accent_secondary: str = "#22D3EE"
    accent_tertiary: str = "#C084FC"
    success: str = "#34D399"
    warning: str = "#FBBF24"
    danger: str = "#F87171"
    border_radius: str = "20px"
    colorway: Sequence[str] = (
        "#6366F1",
        "#22D3EE",
        "#C084FC",
        "#FDE68A",
        "#34D399",
        "#F97316",
    )


NEON_THEME = BrandTheme(
    key="neon",
    gradient_background="linear-gradient(140deg, #05070f 0%, #0b1728 45%, #25113c 100%)",
    sidebar_background="rgba(10, 17, 34, 0.75)",
    surface_color="rgba(15, 23, 42, 0.55)",
    surface_border="rgba(99, 102, 241, 0.25)",
    overlay_shadow="0px 32px 80px rgba(15, 23, 42, 0.45)",
    text_color="#E2E8F0",
    muted_text="#94A3B8",
    accent_primary="#6366F1",
    accent_secondary="#22D3EE",
    accent_tertiary="#C084FC",
    success="#34D399",
    warning="#FBBF24",
    danger="#F87171",
    border_radius="20px",
    colorway=(
        "#6366F1",
        "#22D3EE",
        "#C084FC",
        "#FDE68A",
        "#34D399",
        "#F97316",
    ),
)

MIDNIGHT_THEME = BrandTheme(
    key="midnight",
    gradient_background="linear-gradient(150deg, #0B1220 0%, #111C2E 52%, #1C273A 100%)",
    sidebar_background="rgba(11, 17, 30, 0.82)",
    surface_color="rgba(18, 25, 39, 0.72)",
    surface_border="rgba(100, 116, 139, 0.28)",
    overlay_shadow="0px 28px 60px rgba(8, 12, 22, 0.55)",
    text_color="#E5E7EB",
    muted_text="#94A3B8",
    accent_primary="#4F46E5",
    accent_secondary="#38BDF8",
    accent_tertiary="#8B5CF6",
    success="#22C55E",
    warning="#F59E0B",
    danger="#EF4444",
    border_radius="18px",
    colorway=(
        "#4F46E5",
        "#38BDF8",
        "#8B5CF6",
        "#FBBF24",
        "#22C55E",
        "#F97316",
    ),
)

LUMA_THEME = BrandTheme(
    key="luma",
    gradient_background="linear-gradient(160deg, #F4F7FB 0%, #FFFFFF 55%, #E9ECF5 100%)",
    sidebar_background="rgba(255, 255, 255, 0.94)",
    surface_color="rgba(255, 255, 255, 0.85)",
    surface_border="rgba(203, 213, 225, 0.7)",
    overlay_shadow="0px 18px 42px rgba(148, 163, 184, 0.35)",
    text_color="#0F172A",
    muted_text="#475569",
    accent_primary="#2563EB",
    accent_secondary="#0EA5E9",
    accent_tertiary="#A855F7",
    success="#16A34A",
    warning="#D97706",
    danger="#DC2626",
    border_radius="16px",
    colorway=(
        "#2563EB",
        "#0EA5E9",
        "#F97316",
        "#10B981",
        "#FACC15",
        "#A855F7",
    ),
)

AVAILABLE_THEMES: Mapping[str, BrandTheme] = {
    "Midnight Aurora": MIDNIGHT_THEME,
    "Luma Skyline": LUMA_THEME,
    "Neon Pulse (Legacy)": NEON_THEME,
}

DEFAULT_THEME_NAME = "Midnight Aurora"

DEFAULT_PLOTLY_CONFIG: Mapping[str, object] = {
    "displayModeBar": False,
    "scrollZoom": False,
    "responsive": True,
}
"""Default Plotly configuration applied to every chart render."""


def register_plotly_template(theme: BrandTheme) -> str:
    """Register and return the custom Plotly template name."""

    template_name = f"revops-{theme.key}"
    if template_name in pio.templates:
        return template_name

    grid_color = "rgba(148, 163, 184, 0.25)" if theme.key != "luma" else "rgba(148, 163, 184, 0.35)"
    hover_bg = "rgba(15, 23, 42, 0.85)" if theme.key != "luma" else "rgba(255, 255, 255, 0.9)"

    template = go.layout.Template(
        layout=dict(
            font=dict(family=theme.font_family, color=theme.text_color, size=14),
            title=dict(font=dict(size=26, color=theme.text_color, family=theme.font_family), x=0.02),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor=theme.surface_color,
            colorway=list(theme.colorway),
            legend=dict(
                bgcolor=theme.surface_color,
                bordercolor=theme.surface_border,
                borderwidth=1,
                font=dict(color=theme.text_color, size=12),
                orientation="h",
                yanchor="bottom",
                y=1.02,
            ),
            xaxis=dict(
                gridcolor=grid_color,
                title=dict(font=dict(color=theme.muted_text)),
                tickfont=dict(color=theme.muted_text),
                zerolinecolor="rgba(148, 163, 184, 0.15)",
                showspikes=True,
                spikemode="across",
                spikethickness=1,
                spikecolor=theme.accent_secondary,
            ),
            yaxis=dict(
                gridcolor=grid_color,
                title=dict(font=dict(color=theme.muted_text)),
                tickfont=dict(color=theme.muted_text),
                zerolinecolor="rgba(148, 163, 184, 0.15)",
            ),
            margin=dict(l=40, r=32, t=70, b=45),
            hovermode="x unified",
            hoverlabel=dict(
                bgcolor=hover_bg,
                bordercolor=theme.accent_primary,
                font=dict(color=theme.text_color, family=theme.font_family, size=13),
            ),
        )
    )
    pio.templates[template_name] = template
    return template_name


def apply_plotly_theme(theme: BrandTheme) -> None:
    """Apply the project-wide Plotly defaults."""

    from plotly import express as px

    template_name = register_plotly_template(theme)
    setattr(px.defaults, "template", template_name)
    setattr(px.defaults, "color_discrete_sequence", list(theme.colorway))


def inject_global_styles(theme: BrandTheme) -> None:
    """Inject global CSS overrides for a modern, AI SaaS aesthetic."""

    st.markdown(
        f"""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600&display=swap');

            :root {{
                --brand-surface: {theme.surface_color};
                --brand-border: {theme.surface_border};
                --brand-radius: {theme.border_radius};
                --brand-shadow: {theme.overlay_shadow};
                --brand-text: {theme.text_color};
                --brand-muted: {theme.muted_text};
                --brand-accent: {theme.accent_primary};
                --brand-accent-secondary: {theme.accent_secondary};
                --brand-accent-tertiary: {theme.accent_tertiary};
            }}

            html, body, [class*="css"] {{
                font-family: {theme.font_family};
            }}

            body {{
                color: {theme.text_color};
                background: {theme.gradient_background} !important;
            }}

            div[data-testid="stAppViewContainer"] {{
                background: {theme.gradient_background};
                color: {theme.text_color};
            }}

            header[data-testid="stHeader"] {{
                background: transparent;
            }}

            section[data-testid="stSidebar"] {{
                background: {theme.sidebar_background};
                backdrop-filter: blur(22px);
                border-right: 1px solid {theme.surface_border};
            }}

            section[data-testid="stSidebar"] * {{
                color: {theme.text_color} !important;
            }}

            div[data-testid="stSidebar"] .stMarkdown, div[data-testid="stSidebar"] .stMarkdown p {{
                color: {theme.muted_text} !important;
            }}

            .sidebar-title {{
                font-size: 1.05rem;
                font-weight: 600;
                color: {theme.text_color};
                margin-bottom: 0.35rem;
            }}

            .sidebar-subtitle {{
                font-size: 0.85rem;
                line-height: 1.5;
                color: {theme.muted_text};
                margin-bottom: 1.2rem;
            }}

            div.block-container {{
                padding-top: 2.8rem;
                max-width: 1180px;
            }}

            .stTabs [data-baseweb="tab-list"] {{
                gap: 0.75rem;
                border-bottom: 1px solid {theme.surface_border};
            }}

            .stTabs [data-baseweb="tab"] {{
                padding: 0.75rem 1.5rem;
                background: {theme.surface_color};
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 999px;
                color: {theme.muted_text};
                font-weight: 600;
                transition: all 0.25s ease;
            }}

            .stTabs [aria-selected="true"] {{
                background: linear-gradient(135deg, {theme.accent_primary}b3, {theme.accent_secondary}b3);
                color: {theme.text_color};
                box-shadow: 0px 12px 40px {theme.accent_primary}40;
                border-color: {theme.accent_primary}80;
            }}

            div[data-testid="stMetric"] {{
                background: var(--brand-surface);
                border: 1px solid var(--brand-border);
                border-radius: {theme.border_radius};
                padding: 1.1rem 1.3rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(20px);
            }}

            div[data-testid="stMetricValue"] {{
                color: {theme.accent_secondary};
                font-size: 1.7rem;
                font-weight: 600;
            }}

            div[data-testid="stMetricLabel"] {{
                color: {theme.muted_text} !important;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}

            div[data-testid="stPlotlyChart"] {{
                background: var(--brand-surface);
                border: 1px solid var(--brand-border);
                border-radius: {theme.border_radius};
                padding: 0.9rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(18px);
                box-sizing: border-box;
                max-width: 100%;
                overflow: hidden;
            }}

            div[data-testid="stPlotlyChart"] > div:first-child {{
                width: 100% !important;
                margin: 0 auto;
            }}

            div[data-testid="column"] {{
                min-width: 0 !important;
            }}

            div[data-testid="stDataFrame"] {{
                background: var(--brand-surface);
                border: 1px solid var(--brand-border);
                border-radius: {theme.border_radius};
                padding: 0.65rem 0.5rem 0.5rem 0.5rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(18px);
            }}

            div[data-testid="stDataFrame"] table {{
                font-family: {theme.font_family};
                color: {theme.text_color};
            }}

            div[data-testid="stDataFrame"] thead tr {{
                background: {theme.accent_primary}1a;
            }}

            div[data-testid="stDataFrame"] tbody td {{
                border-color: rgba(148, 163, 184, 0.12) !important;
            }}

            .stSelectbox, .stMultiSelect, .stDateInput {{
                border-radius: 12px !important;
            }}

            div[data-testid="stFormSubmitButton"] button, button[kind="primary"] {{
                border-radius: 999px;
                background: linear-gradient(135deg, {theme.accent_primary}, {theme.accent_secondary});
                border: none;
                color: white;
                font-weight: 600;
                box-shadow: 0px 14px 30px {theme.accent_primary}4d;
            }}

            div[data-testid="stMarkdown"] h1,
            div[data-testid="stMarkdown"] h2,
            div[data-testid="stMarkdown"] h3,
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {{
                color: {theme.text_color};
                font-weight: 650;
            }}

            .hero-header {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 2.2rem;
                background: var(--brand-surface);
                border: 1px solid var(--brand-border);
                border-radius: var(--brand-radius);
                padding: 2.1rem 2.4rem;
                margin-bottom: 1.8rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(24px);
            }}

            .hero-header h1 {{
                font-size: 2.35rem;
                line-height: 1.2;
                margin-bottom: 0.5rem;
                color: {theme.text_color};
            }}

            .hero-subtitle {{
                font-size: 1.02rem;
                color: {theme.muted_text};
                max-width: 560px;
                margin-bottom: 0;
            }}

            .hero-theme {{
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                margin-top: 0.55rem;
                padding: 0.3rem 0.75rem;
                border-radius: 999px;
                border: 1px solid {theme.surface_border};
                background: linear-gradient(135deg, {theme.accent_primary}1f, {theme.accent_secondary}1f);
                color: {theme.text_color};
                font-size: 0.8rem;
                font-weight: 500;
                letter-spacing: 0.04em;
                text-transform: uppercase;
            }}

            .hero-eyebrow {{
                font-size: 0.75rem;
                letter-spacing: 0.28em;
                text-transform: uppercase;
                font-weight: 600;
                color: {theme.accent_secondary};
                margin-bottom: 0.75rem;
            }}

            .hero-badge {{
                display: flex;
                align-items: center;
                gap: 0.9rem;
                padding: 1rem 1.1rem;
                border-radius: 18px;
                background: linear-gradient(135deg, {theme.accent_secondary}26, {theme.accent_primary}26);
                border: 1px solid {theme.accent_primary}40;
                box-shadow: 0 18px 42px {theme.accent_secondary}33;
            }}

            .hero-badge__pulse {{
                width: 12px;
                height: 12px;
                border-radius: 999px;
                background: {theme.success};
                box-shadow: 0 0 0 0 {theme.success}66;
                animation: heroPulse 1.6s infinite;
            }}

            .hero-badge__label {{
                display: block;
                font-weight: 600;
                color: {theme.text_color};
            }}

            .hero-badge__meta {{
                display: block;
                font-size: 0.78rem;
                color: {theme.muted_text};
            }}

            @keyframes heroPulse {{
                0% {{ box-shadow: 0 0 0 0 {theme.success}66; }}
                70% {{ box-shadow: 0 0 0 12px {theme.success}00; }}
                100% {{ box-shadow: 0 0 0 0 {theme.success}00; }}
            }}

            .stDivider {{
                border-top: 1px solid rgba(148, 163, 184, 0.25) !important;
            }}

            .insight-card {{
                background: var(--brand-surface);
                border: 1px solid var(--brand-border);
                border-radius: calc(var(--brand-radius) - 6px);
                padding: 1.2rem 1.4rem;
                margin-bottom: 0.6rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(16px);
            }}

            .insight-card--marketing {{
                border-left: 4px solid {theme.accent_primary};
            }}

            .insight-card--pipeline {{
                border-left: 4px solid {theme.accent_secondary};
            }}

            .insight-card--revenue {{
                border-left: 4px solid {theme.accent_tertiary};
            }}

            .insight-chip {{
                display: inline-block;
                font-size: 0.7rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                color: {theme.accent_secondary};
            }}

            .insight-message {{
                font-size: 1.02rem;
                color: {theme.text_color};
                margin: 0.35rem 0 0.2rem 0;
            }}

            div[data-testid="stProgressBar"] {{
                background: linear-gradient(90deg, {theme.accent_primary}26, {theme.accent_secondary}26);
                border-radius: 999px;
                height: 10px;
                margin: 0.4rem 0 0.7rem 0;
            }}

            div[data-testid="stProgressBar"] > div {{
                background: linear-gradient(135deg, {theme.accent_primary}, {theme.accent_secondary});
                border-radius: 999px;
            }}

            @media (max-width: 1200px) {{
                div.block-container {{
                    max-width: 100%;
                    padding: 2rem 1.8rem;
                }}

                .hero-header {{
                    flex-direction: column;
                    align-items: flex-start;
                    gap: 1.6rem;
                }}

                .hero-badge {{
                    width: 100%;
                }}

                .stTabs [data-baseweb="tab-list"] {{
                    overflow-x: auto;
                    padding-bottom: 0.5rem;
                }}

                .stTabs [data-baseweb="tab"] {{
                    flex: 0 0 auto;
                }}
            }}

            @media (max-width: 960px) {{
                .hero-header {{
                    padding: 1.8rem 1.5rem;
                }}

                section[data-testid="stSidebar"] {{
                    width: 260px;
                }}

                div[data-testid="column"] {{
                    flex: 1 1 100% !important;
                    min-width: 100% !important;
                }}

                div[data-testid="stMetric"] {{
                    margin-bottom: 0.9rem;
                }}
            }}

            @media (max-width: 640px) {{
                div.block-container {{
                    padding: 1.4rem 1.1rem;
                }}

                .hero-header h1 {{
                    font-size: 1.85rem;
                }}

                .hero-subtitle {{
                    font-size: 0.95rem;
                }}

                .hero-badge {{
                    display: none;
                }}

                section[data-testid="stSidebar"] {{
                    width: 220px;
                }}

                .insight-message {{
                    font-size: 0.92rem;
                }}

                div[data-testid="stDataFrame"] {{
                    padding: 0.45rem 0.35rem 0.35rem 0.35rem;
                }}
            }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def apply_theme(theme_name: str) -> BrandTheme:
    """Apply the selected theme (Plotly + CSS) and return it."""

    theme = AVAILABLE_THEMES.get(theme_name, AVAILABLE_THEMES[DEFAULT_THEME_NAME])
    apply_plotly_theme(theme)
    inject_global_styles(theme)
    return theme


__all__ = [
    "BrandTheme",
    "NEON_THEME",
    "MIDNIGHT_THEME",
    "LUMA_THEME",
    "AVAILABLE_THEMES",
    "DEFAULT_THEME_NAME",
    "DEFAULT_PLOTLY_CONFIG",
    "apply_theme",
    "register_plotly_template",
    "apply_plotly_theme",
    "inject_global_styles",
]
