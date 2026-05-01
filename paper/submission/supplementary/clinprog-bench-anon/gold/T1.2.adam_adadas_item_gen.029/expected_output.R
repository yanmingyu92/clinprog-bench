# ================================================================
# ADADAS (ADAS-Cog (item analysis)) Creation Program
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

# --- Derive ADADAS key variables ---
# Key variables: PARAMCD, ACITM01, ACITM02, ACITM03, ACTOT, AVAL, BASE
# Records: 2718

# --- Apply ADaM metadata ---
write_xpt(adadas, path = "path/to/output/adadas.xpt")
