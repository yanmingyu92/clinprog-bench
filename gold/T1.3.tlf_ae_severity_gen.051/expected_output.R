# ================================================================
# 14-4.04: AE by Maximum Severity
# Study: CDISCPilot01
# Population: Safety
# ================================================================

library(rtables)
library(haven)
library(dplyr)

# --- Read ADAE ---
data <- read_xpt("path/to/adam/ADAE.xpt") %>%
  filter(...)

# --- Build table ---
lyt <- basic_table(show_colcounts = TRUE) %>%
  split_cols_by("TRT01P")

tbl <- build_table(lyt, data)

# --- Export RTF ---
as_rtf(tbl, file = "path/to/output/tlf-ae_severity.rtf")
