#!/usr/bin/env Rscript
# 01_descriptive_stats.R
#
# Summary statistics and trends for the youth panel, before running the
# main IV-DID specification.
#
# Usage:
#   Rscript r/01_descriptive_stats.R
#
# Input:
#   data/processed/panel_youth.csv
#
# Output:
#   tables/summary_stats.csv
#   plots/pretrends_enrollment.png
#   plots/pretrends_labor_participation.png

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(ggplot2)
})

input_path <- file.path("data", "processed", "panel_youth.csv")
tables_dir <- "tables"
plots_dir <- "plots"

if (!file.exists(input_path)) {
  stop(sprintf("%s not found. Run the Python pipeline first (see README).", input_path))
}

dir.create(tables_dir, showWarnings = FALSE, recursive = TRUE)
dir.create(plots_dir, showWarnings = FALSE, recursive = TRUE)

panel <- read_csv(input_path, show_col_types = FALSE)

# --- Summary statistics by exposure group ---
summary_stats <- panel %>%
  group_by(high_exposure) %>%
  summarise(
    n = n(),
    mean_enrolled = mean(enrolled, na.rm = TRUE),
    mean_labor_force = mean(in_labor_force, na.rm = TRUE),
    mean_age = mean(age, na.rm = TRUE),
    mean_education_years = mean(education_years, na.rm = TRUE),
    .groups = "drop"
  )

write_csv(summary_stats, file.path(tables_dir, "summary_stats.csv"))
print(summary_stats)

# --- Pre-trend visualization: enrollment ---
trends_enrollment <- panel %>%
  group_by(year, high_exposure) %>%
  summarise(mean_enrolled = mean(enrolled, na.rm = TRUE), .groups = "drop")

p_enrollment <- ggplot(trends_enrollment, aes(x = year, y = mean_enrolled,
                                               color = factor(high_exposure))) +
  geom_line() +
  geom_point() +
  geom_vline(xintercept = 2003, linetype = "dashed") +
  labs(
    title = "School Enrollment Trends by Regional Mining Exposure",
    x = "Year", y = "Share Enrolled", color = "High Exposure"
  ) +
  theme_minimal()

ggsave(file.path(plots_dir, "pretrends_enrollment.png"), p_enrollment,
       width = 8, height = 5)

# --- Pre-trend visualization: labor force participation ---
trends_labor <- panel %>%
  group_by(year, high_exposure) %>%
  summarise(mean_labor_force = mean(in_labor_force, na.rm = TRUE), .groups = "drop")

p_labor <- ggplot(trends_labor, aes(x = year, y = mean_labor_force,
                                     color = factor(high_exposure))) +
  geom_line() +
  geom_point() +
  geom_vline(xintercept = 2003, linetype = "dashed") +
  labs(
    title = "Youth Labor Force Participation Trends by Regional Mining Exposure",
    x = "Year", y = "Share in Labor Force", color = "High Exposure"
  ) +
  theme_minimal()

ggsave(file.path(plots_dir, "pretrends_labor_participation.png"), p_labor,
       width = 8, height = 5)

cat("Descriptive stats and pre-trend plots saved.\n")
