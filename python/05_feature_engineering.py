"""
05_feature_engineering.py

Build final treatment exposure variables, interactions, and youth
subsample used in the R econometric analysis.

Usage
-----
    python python/05_feature_engineering.py

Inputs
------
    data/processed/panel_with_copper.csv

Outputs
-------
    data/processed/panel_youth.csv   <- final analysis-ready panel
"""

import os

import pandas as pd

PROCESSED_DIR = os.path.join("data", "processed")
INPUT_PATH = os.path.join(PROCESSED_DIR, "panel_with_copper.csv")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "panel_youth.csv")

YOUTH_MIN_AGE = 15
YOUTH_MAX_AGE = 24


def restrict_to_youth(df):
    return df[(df["age"] >= YOUTH_MIN_AGE) & (df["age"] <= YOUTH_MAX_AGE)].copy()


def add_treatment_interactions(df):
    df = df.copy()
    df["high_exposure_x_post"] = df["high_exposure"] * df["post_2003"]
    df["low_skill"] = (df["education_years"] <= 8).astype(int)
    return df


def main():
    if not os.path.exists(INPUT_PATH):
        print(f"{INPUT_PATH} not found. Run 04_merge_copper.py first.")
        return

    panel = pd.read_csv(INPUT_PATH)
    youth = restrict_to_youth(panel)
    youth = add_treatment_interactions(youth)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    youth.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved final youth analysis panel to {OUTPUT_PATH} ({len(youth)} rows)")


if __name__ == "__main__":
    main()
