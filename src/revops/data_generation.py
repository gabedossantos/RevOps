from __future__ import annotations

import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import numpy as np
import pandas as pd

RNG_SEED = 42


def _seed_everything(seed: int = RNG_SEED) -> None:
    np.random.seed(seed)
    random.seed(seed)


def generate_marketing_data(days: int = 365, top_channels: int = 4) -> pd.DataFrame:
    _seed_everything()

    channels = [
        "Google Ads",
        "Facebook Ads",
        "LinkedIn",
        "Content Marketing",
        "Email Marketing",
        "Organic Search",
        "Referral",
    ]
    campaigns = [
        "Q1 Brand",
        "Q2 Demo",
        "Q3 Feature",
        "Q4 Holiday",
        "Webinar Series",
        "Product Launch",
    ]
    segments = ["SMB", "MM", "ENT"]
    geos = ["US", "EU", "APAC", "Canada"]

    data = []
    start_date = datetime(2024, 1, 1)

    for day_offset in range(days):
        date = start_date + timedelta(days=day_offset)
        for channel in channels[:top_channels]:
            for segment in segments:
                if channel == "Google Ads":
                    spend = np.random.normal(5000, 1500)
                elif channel == "Facebook Ads":
                    spend = np.random.normal(3000, 1000)
                elif channel == "LinkedIn":
                    spend = (
                        np.random.normal(2000, 500)
                        if segment == "ENT"
                        else np.random.normal(500, 200)
                    )
                else:
                    spend = np.random.normal(1000, 300)

                spend = max(0, spend)

                cpm_multipliers = {
                    "Google Ads": 15,
                    "Facebook Ads": 8,
                    "LinkedIn": 25,
                    "Content Marketing": 5,
                }
                impressions = (spend * 1000) / cpm_multipliers.get(channel, 10)

                ctr_base = {
                    "Google Ads": 0.035,
                    "Facebook Ads": 0.02,
                    "LinkedIn": 0.045,
                    "Content Marketing": 0.015,
                }
                ctr = ctr_base.get(channel, 0.02) * np.random.normal(1, 0.2)
                ctr = max(0.005, ctr)
                clicks = impressions * ctr

                lead_cvr = {"SMB": 0.12, "MM": 0.08, "ENT": 0.05}
                leads = clicks * lead_cvr[segment] * np.random.normal(1, 0.3)
                mqls = leads * np.random.uniform(0.6, 0.8)
                sqls = mqls * np.random.uniform(0.2, 0.4)
                opportunities = sqls * np.random.uniform(0.7, 0.9)

                close_rates = {"SMB": 0.25, "MM": 0.20, "ENT": 0.15}
                closed_won = opportunities * close_rates[segment] * np.random.normal(1, 0.2)

                cac = spend / max(1, closed_won) if closed_won > 0 else spend
                cpl = spend / max(1, leads) if leads > 0 else 0
                roi = (
                    (
                        closed_won
                        * {"SMB": 25000, "MM": 75000, "ENT": 200000}[segment]
                        - spend
                    )
                    / spend
                    if spend > 0
                    else 0
                )

                data.append(
                    {
                        "date": date.strftime("%Y-%m-%d"),
                        "channel": channel,
                        "campaign": random.choice(campaigns),
                        "segment": segment,
                        "geo": random.choice(geos),
                        "spend": round(spend, 2),
                        "impressions": int(impressions),
                        "clicks": int(clicks),
                        "leads": int(leads),
                        "MQLs": int(mqls),
                        "SQLs": int(sqls),
                        "opportunities": int(opportunities),
                        "closed_won": int(closed_won),
                        "CAC": round(cac, 2),
                        "CPL": round(cpl, 2),
                        "CTR": round(clicks / impressions if impressions > 0 else 0, 4),
                        "CVR_stagewise": round(leads / clicks if clicks > 0 else 0, 4),
                        "ROI": round(roi * 100, 2),
                    }
                )

    return pd.DataFrame(data)


def generate_pipeline_data(num_deals: int = 2000) -> pd.DataFrame:
    _seed_everything()

    stages = ["Discovery", "Demo", "Negotiation", "Closed_Won", "Closed_Lost"]
    segments = ["SMB", "MM", "ENT"]
    owners = [
        "Alice Johnson",
        "Bob Smith",
        "Carol Davis",
        "David Wilson",
        "Eva Brown",
        "Frank Miller",
    ]
    channels = [
        "Google Ads",
        "Facebook Ads",
        "LinkedIn",
        "Content Marketing",
        "Referral",
        "Inbound",
    ]

    data = []

    for i in range(num_deals):
        segment = random.choice(segments)
        stage = random.choice(stages)

        if segment == "SMB":
            amount = np.random.lognormal(np.log(25000), 0.5)
        elif segment == "MM":
            amount = np.random.lognormal(np.log(75000), 0.6)
        else:
            amount = np.random.lognormal(np.log(200000), 0.7)

        amount = max(5000, amount)
        created_at = datetime.now() - timedelta(days=random.randint(0, 540))

        if stage == "Closed_Won":
            expected_close = created_at + timedelta(days=random.randint(30, 180))
        elif stage == "Closed_Lost":
            expected_close = created_at + timedelta(days=random.randint(20, 120))
        else:
            expected_close = created_at + timedelta(days=random.randint(60, 300))

        probabilities = {
            "Discovery": 0.25,
            "Demo": 0.45,
            "Negotiation": 0.75,
            "Closed_Won": 1.0,
            "Closed_Lost": 0.0,
        }

        probability = probabilities[stage] * np.random.normal(1, 0.1)
        probability = max(0, min(1, probability))

        last_stage_change = created_at + timedelta(days=random.randint(0, 60))
        days_in_stage = max(0, (datetime.now() - last_stage_change).days)
        expected_value = amount * probability

        data.append(
            {
                "deal_id": f"DEAL_{i + 1:04d}",
                "account": f"Account_{random.randint(1, 500):03d}",
                "segment": segment,
                "owner": random.choice(owners),
                "stage": stage,
                "amount": round(amount, 2),
                "created_at": created_at.strftime("%Y-%m-%d"),
                "expected_close": expected_close.strftime("%Y-%m-%d"),
                "last_stage_change": last_stage_change.strftime("%Y-%m-%d"),
                "days_in_stage": days_in_stage,
                "probability": round(probability, 3),
                "expected_value": round(expected_value, 2),
                "status": "Open" if stage not in ["Closed_Won", "Closed_Lost"] else stage,
                "source_channel": random.choice(channels),
            }
        )

    return pd.DataFrame(data)


def generate_revenue_data(num_customers: int = 1500) -> pd.DataFrame:
    _seed_everything()

    segments = ["SMB", "MM", "ENT"]
    plans = {
        "SMB": ["Starter", "Professional", "Business"],
        "MM": ["Professional", "Business", "Enterprise"],
        "ENT": ["Business", "Enterprise", "Custom"],
    }
    churn_reasons = [
        "Price",
        "Competition",
        "Feature Gap",
        "Support",
        "Business Closure",
        "Merger",
        "Budget Cut",
    ]

    data = []

    for i in range(num_customers):
        customer_id = f"CUST_{i + 1:04d}"
        account = f"Account_{i + 1:03d}"
        segment = random.choice(segments)
        plan = random.choice(plans[segment])
        start_date = datetime.now() - timedelta(days=random.randint(0, 1095))

        base_mrr_ranges = {
            "SMB": {"Starter": (500, 1500), "Professional": (1500, 3000), "Business": (3000, 8000)},
            "MM": {"Professional": (3000, 8000), "Business": (8000, 20000), "Enterprise": (20000, 50000)},
            "ENT": {"Business": (15000, 40000), "Enterprise": (40000, 100000), "Custom": (100000, 500000)},
        }

        mrr_range = base_mrr_ranges[segment][plan]
        starting_mrr = np.random.uniform(*mrr_range)

        monthly_churn_rates = {"SMB": 0.05, "MM": 0.03, "ENT": 0.02}
        months_since_start = max(1, (datetime.now() - start_date).days / 30.44)
        churn_probability = 1 - (1 - monthly_churn_rates[segment]) ** months_since_start

        churned_flag = random.random() < churn_probability

        if churned_flag:
            days_since_start = max(30, (datetime.now() - start_date).days)
            churn_days = random.randint(30, days_since_start)
            churn_date = start_date + timedelta(days=churn_days)
            churn_reason = random.choice(churn_reasons)
        else:
            churn_date = None
            churn_reason = None

        if not churned_flag:
            new_mrr = starting_mrr if (datetime.now() - start_date).days <= 30 else 0

            expansion_probability = min(0.2, months_since_start * 0.2 / 12)
            expansion_mrr = (
                starting_mrr * 0.3 * random.random()
                if random.random() < expansion_probability
                else 0
            )

            contraction_probability = min(0.1, months_since_start * 0.1 / 12)
            contraction_mrr = (
                starting_mrr * 0.2 * random.random()
                if random.random() < contraction_probability
                else 0
            )

            current_mrr = starting_mrr + expansion_mrr - contraction_mrr
        else:
            new_mrr = 0
            expansion_mrr = 0
            contraction_mrr = 0
            current_mrr = 0

        arpa = current_mrr

        if not churned_flag and current_mrr > 0:
            base_mrr = max(1.0, current_mrr - expansion_mrr + contraction_mrr)
            nrr = current_mrr / base_mrr
        else:
            nrr = 0.0

        data.append(
            {
                "customer_id": customer_id,
                "account": account,
                "segment": segment,
                "plan": plan,
                "start_date": start_date.strftime("%Y-%m-%d"),
                "mrr": round(current_mrr, 2),
                "new_mrr": round(new_mrr, 2),
                "expansion_mrr": round(expansion_mrr, 2),
                "contraction_mrr": round(contraction_mrr, 2),
                "churned_flag": churned_flag,
                "churn_date": churn_date.strftime("%Y-%m-%d") if churn_date else None,
                "churn_reason": churn_reason,
                "arpa": round(arpa, 2),
                "nrr": round(nrr, 3),
            }
        )

    return pd.DataFrame(data)


def generate_benchmarks_data() -> pd.DataFrame:
    _seed_everything()

    channel_cpl_data = [
        {"metric": "channel_cpl_range", "channel": "Google Ads", "segment": "SMB", "min_value": 15, "max_value": 50, "target_value": 25},
        {"metric": "channel_cpl_range", "channel": "Google Ads", "segment": "MM", "min_value": 25, "max_value": 80, "target_value": 45},
        {"metric": "channel_cpl_range", "channel": "Google Ads", "segment": "ENT", "min_value": 50, "max_value": 200, "target_value": 100},
        {"metric": "channel_cpl_range", "channel": "Facebook Ads", "segment": "SMB", "min_value": 10, "max_value": 35, "target_value": 20},
        {"metric": "channel_cpl_range", "channel": "Facebook Ads", "segment": "MM", "min_value": 20, "max_value": 60, "target_value": 35},
        {"metric": "channel_cpl_range", "channel": "LinkedIn", "segment": "ENT", "min_value": 75, "max_value": 300, "target_value": 150},
    ]

    stage_conversion_data = [
        {"metric": "stage_conversion_benchmarks", "stage_from": "Lead", "stage_to": "MQL", "segment": "SMB", "target_value": 0.65},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Lead", "stage_to": "MQL", "segment": "MM", "target_value": 0.60},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Lead", "stage_to": "MQL", "segment": "ENT", "target_value": 0.55},
        {"metric": "stage_conversion_benchmarks", "stage_from": "MQL", "stage_to": "SQL", "segment": "SMB", "target_value": 0.30},
        {"metric": "stage_conversion_benchmarks", "stage_from": "MQL", "stage_to": "SQL", "segment": "MM", "target_value": 0.25},
        {"metric": "stage_conversion_benchmarks", "stage_from": "MQL", "stage_to": "SQL", "segment": "ENT", "target_value": 0.20},
        {"metric": "stage_conversion_benchmarks", "stage_from": "SQL", "stage_to": "Opportunity", "segment": "SMB", "target_value": 0.80},
        {"metric": "stage_conversion_benchmarks", "stage_from": "SQL", "stage_to": "Opportunity", "segment": "MM", "target_value": 0.75},
        {"metric": "stage_conversion_benchmarks", "stage_from": "SQL", "stage_to": "Opportunity", "segment": "ENT", "target_value": 0.70},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Discovery", "stage_to": "Demo", "segment": "SMB", "target_value": 0.60},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Discovery", "stage_to": "Demo", "segment": "MM", "target_value": 0.55},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Discovery", "stage_to": "Demo", "segment": "ENT", "target_value": 0.50},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Demo", "stage_to": "Negotiation", "segment": "SMB", "target_value": 0.45},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Demo", "stage_to": "Negotiation", "segment": "MM", "target_value": 0.40},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Demo", "stage_to": "Negotiation", "segment": "ENT", "target_value": 0.35},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Negotiation", "stage_to": "Closed_Won", "segment": "SMB", "target_value": 0.65},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Negotiation", "stage_to": "Closed_Won", "segment": "MM", "target_value": 0.60},
        {"metric": "stage_conversion_benchmarks", "stage_from": "Negotiation", "stage_to": "Closed_Won", "segment": "ENT", "target_value": 0.55},
    ]

    sales_cycle_data = [
        {"metric": "sales_cycle_by_segment", "segment": "SMB", "target_value": 60, "min_value": 30, "max_value": 90},
        {"metric": "sales_cycle_by_segment", "segment": "MM", "target_value": 120, "min_value": 90, "max_value": 180},
        {"metric": "sales_cycle_by_segment", "segment": "ENT", "target_value": 240, "min_value": 180, "max_value": 360},
    ]

    nrr_targets_data = [
        {"metric": "nrr_targets", "segment": "SMB", "target_value": 1.05, "min_value": 0.95, "max_value": 1.15},
        {"metric": "nrr_targets", "segment": "MM", "target_value": 1.08, "min_value": 1.00, "max_value": 1.20},
        {"metric": "nrr_targets", "segment": "ENT", "target_value": 1.12, "min_value": 1.05, "max_value": 1.25},
    ]

    ltv_cac_data = [
        {"metric": "ltv_cac_targets", "segment": "SMB", "target_value": 3.0, "min_value": 2.5, "max_value": 5.0},
        {"metric": "ltv_cac_targets", "segment": "MM", "target_value": 4.0, "min_value": 3.0, "max_value": 6.0},
        {"metric": "ltv_cac_targets", "segment": "ENT", "target_value": 5.0, "min_value": 3.5, "max_value": 8.0},
    ]

    win_rate_data = [
        {"metric": "win_rate_targets", "segment": "SMB", "target_value": 0.25, "min_value": 0.20, "max_value": 0.35},
        {"metric": "win_rate_targets", "segment": "MM", "target_value": 0.20, "min_value": 0.15, "max_value": 0.30},
        {"metric": "win_rate_targets", "segment": "ENT", "target_value": 0.15, "min_value": 0.10, "max_value": 0.25},
    ]

    cac_payback_data = [
        {"metric": "cac_payback_targets", "segment": "SMB", "target_value": 12, "min_value": 6, "max_value": 18},
        {"metric": "cac_payback_targets", "segment": "MM", "target_value": 18, "min_value": 12, "max_value": 24},
        {"metric": "cac_payback_targets", "segment": "ENT", "target_value": 24, "min_value": 18, "max_value": 36},
    ]

    all_benchmarks = []
    for dataset in [
        channel_cpl_data,
        stage_conversion_data,
        sales_cycle_data,
        nrr_targets_data,
        ltv_cac_data,
        win_rate_data,
        cac_payback_data,
    ]:
        all_benchmarks.extend(dataset)

    records = []
    for idx, benchmark in enumerate(all_benchmarks):
        records.append(
            {
                "benchmark_id": f"BENCH_{idx + 1:03d}",
                "metric_type": benchmark["metric"],
                "category": benchmark.get("channel", benchmark.get("segment", benchmark.get("stage_from", "General"))),
                "subcategory": benchmark.get("segment", benchmark.get("stage_to", "All")),
                "target_value": benchmark["target_value"],
                "min_value": benchmark.get("min_value", benchmark["target_value"] * 0.8),
                "max_value": benchmark.get("max_value", benchmark["target_value"] * 1.2),
                "unit": (
                    "percentage"
                    if benchmark["target_value"] <= 1 and "ltv_cac" not in benchmark["metric"]
                    else "currency"
                    if "cpl" in benchmark["metric"].lower()
                    else "ratio"
                    if "ltv_cac" in benchmark["metric"]
                    else "days"
                    if "cycle" in benchmark["metric"] or "payback" in benchmark["metric"]
                    else "number"
                ),
                "description": (
                    f"{benchmark['metric'].replace('_', ' ').title()} benchmark for "
                    f"{benchmark.get('segment', benchmark.get('channel', 'all segments'))}"
                ),
            }
        )

    return pd.DataFrame(records)


def generate_all_datasets(output_dir: Path) -> Tuple[Path, Path, Path, Path]:
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    marketing = generate_marketing_data()
    pipeline = generate_pipeline_data()
    revenue = generate_revenue_data()
    benchmarks = generate_benchmarks_data()

    marketing_path = output_dir / "marketing_channels.csv"
    pipeline_path = output_dir / "pipeline_deals.csv"
    revenue_path = output_dir / "revenue_customers.csv"
    benchmarks_path = output_dir / "benchmarks.csv"

    marketing.to_csv(marketing_path, index=False)
    pipeline.to_csv(pipeline_path, index=False)
    revenue.to_csv(revenue_path, index=False)
    benchmarks.to_csv(benchmarks_path, index=False)

    return marketing_path, pipeline_path, revenue_path, benchmarks_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate RevOps synthetic datasets.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path.cwd(),
        help="Directory where CSVs should be written",
    )
    args = parser.parse_args()

    marketing_path, pipeline_path, revenue_path, benchmarks_path = generate_all_datasets(args.output)

    print("Datasets generated:")
    print(f"✅ {marketing_path}")
    print(f"✅ {pipeline_path}")
    print(f"✅ {revenue_path}")
    print(f"✅ {benchmarks_path}")


if __name__ == "__main__":
    main()
