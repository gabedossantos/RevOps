# RevOps Control Center

A modern, responsive analytics dashboard for revenue operations teams. Visualize marketing, pipeline, and revenue data with interactive filters, beautiful charts, and actionable insights—all powered by local CSVs and Python.

---

## Architecture Overview

![Architecture Diagram](revops_architecture.png)

- **Streamlit UI**: `streamlit_app/app.py` — main dashboard, filters, and theming
- **Analytics Layer**: `src/revops/analytics/` — KPI calculations and aggregations
- **Data Access**: `src/revops/data.py` — cached CSV loaders
- **Synthetic Data**: `src/revops/data_generation.py` — CLI to generate demo datasets
- **Validation**: `src/revops/validation.py` — schema checks for all data
- **Tests**: `tests/` — pytest suite for analytics and validation

---

## Quick Start: Run in 5 Minutes

1. **Clone and enter the repo**
   ```bash
   git clone <your-fork-url> revops-dashboard
   cd revops-dashboard
   ```
2. **Create a virtual environment and install dependencies**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -e '.[dev]'
   ```
3. **(Optional) Regenerate demo data**
   ```bash
   python -m revops.data_generation --output .
   ```
4. **Launch the dashboard**
   ```bash
   streamlit run streamlit_app/app.py
   ```
5. **Open your browser**
   - Go to [http://localhost:8501](http://localhost:8501)
   - Explore tabs for Marketing, Pipeline, Revenue, and Insights

---

## Seed Data

- `marketing_channels.csv` — marketing funnel events
- `pipeline_deals.csv` — sales pipeline deals
- `revenue_customers.csv` — customer revenue and churn
- `benchmarks.csv` — industry targets for KPIs

Regenerate all with:
```bash
python -m revops.data_generation --output .
```

---

## Project Structure

```
streamlit_app/         # UI, theming, entrypoint
src/revops/            # Analytics, data, validation, generation
  analytics/           # KPI logic
  ai/                  # Insights engine
  data.py              # CSV loaders
  data_generation.py   # Synthetic data CLI
  validation.py        # Schema checks
  config.py            # Data paths
benchmarks.csv         # Seed data
marketing_channels.csv # Seed data
pipeline_deals.csv     # Seed data
revenue_customers.csv  # Seed data
tests/                 # Pytest suite
README.md              # This file
```

---

## Setup Scripts

- **Install**: `pip install -e '.[dev]'`
- **Generate data**: `python -m revops.data_generation --output .`
- **Run tests**: `pytest`
- **Start dashboard**: `streamlit run streamlit_app/app.py`

---

## Documentation

- `docs/developer-guide.md` — technical deep dive
- `docs/business-user-guide.md` — user-facing walkthrough

---

## License

MIT (see `LICENSE`)
