"""
02_clean_casen.py

Standardize CASEN variables across survey waves (2003, 2006, 2009, 2011)
into a consistent schema for merging with labor force and copper price data.

Usage
-----
    python python/02_clean_casen.py

Inputs
------
    data/raw/casen/<year>/*.csv (or .sav/.dta, converted upstream)

Outputs
-------
    data/processed/casen_clean.csv

Key standardized variables
---------------------------
    year            survey wave
    region          region code (standardized across waves)
    comuna          comuna (municipality) code
    person_id       unique respondent identifier
    age             age in years
    female          indicator, 1 = female
    enrolled        indicator, 1 = currently enrolled in school/education
    in_labor_force  indicator, 1 = participating in the labor force
    employed        indicator, 1 = employed
    education_years years of completed education
    weight          survey sampling weight
"""

import glob
import os

import pandas as pd

RAW_CASEN_DIR = os.path.join("data", "raw", "casen")
PROCESSED_DIR = os.path.join("data", "processed")
OUTPUT_PATH = os.path.join(PROCESSED_DIR, "casen_clean.csv")

# Mapping of raw CASEN variable names to standardized names.
# Actual CASEN column names vary by wave; update this mapping once raw
# files are available.
VARIABLE_MAP = {
    "region": "region",
    "comuna": "comuna",
    "folio": "person_id",
    "edad": "age",
    "sexo": "female",
    "asiste": "enrolled",
    "activ": "in_labor_force",
    "ocupado": "employed",
    "esc": "education_years",
    "expr": "weight",
}


def load_casen_wave(path):
    df = pd.read_csv(path)
    df = df.rename(columns=VARIABLE_MAP)
    return df


def clean_wave(df, year):
    df = df.copy()
    df["year"] = year
    if "female" in df.columns:
        # Recode sex coded as 1=male, 2=female into a female indicator.
        df["female"] = (df["female"] == 2).astype(int)
    return df


def main():
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    wave_files = sorted(glob.glob(os.path.join(RAW_CASEN_DIR, "*", "*.csv")))

    if not wave_files:
        print(f"No CASEN files found under {RAW_CASEN_DIR}. "
              "Run 01_download_data.py and place raw files first.")
        return

    frames = []
    for path in wave_files:
        year = os.path.basename(os.path.dirname(path))
        df = load_casen_wave(path)
        df = clean_wave(df, year)
        frames.append(df)

    casen = pd.concat(frames, ignore_index=True)
    casen.to_csv(OUTPUT_PATH, index=False)
    print(f"Saved cleaned CASEN panel to {OUTPUT_PATH} ({len(casen)} rows)")


if __name__ == "__main__":
    main()
