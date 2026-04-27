# ================================================================
# ADADAS (ADAS-Cog Analysis Dataset) Creation Program
# Study: CDISCPilot01
# Standard: ADaM IG v1.1 (BDS)
# Packages: admiral, haven, dplyr, xportr
# ================================================================

library(admiral)
library(haven)
library(dplyr)
library(tidyr)
library(xportr)

# --- Read source datasets ---
qs   <- read_xpt("C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/04_sdtm/datasets/qs.xpt")
adsl <- read_xpt("C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/05_adam/datasets/adsl.xpt")

# --- Filter to ADAS-Cog questionnaire ---
adadas_raw <- qs %>%
  filter(QSCAT == "ADAS-COG")

# --- Define PARAMCD mapping ---
adadas <- adadas_raw %>%
  mutate(
    PARAMCD = case_when(
      QSTESTCD == "ACTOT"   ~ "ACTOT",
      QSTESTCD == "ACITM01" ~ "ACITM01",
      QSTESTCD == "ACITM02" ~ "ACITM02",
      QSTESTCD == "ACITM03" ~ "ACITM03",
      QSTESTCD == "ACITM04" ~ "ACITM04",
      QSTESTCD == "ACITM05" ~ "ACITM05",
      QSTESTCD == "ACITM06" ~ "ACITM06",
      QSTESTCD == "ACITM07" ~ "ACITM07",
      QSTESTCD == "ACITM08" ~ "ACITM08",
      QSTESTCD == "ACITM09" ~ "ACITM09",
      QSTESTCD == "ACITM10" ~ "ACITM10",
      QSTESTCD == "ACITM11" ~ "ACITM11"
    ),
    PARAM = case_when(
      PARAMCD == "ACTOT"   ~ "ADAS-Cog (11) Total Score",
      PARAMCD == "ACITM01" ~ "Word Recall Task",
      PARAMCD == "ACITM02" ~ "Naming Objects and Fingers",
      PARAMCD == "ACITM03" ~ "Commands",
      PARAMCD == "ACITM04" ~ "Constructional Praxis",
      PARAMCD == "ACITM05" ~ "Ideational Praxis",
      PARAMCD == "ACITM06" ~ "Orientation",
      PARAMCD == "ACITM07" ~ "Word Recognition",
      PARAMCD == "ACITM08" ~ "Remembering Test Instructions",
      PARAMCD == "ACITM09" ~ "Spoken Language Ability",
      PARAMCD == "ACITM10" ~ "Comprehension",
      PARAMCD == "ACITM11" ~ "Word-Finding Difficulty"
    )
  )

# --- Visit windowing ---
adadas <- adadas %>%
  mutate(
    AWTARGET = case_when(
      VISITNUM ==  0 ~   0,
      VISITNUM ==  8 ~  56,
      VISITNUM == 16 ~ 112,
      VISITNUM == 24 ~ 168
    ),
    AWLO = case_when(
      VISITNUM ==  0 ~  NA_real_,
      VISITNUM ==  8 ~  29,
      VISITNUM == 16 ~  85,
      VISITNUM == 24 ~ 141
    ),
    AWHI = case_when(
      VISITNUM ==  0 ~   1,
      VISITNUM ==  8 ~  84,
      VISITNUM == 16 ~ 140,
      VISITNUM == 24 ~ 336
    )
  )

# --- Derive AVAL and compute BASE, CHG, PCHG ---
adadas <- adadas %>%
  mutate(AVAL = as.numeric(QSSTRESC))

# Baseline value (visit 0)
baseline_vals <- adadas %>%
  filter(VISITNUM == 0) %>%
  select(USUBJID, PARAMCD, BASE = AVAL)

adadas <- adadas %>%
  left_join(baseline_vals, by = c("USUBJID", "PARAMCD")) %>%
  mutate(
    CHG  = AVAL - BASE,
    PCHG = if_else(BASE != 0, (CHG / BASE) * 100, NA_real_)
  )

# --- LOCF imputation ---
adadas_locf <- adadas %>%
  filter(VISITNUM > 0 & !is.na(AVAL)) %>%
  arrange(USUBJID, PARAMCD, AWTARGET) %>%
  group_by(USUBJID, PARAMCD) %>%
  fill(AVAL, CHG, PCHG, .direction = "down") %>%
  mutate(DTYPE = if_else(is.na(QSSTRESC) & !is.na(AVAL), "LOCF", NA_character_)) %>%
  ungroup()

adadas <- bind_rows(
  adadas %>% filter(VISITNUM == 0),
  adadas_locf
)

# --- Analysis flag ---
adadas <- adadas %>%
  mutate(ANL01FL = if_else(PARAMCD == "ACTOT" & !is.na(AVAL), "Y", ""))

# --- Merge with ADSL ---
adsl_sub <- adsl %>%
  filter(EFFFL == "Y") %>%
  select(USUBJID, TRT01P, TRT01A, TRT01PN, TRT01AN, ITTFL, SAFFL, EFFFL)

adadas <- adadas %>%
  inner_join(adsl_sub, by = "USUBJID")

# --- Apply ADaM metadata and export ---
adadas <- adadas %>%
  xportr_type(path = "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/05_adam/ADaM_Specifications.xlsx", domain = "ADADAS") %>%
  xportr_label(path = "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/track1-pilot01/external/eSubmission-Benchmark/05_adam/ADaM_Specifications.xlsx", domain = "ADADAS")

write_xpt(adadas, path = "C:/Users/yanmi/Downloads/ClinAgent-main/ClinAgent-main/bench-program/clinprog-bench/gold/_exec_output/adadas.xpt")
