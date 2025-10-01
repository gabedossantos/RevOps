# RevOps Workspace Architecture Plan

## Objectives
- Transform the existing CSV datasets and prototype scripts into a maintainable Python application.
- Deliver an interactive dashboard experience (Streamlit) that mirrors the Marketing, Pipeline, Revenue, and AI Co-Pilot views outlined in the specification.
- Provide reusable analytics modules and a lightweight rule-based insights engine to power both the UI and potential API clients.
- Set up automated tests and documentation so the workspace can evolve toward the full Next.js experience described in `revops-dashboard-spec.md`.

## High-Level Components
1. **Data Access Layer (`revops/data`):**
   - Helpers to read the canonical CSVs (marketing, pipeline, revenue, benchmarks).
   - Lazy loading with caching to avoid repeated disk reads.
   - Schema validation and typing via `pydantic` models to ensure data integrity.

2. **Analytics Layer (`revops/analytics`):**
   - `marketing.py`: KPI aggregations, channel breakdowns, trend calculations.
   - `pipeline.py`: Stage funnels, velocity metrics, stuck-deal detection.
   - `revenue.py`: MRR waterfalls, churn cohorts, NRR calculations.
   - Shared utilities for currency/percentage formatting and time-binning.

3. **Insights Engine (`revops/ai`):**
   - Deterministic rules that synthesize insights, recommendations, and alerts from analytics outputs.
   - Extensible interface ready for future enhancements.

4. **Presentation Layer (`streamlit_app/app.py`):**
   - Streamlit multipage layout with tabs for Marketing, Pipeline, Revenue, and AI Co-Pilot.
   - Interactive filters (date range, segment, channel, geography) with cross-view synchronization.
   - Visualizations built with Plotly/Altair and data tables leveraging the analytics layer.

5. **Automation & Tooling:**
   - `pyproject.toml` (or `requirements.txt`) capturing pandas, numpy, streamlit, plotly, pydantic, pytest.
   - CLI entry point (`revops/cli.py`) to regenerate CSVs using the original simulation logic.
   - Git-friendly data storage – large CSVs remain in the root `data/` folder, accessed by relative path.

6. **Quality Gates:**
   - Unit tests in `tests/` validating key metric computations and AI recommendations.
   - CI-friendly commands: `pytest`, `streamlit run streamlit_app/app.py`.
   - Optional smoke test script to ensure data loads without errors.

## Data Flow
```
CSV Files → Data Loader → Analytics Aggregations → Insights Engine → Streamlit UI / CLI
```

## Open Questions & Assumptions
- The initial implementation will target Streamlit for velocity; the Next.js scaffold remains a future enhancement.
- AI Co-Pilot responses rely on deterministic heuristics.
- CSV datasets in the repository are treated as the source of truth and regenerated on demand via the CLI.

## Next Steps
1. Scaffold the Python package and dependency manifest.
2. Port simulation scripts into reusable modules and expose a CLI surface.
3. Implement analytics functions with unit tests.
4. Build the Streamlit dashboard that consumes the analytics layer.
5. Document usage in `README.md` and run validation commands.
