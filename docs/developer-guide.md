# RevOps Control Center — Developer Guide

## Purpose

This guide is the canonical reference for engineers extending or maintaining the RevOps Control Center. It documents the repository layout, runtime architecture, data contracts, build tooling, and recommended extension patterns.

---

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
streamlit run streamlit_app/app.py
```

- **Python version**: 3.9+ (validated on 3.13.4)
- **Primary entry point**: `streamlit_app/app.py`
- **Test suite**: `pytest`
- **Synthetic data CLI**: `python -m revops.data_generation --output <dir>`

---

## Architecture overview

```text
CSV datasets ─┐
              ├─▶ Data loaders (`revops.data`) ─▶ Analytics layer (`revops.analytics`) ─▶ Streamlit UI (`streamlit_app/app.py`)
Synthetic CLI ┘                                 │
                                                └─▶ AI insights (`revops.ai.insights`)
```

| Layer | Modules | Responsibilities |
| --- | --- | --- |
| Data access | `revops.config`, `revops.data` | Resolve canonical CSV paths, lazily load DataFrames with caching, expose `clear_caches()` for tests. |
| Analytics | `revops.analytics.*` | Compute KPIs, aggregations, and chart-ready DataFrames for marketing, pipeline, and revenue domains. |
| Insights | `revops.ai.insights` | Generate rule-based guidance derived from analytics outputs. |
| Presentation | `streamlit_app/app.py`, `streamlit_app/theme.py` | Compose the dashboard, manage filters, apply branding, render Plotly charts and Streamlit components. |
| Data generation | `revops.data_generation` | Produce synthetic CSVs that match validation schemas for local demos and testing. |
| Validation & QA | `revops.validation`, `tests/` | Enforce schema contracts via Pydantic models and cover analytics logic with pytest. |

---

## Repository layout

```
revops/
├── streamlit_app/         # Front-end dashboard
├── src/revops/            # Installable Python package
│   ├── analytics/         # KPI calculators and helpers
│   ├── ai/                # Rule-based insight engine
│   ├── data.py            # Cached CSV loaders
│   ├── data_generation.py # Synthetic data factories & CLI
│   ├── validation.py      # Dataset schema validators
│   └── config.py          # Data path configuration
├── tests/                 # Pytest suite with shared fixtures
├── marketing_channels.csv # Canonical input datasets
├── pipeline_deals.csv
├── revenue_customers.csv
├── benchmarks.csv
└── docs/                  # Architecture and usage documentation
```

The project is packaged as an editable install (`pip install -e .`) to make modules importable from scripts, tests, and Streamlit. `streamlit_app/app.py` adjusts `sys.path` defensively for `streamlit run` executions.

---

## Data contracts

All datasets are locally stored CSV files. The contract is enforced via Pydantic models inside `revops.validation`.

### Marketing (`marketing_channels.csv`)

| Column | Type | Notes |
| --- | --- | --- |
| `date` | ISO date | Daily granularity |
| `channel` | str | Acquisition channel |
| `campaign` | str | Campaign label |
| `segment` | {SMB, MM, ENT} | Customer segment |
| `geo` | str | Region |
| `spend` | float | Daily spend |
| `impressions`, `clicks`, `leads`, `MQLs`, `SQLs`, `opportunities`, `closed_won` | int | Funnel counts |
| `CAC`, `CPL` | float | Cost metrics |
| `CTR`, `CVR_stagewise` | float | Rates (0–1) |
| `ROI` | float | Percentage (0–∞) |

### Pipeline (`pipeline_deals.csv`)

Contains deal metadata including stage, owner, monetary values, timestamps, probability, and status.

### Revenue (`revenue_customers.csv`)

Tracks per-customer MRR components, churn indicators, expansion/contraction, ARPA, and NRR.

### Benchmarks (`benchmarks.csv`)

Reference targets by metric (e.g., `channel_cpl_range`, `nrr_targets`). Used by validation tests and available for future benchmark overlays.

---

## Data generation CLI

`revops.data_generation` synthesizes all four datasets with deterministic seeding.

- `generate_marketing_data()` loops over channels × segments × day, applying probabilistic models to generate spend, funnel progression, and derived metrics.
- `generate_pipeline_data()` produces deal-level records with log-normal amounts, stage probabilities, and deal health values.
- `generate_revenue_data()` simulates customer lifecycles with churn/expansion probabilities.
- `generate_benchmarks_data()` emits industry benchmark records for future comparisons.

CLI usage writes fresh CSVs to the target directory and prints resolved paths. The generated files align with the validation schemas.

---

## Data loading & caching

- `revops.config.DataPaths` centralizes file locations with `DEFAULT_DATA_PATHS` pointing to repository CSVs.
- `revops.data` exposes `get_marketing_df`, `get_pipeline_df`, `get_revenue_df`, and `get_benchmarks_df`. Each loader uses `functools.lru_cache` to avoid rereading files during a session.
- `clear_caches()` resets loaders (pytest uses an autouse fixture to clear caches between tests).
- The Streamlit app wraps `load_data()` with `@st.cache_data`, adding UI-level memoization on top of the package caches.

---

## Filter pipeline

The reusable `FilterSet` dataclass (`revops.analytics.utils`) carries start/end dates, segments, channels, and regions. `FilterSet.apply()` normalizes the date column and applies boolean masks.

- Streamlit sidebar controls (`build_filters`) assemble the `FilterSet` for cross-tab consistency.
- Analytics functions accept an optional filter to produce scoped KPIs and aggregations.
- Default behavior is inclusive (no filters set → entire dataset).

---

## Analytics modules

Each analytics module returns primitive Python types or pandas `DataFrame` objects ready for visualization.

### Marketing

- `marketing_kpis()` → totals and averages for spend, funnel counts, CAC, ROI.
- `channel_performance()` → grouped channel stats with conversion and ROI fields.
- `funnel_breakdown()` → stage funnel counts for Plotly funnel charts.
- `trend_timeseries()` → weekly resampled time series of leads/MQLs/SQLs.

### Pipeline

- `pipeline_kpis()` → pipeline totals, weighted value, average deal size, win rate, velocity.
- `stage_distribution()` → stage-level deal counts/amounts for bar charts.
- `owner_performance()` → per-owner totals with computed win rate and cycle time.
- `stuck_deals()` → open deals filtered by age and amount thresholds.

### Revenue

- `revenue_kpis()` → MRR, ARR, average NRR, churn rate.
- `segment_breakdown()` → segment-level revenue composition.
- `mrr_waterfall()` → month-end waterfall table for stacked Plotly bars.
- `churn_reasons()` → churn counts by reason and segment.

### Shared utilities

- `_safe_divide()` prevents division by zero (returns 0.0 fallback).
- `FilterSet` detailed above.

---

## Rule-based insights engine

`revops.ai.insights` defines a Pydantic `Insight` model and deterministic heuristics:

- **Marketing insights** highlight top-performing channels, low conversion funnels, and low ROI alerts.
- **Pipeline insights** surface low win rate, stuck deal totals, and pipeline velocity issues.
- **Revenue insights** flag elevated churn, dominant churn reasons, and sub-105% NRR.

`generate_insights()` aggregates lists from all domains and returns objects the UI renders with category-specific styling. Confidence scores are normalized to 5–95% for visual consistency.

---

## Streamlit presentation layer

### Entry point (`streamlit_app/app.py`)

1. Ensures `src/` is importable when executed via Streamlit.
2. Calls `load_data()` (cached) to fetch marketing, pipeline, and revenue DataFrames.
3. Builds the global filter UI and theme selector in the sidebar.
4. Renders a hero header indicating the active theme and data freshness.
5. Defines four tabs (Marketing, Pipeline, Revenue, AI Co-Pilot) and delegates rendering to domain-specific functions.
6. Uses Plotly Express for charts and Streamlit metrics/dataframes for tabular data.

### Theming (`streamlit_app/theme.py`)

- `BrandTheme` dataclass encapsulates typography, gradients, colorway, spacing, and component tokens.
- Three presets are shipped by default: **Midnight Aurora** (modern dark), **Luma Skyline** (light), and **Neon Pulse (Legacy)**.
- `apply_theme()` registers a Plotly template and injects global CSS with responsive breakpoints.
- `DEFAULT_PLOTLY_CONFIG` ensures consistent chart interactivity (no mode bar, responsive sizing).
- Sidebar theme selector persists choice in `st.session_state` for current session.

### Responsiveness & UX

- Metric grids use a helper to lay out KPIs in configurable column widths.
- Custom CSS defines glassmorphism surfaces, hero layout, tab styling, and responsive breakpoints down to mobile widths.
- Insight cards are styled with category color accents and progress bars.

---

## Testing strategy

- **Fixtures** (`tests/conftest.py`): load DataFrames via package loaders and clear caches after each test.
- **Analytics tests**: verify KPI outputs, ordering, and filter behavior for marketing, pipeline, and revenue modules.
- **Insights tests**: ensure the engine yields at least one insight per run.
- **Validation tests**: enforce schema alignment for all datasets (including benchmarks) using Pydantic models.

Run all tests with `pytest` (fast, <5 seconds on reasonable hardware).

---

## Extensibility guidelines

### Adding a new metric or chart

1. Extend the appropriate analytics module with a pure function returning either a scalar dict or DataFrame.
2. Cover the logic with a pytest in `tests/test_<domain>.py`.
3. Update `streamlit_app/app.py` to render the new metric or chart.
4. If new data columns are required, update the generator, validator, and sample CSVs.

### Introducing a new theme

1. Define a new `BrandTheme` instance in `streamlit_app/theme.py`.
2. Add it to `AVAILABLE_THEMES` with a human-readable label.
3. Optionally adjust `.streamlit/config.toml` to match the preferred default palette.

### Integrating external data sources

- Implement a custom `DataPaths` instance pointing to alternative CSVs or database export.
- Pass the custom paths into `get_*_df()` where necessary (e.g., CLI script or Streamlit session state).
- Ensure `clear_caches()` is called when switching data sources at runtime.

### Evolving the AI engine

- Swap rule weights or thresholds in `marketing_insights`, `pipeline_insights`, and `revenue_insights`.
- The Pydantic `Insight` model can be extended with new fields (e.g., `action_items`). Update UI rendering accordingly.
- Plan for future extensibility by replacing heuristics with API calls returning the same schema if needed.

---

## Deployment considerations

- The project currently targets Streamlit (community cloud, Streamlit sharing, or containerized deployment).
- Ensure environment installs the editable package (`pip install -e .`) and sets `PYTHONPATH` to include `src/` if running outside Streamlit.
- For container builds, copy CSV datasets into the image or mount them at runtime; adjust `DEFAULT_DATA_PATHS` or supply `DataPaths` overrides.
- `.streamlit/config.toml` aligns native Streamlit colors with the Midnight theme for consistent local vs. hosted appearance.

---

## Observability & logging

- The current implementation relies on Streamlit diagnostics and pandas exceptions. Consider wrapping analytics calls with structured logging if deploying at scale.
- Validation helpers raise explicit `ValueError` or `FileNotFoundError` for missing or malformed data. Catch these in ingestion pipelines or CLI automation.

---

## Roadmap suggestions

- Persist sidebar filter selections and theme choice using `st.session_state` or query parameters.
- Overlay `benchmarks.csv` values on charts to highlight gaps vs. targets.
- Implement drill-down pages per channel or segment using Streamlit multipage support.
- Replace deterministic insights with a service-based approach while retaining the `Insight` schema if needed.
- Build CI workflows to run `pytest` and linting checks on pull requests.

---

## Reference links

- `README.md` — high-level product overview and setup.
- `docs/architecture-plan.md` — initial architecture goals.
- `revops-dashboard-spec.md` — future Next.js experience (not yet implemented).
- `revops_data_model.png`, `revops_architecture.png` — visual assets supporting roadmap conversations.
