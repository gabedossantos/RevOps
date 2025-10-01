from pathlib import Path

import pandas as pd

import sys

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from revops.data_generation import generate_benchmarks_data


if __name__ == "__main__":
    benchmarks_df = generate_benchmarks_data()
    print("Benchmarks Data Sample:")
    print(benchmarks_df.head(10))
    print(f"\nTotal records: {len(benchmarks_df)}")
    print("\nMetric types:")
    print(benchmarks_df['metric_type'].value_counts())
    print("\nBenchmarks by unit:")
    print(benchmarks_df['unit'].value_counts())