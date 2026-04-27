# ================================================================
# ADAE (Adverse Events (custom query)) Creation Program
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

# --- Derive ADAE key variables ---
# Key variables: CQ01NAM, TRTEMFL, ASEV, AREL, ASTDY
# Records: 1191

# --- Apply ADaM metadata ---
write_xpt(adae, path = "path/to/output/adae.xpt")
