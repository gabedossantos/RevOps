"""Brand theming utilities for the RevOps Streamlit experience."""

from __future__ import annotations

from dataclasses import dataclass
from string import Template
from typing import Literal, Mapping, Sequence

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st


@dataclass(frozen=True)
class BrandTheme:
    """Brand system for the RevOps Control Center UI."""

    key: str = "default"
    base: Literal["light", "dark"] = "dark"
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

DARK_THEME = BrandTheme(
    key="dark",
    base="dark",
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

LIGHT_THEME = BrandTheme(
    key="light",
    base="light",
    gradient_background="linear-gradient(170deg, #F9FBFF 0%, #FFFFFF 45%, #EEF2FF 100%)",
    sidebar_background="rgba(255, 255, 255, 0.92)",
    surface_color="rgba(255, 255, 255, 0.98)",
    surface_border="rgba(203, 213, 225, 0.6)",
    overlay_shadow="0px 16px 40px rgba(148, 163, 184, 0.28)",
    text_color="#0F172A",
    muted_text="#475569",
    accent_primary="#2563EB",
    accent_secondary="#3B82F6",
    accent_tertiary="#6366F1",
    success="#16A34A",
    warning="#D97706",
    danger="#DC2626",
    border_radius="16px",
    colorway=(
        "#2563EB",
        "#3B82F6",
        "#10B981",
        "#F59E0B",
        "#6366F1",
        "#0EA5E9",
        "#F97316",
    ),
)

AVAILABLE_THEMES: Mapping[str, BrandTheme] = {
    "Dark Mode": DARK_THEME,
    "Light Mode": LIGHT_THEME,
}

DEFAULT_THEME_NAME = "Dark Mode"

DEFAULT_PLOTLY_CONFIG: Mapping[str, object] = {
    "displayModeBar": False,
    "scrollZoom": False,
    "responsive": True,
}
"""Default Plotly configuration applied to every chart render."""


def _surface_tokens(theme: BrandTheme) -> dict[str, str]:
    """Return derived surface colors and borders for the active theme."""

    is_dark = theme.base == "dark"
    return {
        "sidebar_panel_bg": theme.surface_color if is_dark else "rgba(255, 255, 255, 0.98)",
        "control_surface": "rgba(32, 42, 66, 0.82)" if is_dark else "rgba(255, 255, 255, 0.98)",
        "control_hover": "rgba(96, 165, 250, 0.35)" if is_dark else "rgba(37, 99, 235, 0.18)",
        "sidebar_backdrop": theme.sidebar_background if is_dark else "rgba(255, 255, 255, 0.88)",
        "control_border": theme.surface_border if is_dark else "rgba(203, 213, 225, 0.7)",
        "card_surface": theme.surface_color if is_dark else "rgba(255, 255, 255, 0.99)",
        "card_border": theme.surface_border if is_dark else "rgba(203, 213, 225, 0.55)",
        "chart_surface": "rgba(17, 24, 39, 0.78)" if is_dark else "rgba(255, 255, 255, 0.99)",
        "chart_border": theme.surface_border if is_dark else "rgba(226, 232, 240, 0.6)",
        "metric_value_color": theme.accent_secondary if is_dark else theme.accent_primary,
        "table_header_bg": "rgba(96, 165, 250, 0.18)" if is_dark else "rgba(37, 99, 235, 0.12)",
        "table_row_border": "rgba(148, 163, 184, 0.22)" if is_dark else "rgba(226, 232, 240, 0.65)",
        "toggle_track_inactive": "rgba(99, 102, 241, 0.35)" if is_dark else "rgba(148, 163, 184, 0.4)",
        "toggle_glint": theme.accent_secondary if is_dark else theme.accent_primary,
    }


def register_plotly_template(theme: BrandTheme) -> str:
    """Register and return the custom Plotly template name."""

    template_name = f"revops-{theme.key}"
    if template_name in pio.templates:
        return template_name

    surfaces = _surface_tokens(theme)
    grid_color = (
        "rgba(148, 163, 184, 0.35)" if theme.base == "light" else "rgba(148, 163, 184, 0.25)"
    )
    hover_bg = "rgba(255, 255, 255, 0.9)" if theme.base == "light" else "rgba(15, 23, 42, 0.85)"

    template = go.layout.Template(
        layout=dict(
            font=dict(family=theme.font_family, color=theme.text_color, size=14),
            title=dict(font=dict(size=26, color=theme.text_color, family=theme.font_family), x=0.02),
            paper_bgcolor=surfaces["chart_surface"],
            plot_bgcolor=surfaces["chart_surface"],
            colorway=list(theme.colorway),
            legend=dict(
                bgcolor=surfaces["chart_surface"],
                bordercolor=surfaces["chart_border"],
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

    tokens = _surface_tokens(theme)
    accent_primary1f = f"{theme.accent_primary}1f"
    accent_secondary1f = f"{theme.accent_secondary}1f"
    accent_primarycc = f"{theme.accent_primary}cc"
    accent_secondarycc = f"{theme.accent_secondary}cc"
    accent_primary26 = f"{theme.accent_primary}26"
    accent_secondary26 = f"{theme.accent_secondary}26"

    mode_specific_rules = ""
    if theme.base == "light":
        tokens_for_light = tokens
        light_surface = tokens_for_light["card_surface"]
        light_border = tokens_for_light["card_border"]
        table_header_bg = tokens_for_light["table_header_bg"]
        table_border = tokens_for_light["table_row_border"]
        control_hover = tokens_for_light["control_hover"]
        mode_specific_rules = f"""
            body[data-theme-mode="light"] div[data-testid="stAppViewContainer"] {{
                background: {theme.gradient_background};
                color: {theme.text_color};
            }}

            body[data-theme-mode="light"] .stTabs [data-baseweb="tab"] {{
                background: {light_surface} !important;
                border-color: {light_border} !important;
                color: {theme.muted_text} !important;
            }}

            body[data-theme-mode="light"] .stTabs [aria-selected="true"] {{
                color: {theme.text_color} !important;
            }}

            body[data-theme-mode="light"] div[data-testid="stPlotlyChart"] {{
                background: {light_surface} !important;
                border-color: {light_border} !important;
            }}

            body[data-theme-mode="light"] div[data-testid="stPlotlyChart"] .plotly .bg,
            body[data-theme-mode="light"] div[data-testid="stPlotlyChart"] .plotly .cartesianlayer .bg,
            body[data-theme-mode="light"] div[data-testid="stPlotlyChart"] .plotly .legend rect,
            body[data-theme-mode="light"] div[data-testid="stPlotlyChart"] .plotly .legend path {{
                fill: {light_surface} !important;
            }}

            body[data-theme-mode="light"] div[data-testid="stDataFrame"] {{
                background: {light_surface} !important;
                border-color: {light_border} !important;
                color: {theme.text_color} !important;
            }}

            body[data-theme-mode="light"] div[data-testid="stDataFrame"] table {{
                color: {theme.text_color} !important;
            }}

            body[data-theme-mode="light"] div[data-testid="stDataFrame"] thead tr {{
                background: {table_header_bg} !important;
            }}

            body[data-theme-mode="light"] div[data-testid="stDataFrame"] tbody td {{
                border-color: {table_border} !important;
            }}

            body[data-theme-mode="light"] div[data-testid="stSelectbox"] > div,
            body[data-theme-mode="light"] div[data-testid="stMultiSelect"] > div,
            body[data-theme-mode="light"] div[data-testid="stDateInput"] > div,
            body[data-theme-mode="light"] div[data-baseweb="select"],
            body[data-theme-mode="light"] div[data-baseweb="input"],
            body[data-theme-mode="light"] div[data-baseweb="datepicker"] {{
                background: {light_surface} !important;
                border: 1px solid {light_border} !important;
                color: {theme.text_color} !important;
            }}

            body[data-theme-mode="light"] div[data-baseweb="select"] input,
            body[data-theme-mode="light"] div[data-baseweb="input"] input,
            body[data-theme-mode="light"] div[data-baseweb="datepicker"] input {{
                color: {theme.text_color} !important;
            }}

            body[data-theme-mode="light"] div[data-baseweb="popover"] {{
                background: {light_surface} !important;
                border: 1px solid {light_border} !important;
                box-shadow: {theme.overlay_shadow} !important;
            }}

            body[data-theme-mode="light"] div[data-baseweb="popover"] ul {{
                background: transparent !important;
            }}

            body[data-theme-mode="light"] div[data-baseweb="popover"] li,
            body[data-theme-mode="light"] div[data-baseweb="popover"] input {{
                color: {theme.text_color} !important;
            }}

            body[data-theme-mode="light"] div[data-baseweb="popover"] li:hover,
            body[data-theme-mode="light"] div[data-baseweb="popover"] li[data-baseweb="option"]:hover {{
                background: {control_hover} !important;
            }}

            body[data-theme-mode="light"] div[data-baseweb="tag"] {{
                background: linear-gradient(135deg, {theme.accent_primary}, {theme.accent_secondary}) !important;
                color: #f8fafc !important;
                border: none !important;
                box-shadow: 0px 12px 24px rgba(37, 99, 235, 0.22) !important;
            }}

            body[data-theme-mode="light"] div[data-baseweb="tag"] span,
            body[data-theme-mode="light"] div[data-baseweb="tag"] svg path,
            body[data-theme-mode="light"] div[data-baseweb="tag"] svg polygon {{
                fill: #f8fafc !important;
                color: #f8fafc !important;
            }}

            body[data-theme-mode="light"] button[kind="secondary"] {{
                background: {light_surface} !important;
                border-color: {light_border} !important;
                color: {theme.muted_text} !important;
            }}

            body[data-theme-mode="light"] button[kind="secondary"]:hover,
            body[data-theme-mode="light"] button[kind="secondary"][aria-pressed="true"] {{
                color: {theme.text_color} !important;
                border-color: {theme.accent_primary} !important;
            }}

            body[data-theme-mode="light"] section[data-testid="stSidebar"] {{
                background: {theme.sidebar_background} !important;
            }}
        """

    template = Template(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@500;600&display=swap');

            :root {
                color-scheme: $color_scheme;
                --brand-surface: $surface_color;
                --brand-border: $surface_border;
                --brand-radius: $border_radius;
                --brand-shadow: $overlay_shadow;
                --brand-text: $text_color;
                --brand-muted: $muted_text;
                --brand-accent: $accent_primary;
                --brand-accent-secondary: $accent_secondary;
                --brand-accent-tertiary: $accent_tertiary;
                --sidebar-panel-bg: $sidebar_panel_bg;
                --sidebar-control-bg: $control_surface;
                --sidebar-control-hover: $control_hover;
                --sidebar-control-border: $control_border;
                --sidebar-background: $sidebar_backdrop;
                --card-surface: $card_surface;
                --card-border: $card_border;
                --chart-surface: $chart_surface;
                --chart-border: $chart_border;
                --metric-value: $metric_value_color;
                --table-header-bg: $table_header_bg;
                --table-border: $table_row_border;
                --toggle-track-active: linear-gradient(135deg, $accent_primary, $accent_secondary);
                --toggle-track-inactive: $toggle_track_inactive;
                --toggle-thumb-glint: $toggle_glint;
            }

            html, body, [class*="css"] {
                font-family: $font_family;
            }

            body {
                color: $text_color;
                background: $gradient_background !important;
            }

            div[data-testid="stAppViewContainer"] {
                background: $gradient_background;
                color: $text_color;
            }

            header[data-testid="stHeader"] {
                background: transparent;
            }

            section[data-testid="stSidebar"] {
                background: var(--sidebar-background);
                backdrop-filter: blur(22px);
                border-right: 1px solid var(--brand-border);
            }

            section[data-testid="stSidebar"] .block-container {
                background: var(--sidebar-panel-bg);
                border-radius: calc($border_radius - 6px);
                padding: 1.2rem 1.05rem 1.6rem;
                border: 1px solid var(--brand-border);
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(18px);
            }

            section[data-testid="stSidebar"] .block-container > *:not(:last-child) {
                margin-bottom: 0.85rem;
            }

            section[data-testid="stSidebar"] * {
                color: var(--brand-text) !important;
            }

            section[data-testid="stSidebar"] .stMarkdown,
            section[data-testid="stSidebar"] .stMarkdown p {
                color: var(--brand-muted) !important;
            }

            .theme-toggle {
                margin: 0.6rem 0 0.4rem;
            }

            .theme-toggle::before {
                content: "Color mode";
                display: block;
                font-size: 0.68rem;
                letter-spacing: 0.2em;
                text-transform: uppercase;
                font-weight: 600;
                color: var(--brand-muted);
                margin-bottom: 0.45rem;
            }

            .theme-toggle > div[role="radiogroup"] {
                display: flex;
                gap: 0.35rem;
                background: var(--sidebar-control-bg);
                border: 1px solid var(--sidebar-control-border);
                border-radius: 999px;
                padding: 0.25rem;
            }

            .theme-toggle [role="radio"] {
                flex: 1;
                position: relative;
                text-align: center;
                border-radius: 999px;
                padding: 0.45rem 0.75rem;
                font-weight: 600;
                letter-spacing: 0.08em;
                text-transform: uppercase;
                color: var(--brand-muted);
                cursor: pointer;
                transition: all 0.25s ease;
            }

            .theme-toggle [role="radio"]::after {
                content: "";
                position: absolute;
                inset: 2px;
                border-radius: 999px;
                background: transparent;
                opacity: 0;
                transition: opacity 0.25s ease;
            }

            .theme-toggle [role="radio"][aria-checked="true"] {
                background: var(--toggle-track-active);
                color: var(--brand-text);
                box-shadow: 0 12px 26px rgba(37, 99, 235, 0.28);
            }

            .theme-toggle [role="radio"][aria-checked="true"]::after {
                opacity: 1;
                background: linear-gradient(135deg, transparent, var(--toggle-thumb-glint)33);
            }

            .theme-toggle [role="radio"]:hover {
                box-shadow: 0 0 0 2px var(--sidebar-control-hover);
            }

            .sidebar-title {
                font-size: 1.05rem;
                font-weight: 600;
                color: var(--brand-text);
                margin-bottom: 0.35rem;
            }

            .sidebar-subtitle {
                font-size: 0.85rem;
                line-height: 1.5;
                color: var(--brand-muted);
                margin-bottom: 1.1rem;
            }

            section[data-testid="stSidebar"] label {
                color: var(--brand-text) !important;
                font-weight: 500;
            }

            section[data-testid="stSidebar"] .stSelectbox > div,
            section[data-testid="stSidebar"] .stMultiSelect > div,
            section[data-testid="stSidebar"] .stDateInput > div {
                background: var(--sidebar-control-bg);
                border: 1px solid var(--sidebar-control-border);
                border-radius: 12px;
                box-shadow: none;
                transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
            }

            section[data-testid="stSidebar"] div[data-baseweb="select"],
            section[data-testid="stSidebar"] div[data-baseweb="popover"],
            section[data-testid="stSidebar"] div[data-baseweb="input"],
            section[data-testid="stSidebar"] div[data-baseweb="datepicker"] {
                background: var(--sidebar-control-bg) !important;
                border: 1px solid var(--sidebar-control-border) !important;
                border-radius: 12px !important;
                box-shadow: none !important;
                transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
            }

            section[data-testid="stSidebar"] div[data-baseweb="select"] > div,
            section[data-testid="stSidebar"] div[data-baseweb="input"] > div,
            section[data-testid="stSidebar"] div[data-baseweb="datepicker"] > div {
                background: transparent !important;
            }

            section[data-testid="stSidebar"] .stSelectbox > div:hover,
            section[data-testid="stSidebar"] .stMultiSelect > div:hover,
            section[data-testid="stSidebar"] .stDateInput > div:hover,
            section[data-testid="stSidebar"] .stSelectbox > div:focus-within,
            section[data-testid="stSidebar"] .stMultiSelect > div:focus-within,
            section[data-testid="stSidebar"] .stDateInput > div:focus-within {
                border-color: $accent_primary;
                box-shadow: 0 0 0 2px var(--sidebar-control-hover);
            }

            section[data-testid="stSidebar"] input,
            section[data-testid="stSidebar"] span,
            section[data-testid="stSidebar"] select {
                color: var(--brand-text) !important;
            }

            div[data-testid="stSelectbox"] > div,
            div[data-testid="stMultiSelect"] > div,
            div[data-testid="stDateInput"] > div {
                background: var(--card-surface) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 12px !important;
                box-shadow: none !important;
                transition: border-color 0.2s ease, box-shadow 0.2s ease, background 0.2s ease;
            }

            div[data-testid="stSelectbox"] > div:hover,
            div[data-testid="stMultiSelect"] > div:hover,
            div[data-testid="stDateInput"] > div:hover,
            div[data-testid="stSelectbox"] > div:focus-within,
            div[data-testid="stMultiSelect"] > div:focus-within,
            div[data-testid="stDateInput"] > div:focus-within {
                border-color: $accent_primary !important;
                box-shadow: 0 0 0 2px $accent_primary26 !important;
            }

            div[data-testid="stSelectbox"] label,
            div[data-testid="stMultiSelect"] label,
            div[data-testid="stDateInput"] label {
                color: var(--brand-muted) !important;
                font-weight: 500;
            }

            div[data-testid="stSelectbox"] input,
            div[data-testid="stMultiSelect"] input,
            div[data-testid="stDateInput"] input {
                color: var(--brand-text) !important;
            }

            div[data-baseweb="select"],
            div[data-baseweb="input"],
            div[data-baseweb="datepicker"] {
                background: var(--card-surface) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 12px !important;
                box-shadow: none !important;
            }

            div[data-baseweb="popover"] {
                background: var(--card-surface) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 14px !important;
                box-shadow: var(--brand-shadow) !important;
            }

            div[data-baseweb="popover"] ul {
                background: transparent !important;
            }

            div[data-baseweb="popover"] li {
                color: var(--brand-text) !important;
                border-radius: 8px;
                margin: 2px 4px;
            }

            div[data-baseweb="popover"] input {
                color: var(--brand-text) !important;
            }

            div[data-baseweb="popover"] li:hover,
            div[data-baseweb="popover"] li[data-baseweb="option"]:hover {
                background: $accent_primary26 !important;
            }

            div[data-baseweb="tag"] {
                background: linear-gradient(135deg, $accent_primary, $accent_secondary) !important;
                color: #f8fafc !important;
                border: none !important;
                border-radius: 12px !important;
                box-shadow: 0px 12px 24px rgba(37, 99, 235, 0.22) !important;
                font-weight: 600;
                letter-spacing: 0.01em;
            }

            div[data-baseweb="tag"] span {
                color: #f8fafc !important;
            }

            div[data-baseweb="tag"] svg path,
            div[data-baseweb="tag"] svg polygon {
                fill: #f8fafc !important;
            }

            div.block-container {
                padding-top: 2.6rem;
                max-width: 1180px;
            }

            div[data-testid="stHorizontalBlock"] {
                gap: 0.65rem !important;
                align-items: stretch;
            }

            div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
                padding: 0 0.15rem;
            }

            div[data-testid="stHorizontalBlock"] button[kind] {
                width: 100%;
            }

            .hero-header {
                display: flex;
                flex-direction: column;
                gap: 1.8rem;
                background: var(--card-surface);
                border: 1px solid var(--card-border);
                border-radius: var(--brand-radius);
                padding: 2.2rem 2.4rem;
                margin-bottom: 1.8rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(24px);
            }

            .hero-header h1 {
                font-size: 2.3rem;
                line-height: 1.18;
                margin-bottom: 0.55rem;
                color: var(--brand-text);
            }

            .hero-subtitle {
                font-size: 1.02rem;
                color: var(--brand-muted);
                max-width: 560px;
                margin-bottom: 0.35rem;
            }

            .hero-theme {
                display: inline-flex;
                align-items: center;
                gap: 0.35rem;
                margin-top: 0.35rem;
                padding: 0.35rem 0.8rem;
                border-radius: 999px;
                border: 1px solid var(--card-border);
                background: linear-gradient(135deg, $accent_primary1f, $accent_secondary1f);
                color: var(--brand-text);
                font-size: 0.78rem;
                font-weight: 600;
                letter-spacing: 0.05em;
                text-transform: uppercase;
            }

            .hero-eyebrow {
                font-size: 0.75rem;
                letter-spacing: 0.28em;
                text-transform: uppercase;
                font-weight: 600;
                color: var(--brand-accent-secondary);
                margin-bottom: 0.75rem;
            }

            .stTabs [data-baseweb="tab-list"] {
                gap: 0.75rem;
                border-bottom: 1px solid var(--card-border);
            }

            .stTabs [data-baseweb="tab"] {
                padding: 0.75rem 1.4rem;
                background: var(--card-surface) !important;
                background-color: var(--card-surface) !important;
                border: 1px solid var(--card-border) !important;
                border-radius: 999px;
                color: var(--brand-muted) !important;
                font-weight: 600;
                transition: all 0.25s ease;
            }

            .stTabs [aria-selected="true"] {
                background: linear-gradient(135deg, $accent_primarycc, $accent_secondarycc);
                background-color: transparent;
                color: var(--brand-text);
                box-shadow: 0px 16px 38px rgba(37, 99, 235, 0.28);
                border-color: transparent;
            }

            div[data-testid="stMetric"] {
                background: var(--card-surface);
                border: 1px solid var(--card-border);
                border-radius: var(--brand-radius);
                padding: 1.05rem 1.25rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(20px);
            }

            div[data-testid="stMetricValue"] {
                color: var(--metric-value);
                font-size: 1.7rem;
                font-weight: 600;
            }

            div[data-testid="stMetricLabel"] {
                color: var(--brand-muted) !important;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }

            div[data-testid="stPlotlyChart"] {
                background: var(--chart-surface) !important;
                border: 1px solid var(--chart-border) !important;
                border-radius: var(--brand-radius);
                padding: 0.25rem 0.35rem 0.45rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(18px);
                box-sizing: border-box;
                max-width: 100%;
                overflow: hidden;
            }

            div[data-testid="stPlotlyChart"] svg {
                background: transparent;
            }

            div[data-testid="stPlotlyChart"] > div:first-child {
                width: 100% !important;
                margin: 0 auto;
            }

            div[data-testid="stPlotlyChart"] .plot-container,
            div[data-testid="stPlotlyChart"] .plotly,
            div[data-testid="stPlotlyChart"] svg {
                background: transparent !important;
            }

            div[data-testid="stPlotlyChart"] .plotly .bg,
            div[data-testid="stPlotlyChart"] .plotly .subplot.xy .bg,
            div[data-testid="stPlotlyChart"] .plotly .cartesianlayer .bg {
                fill: var(--chart-surface) !important;
            }

            div[data-testid="stPlotlyChart"] .plotly .hoverlayer path {
                fill: var(--chart-surface) !important;
            }

            div[data-testid="stPlotlyChart"] .plotly .legend path,
            div[data-testid="stPlotlyChart"] .plotly .legend rect {
                fill: var(--chart-surface) !important;
            }

            div[data-testid="column"] {
                min-width: 0 !important;
            }

            div[data-testid="stDataFrame"] {
                background: var(--card-surface);
                border: 1px solid var(--card-border);
                border-radius: var(--brand-radius);
                padding: 0.65rem 0.55rem 0.5rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(18px);
            }

            div[data-testid="stDataFrame"] table {
                font-family: $font_family;
                color: var(--brand-text);
            }

            div[data-testid="stDataFrame"] thead tr {
                background: var(--table-header-bg);
            }

            div[data-testid="stDataFrame"] tbody td {
                border-color: var(--table-border) !important;
            }

            .stSelectbox,
            .stMultiSelect,
            .stDateInput {
                border-radius: 12px !important;
            }

            div[data-testid="stFormSubmitButton"] button,
            button[kind="primary"],
            div[data-testid="stFormSubmitButton"] button {
                border-radius: 14px;
                background: linear-gradient(135deg, $accent_primary, $accent_secondary);
                border: 1px solid transparent;
                color: white;
                font-weight: 600;
                font-size: 0.9rem;
                padding: 0.6rem 1.25rem;
                min-height: 44px;
                box-shadow: 0px 12px 28px rgba(99, 102, 241, 0.32);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            button[kind="primary"]:hover,
            div[data-testid="stFormSubmitButton"] button:hover {
                transform: translateY(-1px);
                box-shadow: 0px 18px 36px rgba(99, 102, 241, 0.34);
            }

            button[kind="primary"]:focus-visible,
            div[data-testid="stFormSubmitButton"] button:focus-visible {
                outline: 2px solid $accent_primary26;
                outline-offset: 2px;
            }

            button[kind="secondary"] {
                border-radius: 14px;
                background: var(--card-surface) !important;
                border: 1px solid var(--card-border) !important;
                color: var(--brand-muted) !important;
                font-weight: 600;
                font-size: 0.9rem;
                padding: 0.6rem 1.1rem;
                min-height: 44px;
                line-height: 1.15;
                letter-spacing: 0.01em;
                text-transform: none;
                box-shadow: none !important;
                transition: all 0.22s ease;
            }

            button[kind="secondary"]:hover,
            button[kind="secondary"][aria-pressed="true"],
            button[kind="secondary"]:focus-visible {
                color: var(--brand-text) !important;
                border-color: $accent_primary !important;
                box-shadow: 0px 12px 28px rgba(37, 99, 235, 0.18) !important;
            }

            button[kind="secondary"]:focus-visible {
                outline: 2px solid $accent_primary26;
                outline-offset: 2px;
            }

            div[data-testid="stMarkdown"] h1,
            div[data-testid="stMarkdown"] h2,
            div[data-testid="stMarkdown"] h3,
            .stMarkdown h1,
            .stMarkdown h2,
            .stMarkdown h3 {
                color: var(--brand-text);
                font-weight: 650;
            }

            .insight-card {
                background: var(--card-surface);
                border: 1px solid var(--card-border);
                border-radius: calc($border_radius - 6px);
                padding: 1.2rem 1.4rem;
                margin-bottom: 0.6rem;
                box-shadow: var(--brand-shadow);
                backdrop-filter: blur(16px);
            }

            .insight-card--marketing {
                border-left: 4px solid $accent_primary;
            }

            .insight-card--pipeline {
                border-left: 4px solid $accent_secondary;
            }

            .insight-card--revenue {
                border-left: 4px solid $accent_tertiary;
            }

            .insight-chip {
                display: inline-block;
                font-size: 0.7rem;
                letter-spacing: 0.16em;
                text-transform: uppercase;
                color: $accent_secondary;
            }

            .insight-message {
                font-size: 1.02rem;
                color: var(--brand-text);
                margin: 0.35rem 0 0.2rem 0;
            }

            div[data-testid="stProgressBar"] {
                background: linear-gradient(90deg, $accent_primary26, $accent_secondary26);
                border-radius: 999px;
                height: 10px;
                margin: 0.4rem 0 0.7rem 0;
            }

            div[data-testid="stProgressBar"] > div {
                background: linear-gradient(135deg, $accent_primary, $accent_secondary);
                border-radius: 999px;
            }

            .stDivider {
                border-top: 1px solid var(--card-border) !important;
            }

            @media (max-width: 1200px) {
                div.block-container {
                    max-width: 100%;
                    padding: 2rem 1.8rem;
                }

                .hero-header {
                    padding: 1.9rem 1.8rem;
                }

                .stTabs [data-baseweb="tab-list"] {
                    overflow-x: auto;
                    padding-bottom: 0.5rem;
                }

                .stTabs [data-baseweb="tab"] {
                    flex: 0 0 auto;
                }
            }

            @media (max-width: 960px) {
                .hero-header {
                    padding: 1.7rem 1.5rem;
                }

                section[data-testid="stSidebar"] {
                    width: 260px;
                }

                div[data-testid="column"] {
                    flex: 1 1 100% !important;
                    min-width: 100% !important;
                }

                div[data-testid="stMetric"] {
                    margin-bottom: 0.9rem;
                }
            }

            @media (max-width: 640px) {
                div.block-container {
                    padding: 1.4rem 1.1rem;
                }

                .hero-header h1 {
                    font-size: 1.85rem;
                }

                .hero-subtitle {
                    font-size: 0.95rem;
                }

                section[data-testid="stSidebar"] {
                    width: 220px;
                }

                .insight-message {
                    font-size: 0.92rem;
                }

                div[data-testid="stDataFrame"] {
                    padding: 0.45rem 0.35rem 0.35rem;
                }
            }

            $mode_specific_rules
        </style>
        <script>
            const body = document.body;
            if (body) {
                body.dataset.themeMode = "$color_scheme";
            }
            document.documentElement.dataset.themeMode = "$color_scheme";
        </script>
        """
    )

    css = template.substitute(
        color_scheme=theme.base,
        surface_color=theme.surface_color,
        surface_border=theme.surface_border,
        border_radius=theme.border_radius,
        overlay_shadow=theme.overlay_shadow,
        text_color=theme.text_color,
        muted_text=theme.muted_text,
        accent_primary=theme.accent_primary,
        accent_secondary=theme.accent_secondary,
        accent_tertiary=theme.accent_tertiary,
        font_family=theme.font_family,
        gradient_background=theme.gradient_background,
        accent_primary1f=accent_primary1f,
        accent_secondary1f=accent_secondary1f,
        accent_primarycc=accent_primarycc,
        accent_secondarycc=accent_secondarycc,
        accent_primary26=accent_primary26,
        accent_secondary26=accent_secondary26,
        mode_specific_rules=mode_specific_rules,
        **tokens,
    )

    st.markdown(css, unsafe_allow_html=True)


def apply_theme(theme_name: str) -> BrandTheme:
    """Apply the selected theme (Plotly + CSS) and return it."""

    theme = AVAILABLE_THEMES.get(theme_name, AVAILABLE_THEMES[DEFAULT_THEME_NAME])
    apply_plotly_theme(theme)
    inject_global_styles(theme)
    st.session_state["_brand_theme"] = theme
    st.session_state["_brand_surface_tokens"] = _surface_tokens(theme)
    return theme


__all__ = [
    "BrandTheme",
    "DARK_THEME",
    "LIGHT_THEME",
    "AVAILABLE_THEMES",
    "DEFAULT_THEME_NAME",
    "DEFAULT_PLOTLY_CONFIG",
    "apply_theme",
    "register_plotly_template",
    "apply_plotly_theme",
    "inject_global_styles",
]
