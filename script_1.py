from pathlib import Path

import pandas as pd

import sys

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from revops.data_generation import generate_pipeline_data


if __name__ == "__main__":
    pipeline_df = generate_pipeline_data()
    print("Pipeline Deals Data Sample:")
    print(pipeline_df.head())
    print(f"\nTotal records: {len(pipeline_df)}")
    print("\nStage distribution:")
    print(pipeline_df["stage"].value_counts())
    print("\nSegment distribution:")
    print(pipeline_df["segment"].value_counts())
    print("\nAmount statistics by segment:")
    print(pipeline_df.groupby("segment")["amount"].describe())