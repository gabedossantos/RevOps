from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent / "src"))

from revops.data_generation import generate_marketing_data


if __name__ == "__main__":
    marketing_df = generate_marketing_data()
    print("Marketing Channels Data Sample:")
    print(marketing_df.head())
    print(f"\nTotal records: {len(marketing_df)}")
    print("\nSummary statistics:")
    print(marketing_df[["spend", "leads", "opportunities", "closed_won", "CAC", "ROI"]].describe())