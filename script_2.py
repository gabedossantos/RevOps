from pathlib import Path

import pandas as pd

import sys

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from revops.data_generation import generate_revenue_data


if __name__ == "__main__":
    revenue_df = generate_revenue_data()
    print("Revenue Customers Data Sample:")
    print(revenue_df.head())
    print(f"\nTotal records: {len(revenue_df)}")
    print("\nChurn analysis:")
    print(f"Churned customers: {revenue_df['churned_flag'].sum()}")
    print(f"Active customers: {(~revenue_df['churned_flag']).sum()}")
    print(f"Overall churn rate: {revenue_df['churned_flag'].mean():.2%}")
    print("\nChurn by segment:")
    print(revenue_df.groupby('segment')['churned_flag'].agg(['count', 'sum', 'mean']))
    print("\nMRR statistics by segment:")
    active_customers = revenue_df[~revenue_df['churned_flag']]
    print(active_customers.groupby('segment')['mrr'].describe())