"""
01_download_data.py

Fetch raw data sources for the copper shock / youth outcomes project:
    - CASEN (Chilean Socio-Economic Characterization Survey), 2003-2011
    - INE National Labor Force Survey (ENE), 2003-2011
    - Copper prices (FRED / LME), 2003-2011

Usage
-----
    python python/01_download_data.py

Notes
-----
CASEN and ENE microdata typically require manual download from the
official portals (registration / terms of use). This script documents
the expected raw file locations and downloads what can be fetched
programmatically (e.g., copper prices from FRED).

Outputs
-------
    data/raw/casen/           CASEN microdata by wave (2003, 2006, 2009, 2011)
    data/raw/ine_ene/         INE ENE quarterly labor force microdata
    data/raw/copper_prices.csv  Copper price series (monthly)
"""

import os

RAW_DIR = os.path.join("data", "raw")
CASEN_DIR = os.path.join(RAW_DIR, "casen")
ENE_DIR = os.path.join(RAW_DIR, "ine_ene")

CASEN_URL = "http://observatorio.ministeriodesarrollosocial.gob.cl/encuesta-casen"
INE_ENE_URL = "https://www.ine.gob.cl/estadisticas/sociales/mercado-laboral/ocupacion-y-desocupacion"
FRED_COPPER_SERIES = "PCOPPUSDM"  # Global price of copper, FRED series ID


def ensure_dirs():
    os.makedirs(CASEN_DIR, exist_ok=True)
    os.makedirs(ENE_DIR, exist_ok=True)


def download_copper_prices(output_path=os.path.join(RAW_DIR, "copper_prices.csv")):
    """Download monthly copper price series from FRED.

    Requires a FRED API key set as the FRED_API_KEY environment variable.
    See https://fred.stlouisfed.org/docs/api/api_key.html
    """
    try:
        from fredapi import Fred
    except ImportError as exc:
        raise ImportError(
            "fredapi is required. Install with `pip install -r python/requirements.txt`."
        ) from exc

    api_key = os.environ.get("FRED_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "Set the FRED_API_KEY environment variable before running this script."
        )

    fred = Fred(api_key=api_key)
    series = fred.get_series(FRED_COPPER_SERIES)
    series.to_csv(output_path, header=["copper_price_usd_per_lb"])
    print(f"Saved copper prices to {output_path}")


def print_manual_download_instructions():
    print("CASEN microdata (2003, 2006, 2009, 2011):")
    print(f"  Download manually from {CASEN_URL}")
    print(f"  Place raw files under {CASEN_DIR}/<year>/")
    print()
    print("INE ENE quarterly microdata (2003-2011):")
    print(f"  Download manually from {INE_ENE_URL}")
    print(f"  Place raw files under {ENE_DIR}/<year>_<quarter>/")


if __name__ == "__main__":
    ensure_dirs()
    print_manual_download_instructions()
    try:
        download_copper_prices()
    except (ImportError, EnvironmentError) as err:
        print(f"Skipping copper price download: {err}")
