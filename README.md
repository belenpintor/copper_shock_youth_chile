# Causal Impact of Copper Price Shock on Youth Education and Labor Participation in Chile

## Research Question

Did the sustained increase in copper prices (2003-2011) reduce school enrollment
and increase labor participation among youth in mining-dependent Chilean regions?

Chile is the world's largest copper producer. Copper prices rose from
$0.80/lb (2003) to $4.00/lb (2008), settling at $3.00-4.00/lb (2009-2011).
This mining boom raised demand for low- and medium-skilled workers, altering
the regional skill premium and — potentially — the opportunity cost of
staying in school for youth in mining-dependent regions. This project asks
whether that demand shock had a measurable, causal effect on youth schooling
and labor market decisions.

## Methodology

**Design:** Instrumental Variables (IV) with Difference-in-Differences (DID).

Main specification:

```
Y_it = b0 + b1 * HighExposure_i x Post2003_t + b2 * HighExposure_i + b3 * t + e_it
```

- `Y_it`: outcome (school enrollment, labor force participation) for individual/region `i` at time `t`
- `HighExposure_i`: baseline regional mining employment intensity
- `Post2003_t`: indicator for the post-2003 copper boom period
- `b1`: the treatment effect of interest (causal impact of the shock)

**Instrument.** Because regional exposure could be correlated with
unobserved local trends, the treatment interaction is instrumented with an
interaction of baseline exposure and the (plausibly exogenous) world copper
price:

```
Shock_it = HighExposure_i x CopperPrice_t
```

**Treatment definition.** Regions are classified by proportion of the labor
force in mining and pre-shock mining employment intensity:

- High-exposure regions: Antofagasta, Tarapacá, Coquimbo, Atacama
- Low-exposure regions: all other regions (control group)

**Robustness checks:**

- Pre-trend analysis (2000-2003) to assess parallel trends
- Placebo tests using false treatment periods (2000-2002, 2006-2008)
- Heterogeneous effects by skill level, gender, and age
- Alternative exposure measures (employment share vs. export value)
- Excluding the capital region (Región Metropolitana) as a confounder check

## Data

| Source | Description | Coverage |
| --- | --- | --- |
| CASEN | Chilean Socio-Economic Characterization Survey | 2003-2011 (triennial) |
| INE (ENE) | National Labor Force Survey | 2003-2011 (quarterly) |
| FRED / LME | Copper prices (world market) | 2003-2011 (daily/monthly) |

CASEN and INE ENE microdata require manual download from the official
government portals due to registration/terms-of-use requirements; see
`python/01_download_data.py` for links and expected folder structure. Copper
prices can be fetched programmatically from FRED (requires a free
`FRED_API_KEY`).

- Raw data: `data/raw/`
- Processed/analysis-ready data: `data/processed/`

## Project Structure

```
copper_shock_youth_chile/
├── README.md
├── python/
│   ├── 01_download_data.py        # Fetch CASEN, INE, copper prices
│   ├── 02_clean_casen.py          # Standardize variables
│   ├── 03_merge_ine.py            # Regional labor data
│   ├── 04_merge_copper.py         # Copper prices by date
│   ├── 05_feature_engineering.py  # Treatment exposure, interactions
│   └── requirements.txt
├── r/
│   ├── 01_descriptive_stats.R     # Summary tables, trends
│   ├── 02_iv_regression.R         # Main specification + diagnostics
│   ├── 03_robustness.R            # Placebo, heterogeneity, alt specs
│   └── 04_visualization.R         # Publication-ready plots
├── data/
│   ├── raw/
│   └── processed/
├── plots/
└── tables/
```

## Reproducibility

Run the Python data pipeline first, then the R analysis, in order.

### 1. Python (data preparation)

```bash
cd python
pip install -r requirements.txt
python 01_download_data.py
python 02_clean_casen.py
python 03_merge_ine.py
python 04_merge_copper.py
python 05_feature_engineering.py
```

This produces the analysis-ready panel at `data/processed/panel_youth.csv`.

### 2. R (econometric analysis)

Install the required R packages once:

```r
install.packages(c("dplyr", "readr", "ggplot2", "tidyr", "AER", "lmtest", "sandwich"))
```

Then run the scripts in order from the repository root:

```bash
Rscript r/01_descriptive_stats.R
Rscript r/02_iv_regression.R
Rscript r/03_robustness.R
Rscript r/04_visualization.R
```

Outputs are written to `plots/` and `tables/`.

## Key Findings

_To be filled in once the pipeline has been run on real data._ Expected
outcomes based on the research design:

1. School enrollment decreases in high-exposure regions after 2003.
2. Youth labor force participation increases in high-exposure regions.
3. The effect is larger for low-skilled workers.
4. The effect is heterogeneous by gender, potentially reflecting differences
   in mining-sector wage exposure.

## Timeline (rough)

| Weeks | Milestone |
| --- | --- |
| 1-2 | Data acquisition + Python cleaning pipeline |
| 3-4 | Exploratory analysis + pre-trend visualization |
| 5-6 | Main IV-DID specifications in R |
| 7-8 | Robustness checks + heterogeneity analysis |
| 9-10 | Final plots + polished README |

## Caveats and Limitations

- **Identification assumption:** The IV strategy assumes copper prices are
  exogenous to individual schooling/labor decisions and affect youth
  outcomes only through regional mining labor demand (exclusion
  restriction). This should be scrutinized, particularly with respect to
  national macroeconomic co-movements.
- **Parallel trends:** The DID comparison requires that high- and
  low-exposure regions would have followed similar enrollment/labor trends
  absent the copper shock; pre-2003 trends should be inspected before
  interpreting results causally.
- **Survey comparability:** CASEN and ENE questionnaires and sampling
  frames may change across waves; variable harmonization (`02_clean_casen.py`)
  is critical and should be reviewed against each wave's official
  documentation.
- **Regional aggregation:** Treatment is defined at the region/comuna
  level, so effects reflect local labor market exposure rather than
  individual-level mining employment.
