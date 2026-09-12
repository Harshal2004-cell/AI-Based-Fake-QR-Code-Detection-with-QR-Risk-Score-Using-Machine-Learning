import pandas as pd
from utils.feature_extraction import extract_features

INPUT_FILE = "data/raw_data.csv"
OUTPUT_FILE = "data/qr_dataset.csv"


def prepare_dataset():
    print("======================================")
    print("      DATASET PREPARATION MODULE")
    print("======================================")

    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded raw inputs: {len(df)} rows from {INPUT_FILE}")

    feature_rows = []
    for _, row in df.iterrows():
        qr_data = row["data"]
        label = row["label"]

        features = extract_features(qr_data)
        features["Label"] = label
        feature_rows.append(features)

    feature_df = pd.DataFrame(feature_rows)
    feature_df.to_csv(OUTPUT_FILE, index=False)

    print("\nDataset generated successfully!")
    print(f"Output File: {OUTPUT_FILE}")
    print(f"Dataset Shape: {feature_df.shape}")
    print("\nClass Label Distribution:")
    print(feature_df["Label"].value_counts())
    print("======================================")


if __name__ == "__main__":
    prepare_dataset()