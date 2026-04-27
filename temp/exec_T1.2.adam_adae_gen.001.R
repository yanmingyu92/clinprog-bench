# ================================================================
# ADAE (Adverse Events Analysis Dataset) Creation Program
# Study: CDISCPilot01
# Standard: ADaM IG v1.1
# Packages: admiral, haven, dplyr, xportr
# ================================================================

library(admiral)
library(haven)
library(dplyr)
library(xportr)
library(lubridate)

# --- Read source datasets ---
ae   <- read_xpt("C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/04_sdtm/datasets/ae.xpt")
adsl <- read_xpt("C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/05_adam/datasets/adsl.xpt")

# --- Start ADAE from SDTM AE ---
adae <- ae %>%
  left_join(
    adsl %>%
      select(USUBJID, TRT01P, TRT01A, TRT01PN, TRT01AN,
             ITTFL, SAFFL, EFFFL, TRTSDT),
    by = "USUBJID"
  )

# --- Derive treatment variables ---
adae <- adae %>%
  mutate(
    TRTP  = TRT01P,
    TRTPN = TRT01PN,
    TRTA  = TRT01A,
    TRTAN = TRT01AN
  )

# --- Derive treatment-emergent flag ---
adae <- adae %>%
  mutate(
    ASTDT = as.Date(AESTDTC),
    AENDT = as.Date(AEENDTC),
    TRTEMFL = if_else(!is.na(ASTDT) & !is.na(TRTSDT) & ASTDT >= TRTSDT,
                      "Y", "N")
  )

# --- Derive analysis relative days ---
adae <- adae %>%
  mutate(
    ASTDY = as.integer(ASTDT - TRTSDT) + 1L,
    AENDY = as.integer(AENDT - TRTSDT) + 1L
  )

# --- Derive analysis severity (max severity per AE) ---
adae <- adae %>%
  mutate(ASEV = AESEV)

# --- Apply ADaM metadata ---
adae <- adae %>%
  xportr_type(path = "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/05_adam/ADaM_Specifications.xlsx", domain = "ADAE") %>%
  xportr_label(path = "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/05_adam/ADaM_Specifications.xlsx", domain = "ADAE")

write_xpt(adae, path = "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/clinprog-bench/gold/_exec_output/adae.xpt")
