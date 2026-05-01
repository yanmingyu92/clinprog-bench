# ================================================================
# 14-2.04: Visit Compliance
# Study: CDISCPilot01
# Population: ITT
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
as_rtf(tbl, file = "path/to/output/tlf-visit_comp.rtf")
