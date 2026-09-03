#!/usr/bin/env Rscript
# 02_iv_regression.R
#
# Main IV-DID specification:
#   Y_it = b0 + b1 * HighExposure_i x Post2003_t + b2 * HighExposure_i
#          + b3 * t + e_it
# instrumented with:
#   Shock_it = HighExposure_i x CopperPrice_t
#
# Usage:
#   Rscript r/02_iv_regression.R
#
# Input:
#   data/processed/panel_youth.csv
#
# Output:
#   tables/iv_regression_enrollment.txt
#   tables/iv_regression_labor.txt

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(AER)      # ivreg
  library(lmtest)   # coeftest
  library(sandwich) # clustered SEs
})

input_path <- file.path("data", "processed", "panel_youth.csv")
tables_dir <- "tables"

if (!file.exists(input_path)) {
  stop(sprintf("%s not found. Run the Python pipeline first (see README).", input_path))
}

dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)

panel <- read_csv(input_path, show_col_types = FALSE)

# Reduced-form DID specification (OLS, for comparison).
did_enrollment <- lm(
  enrolled ~ high_exposure_x_post + high_exposure + factor(year),
  data = panel
)

did_labor <- lm(
  in_labor_force ~ high_exposure_x_post + high_exposure + factor(year),
  data = panel
)

# IV specification: instrument the exposure x post interaction with the
# exposure x copper price shock.
iv_enrollment <- ivreg(
  enrolled ~ high_exposure_x_post + high_exposure + factor(year) |
    shock + high_exposure + factor(year),
  data = panel
)

iv_labor <- ivreg(
  in_labor_force ~ high_exposure_x_post + high_exposure + factor(year) |
    shock + high_exposure + factor(year),
  data = panel
)

# Cluster standard errors at the region level.
cluster_se <- function(model, cluster_var) {
  vcov_cl <- vcovCL(model, cluster = cluster_var)
  coeftest(model, vcov = vcov_cl)
}

results_enrollment <- cluster_se(iv_enrollment, panel$region)
results_labor <- cluster_se(iv_labor, panel$region)

capture.output(
  cat("=== DID (OLS): School Enrollment ===\n"),
  summary(did_enrollment),
  cat("\n=== IV-DID: School Enrollment ===\n"),
  results_enrollment,
  file = file.path(tables_dir, "iv_regression_enrollment.txt")
)

capture.output(
  cat("=== DID (OLS): Labor Force Participation ===\n"),
  summary(did_labor),
  cat("\n=== IV-DID: Labor Force Participation ===\n"),
  results_labor,
  file = file.path(tables_dir, "iv_regression_labor.txt")
)

cat("IV-DID regression results saved to tables/.\n")
