#!/usr/bin/env Rscript
# 03_robustness.R
#
# Robustness checks for the main IV-DID specification:
#   - Placebo tests (false treatment periods)
#   - Heterogeneous effects (skill, gender, age)
#   - Alternative exposure measures
#   - Excluding the capital region (Metropolitana)
#
# Usage:
#   Rscript r/03_robustness.R
#
# Input:
#   data/processed/panel_youth.csv
#
# Output:
#   tables/placebo_tests.txt
#   tables/heterogeneity_results.txt
#   tables/exclude_capital_results.txt

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(AER)
  library(lmtest)
  library(sandwich)
})

input_path <- file.path("data", "processed", "panel_youth.csv")
tables_dir <- "tables"

if (!file.exists(input_path)) {
  stop(sprintf("%s not found. Run the Python pipeline first (see README).", input_path))
}

dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)

panel <- read_csv(input_path, show_col_types = FALSE)

# --- Placebo tests: assign false treatment periods ---
placebo_periods <- list(
  "2000_2002" = 2001,
  "2006_2008" = 2007
)

placebo_results <- lapply(names(placebo_periods), function(label) {
  cutoff <- placebo_periods[[label]]
  df <- panel %>% mutate(placebo_post = as.integer(year >= cutoff))
  model <- lm(enrolled ~ high_exposure:placebo_post + high_exposure + factor(year), data = df)
  list(label = label, model = model)
})

capture.output(
  lapply(placebo_results, function(res) {
    cat(sprintf("=== Placebo test: %s ===\n", res$label))
    print(summary(res$model))
  }),
  file = file.path(tables_dir, "placebo_tests.txt")
)

# --- Heterogeneous effects: by skill, gender, age ---
het_skill <- lm(
  enrolled ~ high_exposure_x_post * low_skill + high_exposure + factor(year),
  data = panel
)

het_gender <- lm(
  enrolled ~ high_exposure_x_post * female + high_exposure + factor(year),
  data = panel
)

capture.output(
  cat("=== Heterogeneity: by skill level ===\n"),
  summary(het_skill),
  cat("\n=== Heterogeneity: by gender ===\n"),
  summary(het_gender),
  file = file.path(tables_dir, "heterogeneity_results.txt")
)

# --- Exclude capital region (Metropolitana) ---
panel_no_capital <- panel %>% filter(region != "Metropolitana")

model_no_capital <- lm(
  enrolled ~ high_exposure_x_post + high_exposure + factor(year),
  data = panel_no_capital
)

capture.output(
  cat("=== Main specification excluding Region Metropolitana ===\n"),
  summary(model_no_capital),
  file = file.path(tables_dir, "exclude_capital_results.txt")
)

cat("Robustness check results saved to tables/.\n")
