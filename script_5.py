from pathlib import Path

import pandas as pd

import sys

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from revops.data_generation import generate_all_datasets
from revops.data import get_marketing_df, get_pipeline_df, get_revenue_df, get_benchmarks_df


if __name__ == "__main__":
	output_dir = Path(__file__).resolve().parent
	generate_all_datasets(output_dir)

	marketing_df = get_marketing_df()
	pipeline_df = get_pipeline_df()
	revenue_df = get_revenue_df()
	benchmarks_df = get_benchmarks_df()

	print("Dataset files saved:")
	print("✅ marketing_channels.csv")
	print("✅ pipeline_deals.csv")
	print("✅ revenue_customers.csv")
	print("✅ benchmarks.csv")

	print("\n" + "=" * 50)
	print("KEY METRICS SUMMARY")
	print("=" * 50)

	total_spend = marketing_df["spend"].sum()
	total_leads = marketing_df["leads"].sum()
	total_closed_won = marketing_df["closed_won"].sum()
	avg_cac = marketing_df["CAC"].mean()
	avg_roi = marketing_df["ROI"].mean()

	print(f"\n📊 MARKETING METRICS:")
	print(f"   Total Spend: ${total_spend:,.2f}")
	print(f"   Total Leads: {total_leads:,}")
	print(f"   Total Closed Won: {total_closed_won:,}")
	print(f"   Average CAC: ${avg_cac:.2f}")
	print(f"   Average ROI: {avg_roi:.1f}%")

	open_deals = pipeline_df[pipeline_df["status"] == "Open"]
	total_pipeline = open_deals["amount"].sum()
	weighted_pipeline = open_deals["expected_value"].sum()
	avg_deal_size = pipeline_df["amount"].mean()
	win_rate = len(pipeline_df[pipeline_df["stage"] == "Closed_Won"]) / len(
		pipeline_df[pipeline_df["stage"].isin(["Closed_Won", "Closed_Lost"])]
	)

	print(f"\n💼 PIPELINE METRICS:")
	print(f"   Total Pipeline: ${total_pipeline:,.2f}")
	print(f"   Weighted Pipeline: ${weighted_pipeline:,.2f}")
	print(f"   Average Deal Size: ${avg_deal_size:,.2f}")
	print(f"   Overall Win Rate: {win_rate:.1%}")

	active_customers = revenue_df[~revenue_df["churned_flag"]]
	total_mrr = active_customers["mrr"].sum()
	total_arr = total_mrr * 12
	avg_nrr = active_customers["nrr"].mean()
	churn_rate = revenue_df["churned_flag"].mean()

	print(f"\n💰 REVENUE METRICS:")
	print(f"   Total MRR: ${total_mrr:,.2f}")
	print(f"   Total ARR: ${total_arr:,.2f}")
	print(f"   Average NRR: {avg_nrr:.3f}")
	print(f"   Churn Rate: {churn_rate:.1%}")

	print("\n" + "=" * 50)
	print("DATASET STATISTICS")
	print("=" * 50)
	print(f"Marketing Records: {len(marketing_df):,} (covering {len(marketing_df['date'].unique())} days)")
	print(f"Pipeline Records: {len(pipeline_df):,} deals")
	print(f"Revenue Records: {len(revenue_df):,} customers")
	print(f"Benchmark Records: {len(benchmarks_df):,} benchmarks")