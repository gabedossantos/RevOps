# RevOps Control Center — Business User Guide

This guide explains how revenue, sales, and marketing leaders can use the RevOps Control Center dashboard to monitor performance, uncover trends, and collaborate across functions.

---

## Getting started

1. **Launch the app**
   - Preferred: open the deployed Streamlit link provided by your RevOps team.
   - Local/demo: run `streamlit run streamlit_app/app.py` (RevOps engineering can help if needed).
2. **Choose a visual theme**
   - Open the left sidebar and use the **Visual theme** selector to toggle between:
     - **Midnight Aurora** – high-contrast dark mode (default)
     - **Luma Skyline** – light mode optimized for bright rooms
     - **Neon Pulse (Legacy)** – original neon design preserved for familiarity
3. **Review the hero summary**
   - The hero card confirms the active theme, highlights that data is synthetic (demo) and updated daily, and sets the context for the session.

---

## Shared controls

- **Date range** — trims the analysis window across every dashboard tab.
- **Segments** — filter by customer segment (SMB, Mid-Market, Enterprise).
- **Channels** — narrow to specific marketing acquisition sources.
- **Regions** — focus on geographic performance.

All filters update simultaneously. Adjusting them in the sidebar immediately recalculates KPIs, charts, tables, and AI insights.

---

## Dashboard tabs

### 1. Marketing

Focus: demand generation effectiveness.

- **KPI cards** — total spend, leads, MQLs, SQLs, average CAC, and average ROI.
- **Channel Spend vs ROI chart** — highlights the most efficient channels by coloring bars with ROI percentage.
- **Funnel Breakdown** — visualizes conversion leakage at each stage of the marketing funnel.
- **Weekly Performance Trends** — stacked area chart for leads, MQLs, and SQLs to spot inflection points.
- **Channel table** — sortable details on spend, funnel counts, conversion rate, CAC, and ROI.

**How to use it**
- Identify which campaigns deserve more or less budget.
- Spot segments or regions with conversion bottlenecks.
- Track the impact of recent campaigns by comparing week-over-week trends.

### 2. Pipeline

Focus: sales execution and coverage.

- **KPI cards** — total pipeline, weighted pipeline, average deal size, win rate, and velocity (expected value per day).
- **Stage Distribution** — displays where money is concentrated across the funnel stages.
- **Rep Performance** — compares total closed amount and win rate per owner.
- **Stuck Deals** — list of open deals over 45 days and $50K, enabling fast triage.

**How to use it**
- Validate whether pipeline volume supports upcoming targets.
- Use stage distribution to spot bottlenecks (e.g., too many deals stuck in Negotiation).
- Coach reps by comparing their win rates and cycle times.

### 3. Revenue

Focus: retention, expansion, and recurring revenue health.

- **KPI cards** — total MRR, total ARR, average net revenue retention (NRR), and churn rate.
- **MRR by Segment treemap** — shows which segments generate the most recurring revenue and expansion.
- **MRR Waterfall** — decomposes ending MRR into starting value, new, expansion, contraction, and churn components.
- **Churn Reasons table** — ranks quitting drivers by segment and count.

**How to use it**
- Measure overall recurring revenue momentum.
- Pinpoint segments driving expansion or suffering contraction.
- Coordinate with Customer Success on top churn reasons and remediation actions.

### 4. AI Co-Pilot

Focus: automated commentary and callouts.

- Curated insight cards grouped by **Marketing**, **Pipeline**, or **Revenue**.
- Each card includes a confidence bar and optional supporting data points.

**How to use it**
- Skim the insights for quick context before deep dives or leadership updates.
- Prioritize follow-ups based on high-confidence alerts (e.g., stuck deals volume, rising churn).
- Use data point snippets (channel, deal IDs, churn reason) to open follow-on conversations with the right team.

---

## Key metric definitions

| Metric | Meaning | Formula (simplified) |
| --- | --- | --- |
| **CAC** | Average cost to acquire a new customer | Total spend ÷ closed-won deals |
| **ROI** | Return on marketing investment | ((Revenue − Spend) ÷ Spend) × 100 |
| **Weighted Pipeline** | Pipeline value adjusted by win probability | Σ(Deal amount × Probability) |
| **Win Rate** | Closed-won deals ÷ (Closed-won + Closed-lost) |
| **Velocity** | Expected value generated per day | Weighted pipeline ÷ Average days in stage |
| **MRR** | Monthly recurring revenue from active customers | Σ active subscription values |
| **ARR** | Annual recurring revenue | MRR × 12 |
| **NRR** | Retention including expansion/contraction | (Starting MRR + Expansion − Contraction) ÷ Starting MRR |
| **Churn Rate** | Share of accounts that churned | Churned accounts ÷ Total accounts |

Note: Values are derived from synthetic demo data preloaded in the repository. For production, connect to live sources via your data team.

---

## Best-practice workflows

### Weekly marketing review

1. Set date range to the last 7–28 days.
2. Filter to the segment or region relevant for the upcoming campaign.
3. Scan KPI cards for CAC/ROI movement.
4. Review the Channel Spend vs ROI chart to reallocate budget.
5. Read AI marketing insights to capture quick wins and risks.

### Pipeline inspection before forecast call

1. Filter to the current fiscal quarter.
2. Enable segments that map to your forecast boards.
3. Verify weighted pipeline covers quota multiples.
4. Sort Stuck Deals by days in stage and assign owners for follow-up.
5. Capture AI pipeline insights for meeting talking points.

### Monthly retention debrief

1. Adjust the date range to the previous month.
2. Compare segment treemap vs. MRR waterfall for expansion/contraction mix.
3. Consult Churn Reasons and share top drivers with Customer Success.
4. Pair AI revenue insights with actionable initiatives (save segments, expansion plays).

---

## Theming & presentation tips

- Switch to **Luma Skyline** when presenting in brightly lit rooms or on projectors.
- Use **Midnight Aurora** for storytelling dashboards or when screen sharing in dark mode.
- Theme changes are session-specific; take note of preferred style before exec reviews.

---

## Data freshness & limitations

- The repository ships with synthetic data refreshed daily in development environments.
- Ask RevOps engineering before relying on the demo dataset for official reporting.
- For production adoption, plan a data pipeline that updates the CSV inputs (or integrates the app with your warehouse).

---

## Next steps for your team

- Share the AI insights with marketing, sales, and success leads ahead of planning meetings.
- Align on benchmark targets (stored in `benchmarks.csv`) to compare against KPI outputs.
- Provide feedback to RevOps engineering on additional views, filters, or narratives you need.

---

## Help & support

- **Technical issues**: contact RevOps engineering or file an issue in the repository.
- **Data questions**: reach out to the analytics team owning the underlying CSV refresh.
- **Feature requests**: log them in your team’s backlog or collaborate on the roadmap outlined in `docs/architecture-plan.md`.

Together, these steps help marketing, sales, finance, and success leaders align around a shared source of revenue truth.
