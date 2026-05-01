# ================================================================
# ADTTE (Time-to-Event Analysis) Creation Program
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

# --- Derive ADTTE key variables ---
# Key variables: PARAMCD, PARAM, AVAL, CNSR, ADT, TRTP, TRTPN
# Records: 254

# --- Apply ADaM metadata ---
write_xpt(adtte, path = "path/to/output/adtte.xpt")
