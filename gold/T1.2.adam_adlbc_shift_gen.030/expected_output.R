# ================================================================
# ADLBC (Lab (shift analysis)) Creation Program
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

# --- Derive ADLBC key variables ---
# Key variables: SHIFT, ANRIND, BNRIND, AVAL, BASE, PARAMCD
# Records: 7778

# --- Apply ADaM metadata ---
write_xpt(adlbc, path = "path/to/output/adlbc.xpt")
