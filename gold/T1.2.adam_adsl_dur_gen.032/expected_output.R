# ================================================================
# ADSL (Subject-Level (treatment duration)) Creation Program
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
# Key variables: TRTSDT, TRTEDT, TRTDURD, TRT01P, TRT01PN
# Records: 254

# --- Apply ADaM metadata ---
write_xpt(adsl, path = "path/to/output/adsl.xpt")
