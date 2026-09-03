"""
03_merge_ine.py

Merge INE ENE (Encuesta Nacional de Empleo) regional labor market data
into the cleaned CASEN panel, adding regional mining employment share
used to construct treatment exposure.

Usage
-----
    python python/03_merge_ine.py

Inputs
------
    data/processed/casen_clean.csv
    data/raw/ine_ene/*.csv

Outputs
-------
    data/processed/panel_with_ine.csv
"""

import glob
import os

import pandas as pd

PROCESSED_DIR = os.path.join("data", "processed")
CASEN_CLEAN_PATH = os.path.join(PROCESSED_DIR, "casen_clean.csv")
RAW_INE_DIR = os.path.join("data", "raw", "ine_ene")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "panel_with_ine.csv")

# High-exposure (mining-intensive) regions, per pre-shock mining
# employment share. See README for region codes.
HIGH_EXPOSURE_REGIONS = ["Antofagasta", "Tarapaca", "Coquimbo", "Atacama"]


def load_ine_data():
    files = sorted(glob.glob(os.path.join(RAW_INE_DIR, "*", "*.csv")))
    if not files:
        return None
    frames = [pd.read_csv(f) for f in files]
    return pd.concat(frames, ignore_index=True)


def build_region_mining_share(ine_df):
    """Compute regional share of labor force employed in mining."""
    mining = ine_df[ine_df["sector"] == "mining"]
    total = ine_df.groupby(["region", "year"])["employed"].sum().rename("total_employed")
    mining_employed = mining.groupby(["region", "year"])["employed"].sum().rename("mining_employed")
    shares = pd.concat([total, mining_employed], axis=1).fillna(0)
    shares["mining_share"] = shares["mining_employed"] / shares["total_employed"]
    return shares.reset_index()[["region", "year", "mining_share"]]


def main():
    if not os.path.exists(CASEN_CLEAN_PATH):
        print(f"{CASEN_CLEAN_PATH} not found. Run 02_clean_casen.py first.")
        return

    casen = pd.read_csv(CASEN_CLEAN_PATH)
    ine = load_ine_data()

    if ine is None:
        print(f"No INE ENE files found under {RAW_INE_DIR}. "
              "Adding high_exposure flag from static region list only.")
        merged = casen.copy()
    else:
        mining_share = build_region_mining_share(ine)
        merged = casen.merge(mining_share, on=["region", "year"], how="left")

    merged["high_exposure"] = merged["region"].isin(HIGH_EXPOSURE_REGIONS).astype(int)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    merged.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved merged panel to {OUTPUT_PATH} ({len(merged)} rows)")


if __name__ == "__main__":
    main()
