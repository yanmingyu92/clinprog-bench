# ================================================================
# ADSL (Subject-Level (disposition focus)) Creation Program
# Study: CDISCPilot01
# Standard: ADaM IG v1.1
# Packages: admiral, haven, dplyr, xportr
# ================================================================

library(admiral)
library(haven)
library(dplyr)
library(xportr)

# --- Read source datasets ---
adsl <- read_xpt("path/to/adam/adsl.xpt")

# --- Derive ADSL key variables ---
# Key variables: DISCONFL, DSRAEFL, EOSSTT, DCSREAS, TRTDURD
# Records: 254

# --- Apply ADaM metadata ---
write_xpt(adsl, path = "path/to/output/adsl.xpt")
