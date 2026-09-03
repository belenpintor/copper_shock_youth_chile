#!/usr/bin/env Rscript
# 04_visualization.R
#
# Publication-ready plots summarizing the main results.
#
# Usage:
#   Rscript r/04_visualization.R
#
# Input:
#   data/processed/panel_youth.csv
#
# Output:
#   plots/effect_by_year.png
#   plots/heterogeneity_by_skill.png

suppressPackageStartupMessages({
  library(dplyr)
  library(readr)
  library(ggplot2)
})

input_path <- file.path("data", "processed", "panel_youth.csv")
plots_dir <- "plots"

if (!file.exists(input_path)) {
  stop(sprintf("%s not found. Run the Python pipeline first (see README).", input_path))
}

dir.create(plots_dir, showWarnings = FALSE, recursive = TRUE)

panel <- read_csv(input_path, show_col_types = FALSE)

# --- Event-study style plot: outcome gap by year ---
gap_by_year <- panel %>%
  group_by(year, high_exposure) %>%
  summarise(mean_enrolled = mean(enrolled, na.rm = TRUE), .groups = "drop") %>%
  tidyr::pivot_wider(names_from = high_exposure, values_from = mean_enrolled,
                      names_prefix = "exposure_") %>%
  mutate(gap = exposure_1 - exposure_0)

p_gap <- ggplot(gap_by_year, aes(x = year, y = gap)) +
  geom_line() +
  geom_point() +
  geom_hline(yintercept = 0, linetype = "dotted") +
  geom_vline(xintercept = 2003, linetype = "dashed") +
  labs(
    title = "Enrollment Gap: High- vs. Low-Exposure Regions",
    x = "Year", y = "Enrollment Gap"
  ) +
  theme_minimal()

ggsave(file.path(plots_dir, "effect_by_year.png"), p_gap, width = 8, height = 5)

# --- Heterogeneity by skill level ---
het_skill <- panel %>%
  group_by(high_exposure, low_skill) %>%
  summarise(mean_enrolled = mean(enrolled, na.rm = TRUE), .groups = "drop")

p_het <- ggplot(het_skill, aes(x = factor(high_exposure), y = mean_enrolled,
                                fill = factor(low_skill))) +
  geom_col(position = "dodge") +
  labs(
    title = "Enrollment by Exposure and Skill Level",
    x = "High Exposure", y = "Share Enrolled", fill = "Low Skill"
  ) +
  theme_minimal()

ggsave(file.path(plots_dir, "heterogeneity_by_skill.png"), p_het, width = 8, height = 5)

cat("Publication-ready plots saved to plots/.\n")
