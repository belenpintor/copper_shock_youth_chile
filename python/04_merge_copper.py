"""
04_merge_copper.py

Merge world copper prices into the panel to construct the instrument:
    Shock_it = HighExposure_i x CopperPrice_t

Usage
-----
    python python/04_merge_copper.py

Inputs
------
    data/processed/panel_with_ine.csv
    data/raw/copper_prices.csv

Outputs
-------
    data/processed/panel_with_copper.csv
"""

import os

import pandas as pd

PROCESSED_DIR = os.path.join("data", "processed")
INPUT_PATH = os.path.join(PROCESSED_DIR, "panel_with_ine.csv")
COPPER_PATH = os.path.join("data", "raw", "copper_prices.csv")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "panel_with_copper.csv")


def load_annual_copper_prices(path):
    """Load monthly copper prices and collapse to annual averages."""
    prices = pd.read_csv(path, parse_dates=[0])
    prices.columns = ["date", "copper_price_usd_per_lb"]
    prices["year"] = prices["date"].dt.year
    annual = prices.groupby("year", as_index=False)["copper_price_usd_per_lb"].mean()
    return annual


def main():
    if not os.path.exists(INPUT_PATH):
        print(f"{INPUT_PATH} not found. Run 03_merge_ine.py first.")
        return
    if not os.path.exists(COPPER_PATH):
        print(f"{COPPER_PATH} not found. Run 01_download_data.py first.")
        return

    panel = pd.read_csv(INPUT_PATH)
    copper = load_annual_copper_prices(COPPER_PATH)

    panel["year"] = panel["year"].astype(int)
    merged = panel.merge(copper, on="year", how="left")

    # Construct instrument: interaction of baseline high exposure and
    # the (exogenous) world copper price.
    merged["shock"] = merged["high_exposure"] * merged["copper_price_usd_per_lb"]
    merged["post_2003"] = (merged["year"] >= 2003).astype(int)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    merged.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved panel with copper shock instrument to {OUTPUT_PATH} ({len(merged)} rows)")


if __name__ == "__main__":
    main()
