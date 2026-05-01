# ================================================================
# 14-1.01: Screening Summary
# Study: CDISCPilot01
# Population: All Screened
# ================================================================

library(rtables)
library(haven)
library(dplyr)

# --- Read ADSL ---
data <- read_xpt("path/to/adam/ADSL.xpt") %>%
  filter(...)

# --- Build table ---
lyt <- basic_table(show_colcounts = TRUE) %>%
  split_cols_by("TRT01P")

tbl <- build_table(lyt, data)

# --- Export RTF ---
as_rtf(tbl, file = "path/to/output/tlf-screen.rtf")
