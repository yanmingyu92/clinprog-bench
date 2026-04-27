# ================================================================
# 14-5.02: Forest Plot (Subgroup)
# Study: CDISCPilot01
# Population: Efficacy
# ================================================================

library(rtables)
library(haven)
library(dplyr)

# --- Read ADADAS ---
data <- read_xpt("path/to/adam/ADADAS.xpt") %>%
  filter(...)

# --- Build table ---
lyt <- basic_table(show_colcounts = TRUE) %>%
  split_cols_by("TRT01P")

tbl <- build_table(lyt, data)

# --- Export RTF ---
as_rtf(tbl, file = "path/to/output/tlf-forest.rtf")
