# ================================================================
# 14-2.02: Concomitant Medications
# Study: CDISCPilot01
# Population: Safety
# ================================================================

library(rtables)
library(haven)
library(dplyr)

# --- Read ADCM ---
data <- read_xpt("path/to/adam/ADCM.xpt") %>%
  filter(...)

# --- Build table ---
lyt <- basic_table(show_colcounts = TRUE) %>%
  split_cols_by("TRT01P")

tbl <- build_table(lyt, data)

# --- Export RTF ---
as_rtf(tbl, file = "path/to/output/tlf-conmed.rtf")
