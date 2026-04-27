# ================================================================
# ADSL (Subject-Level Analysis Dataset) Creation Program
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
dm  <- read_xpt("path/to/sdtm/dm.xpt")
ds  <- read_xpt("path/to/sdtm/ds.xpt")
ex  <- read_xpt("path/to/sdtm/ex.xpt")
vs  <- read_xpt("path/to/sdtm/vs.xpt")
sc  <- read_xpt("path/to/sdtm/sc.xpt")
qs  <- read_xpt("path/to/sdtm/qs.xpt")
suppdm <- read_xpt("path/to/sdtm/suppdm.xpt")

# --- Start ADSL from DM (exclude screen failures) ---
adsl <- dm %>%
  filter(ACTARMCD != "Scrnfail") %>%
  select(STUDYID, USUBJID, SUBJID, SITEID, AGE, AGEU, SEX, RACE, ETHNIC, COUNTRY)

# --- Derive treatment variables ---
adsl <- adsl %>%
  mutate(
    TRT01P  = case_when(
      ACTARMCD == "Pbo"    ~ "Placebo",
      ACTARMCD == "Xan_Lo" ~ "Xanomeline Low Dose",
      ACTARMCD == "Xan_Hi" ~ "Xanomeline High Dose"
    ),
    TRT01PN = case_when(
      ACTARMCD == "Pbo"    ~ 0L,
      ACTARMCD == "Xan_Lo" ~ 54L,
      ACTARMCD == "Xan_Hi" ~ 81L
    ),
    TRT01A  = TRT01P,
    TRT01AN = TRT01PN
  )

# --- Derive population flags ---
# ITT: all randomized subjects
adsl <- adsl %>%
  mutate(ITTFL = "Y")

# Safety: received at least 1 dose
ex_dosed <- ex %>%
  filter(!is.na(EXDOSE) & EXDOSE > 0) %>%
  distinct(USUBJID)

adsl <- adsl %>%
  mutate(SAFFL = if_else(USUBJID %in% ex_dosed$USUBJID, "Y", "N"))

# Efficacy: at least one post-beline efficacy assessment
qs_postbl <- qs %>%
  filter(QSCAT == "ADAS-COG" & VISITNUM > 0) %>%
  distinct(USUBJID)

adsl <- adsl %>%
  mutate(EFFFL = if_else(USUBJID %in% qs_postbl$USUBJID, "Y", "N"))

# Completers of Week 24
ds_comp <- ds %>%
  filter(VISIT == "WEEK 24" & DSCAT == "DISPOSITION TRIAL" & DSDECOD == "COMPLETED") %>%
  distinct(USUBJID)

adsl <- adsl %>%
  mutate(COMP24FL = if_else(USUBJID %in% ds_comp$USUBJID, "Y", "N"))

# --- Derive baseline measures from VS ---
vs_bl <- vs %>%
  filter(VSBLFL == "Y") %>%
  select(USUBJID, VSTESTCD, VSSTRESN) %>%
  tidyr::pivot_wider(names_from = VSTESTCD, values_from = VSSTRESN)

adsl <- adsl %>%
  left_join(vs_bl, by = "USUBJID") %>%
  rename(HEIGHTBL = HEIGHT, WEIGHTBL = WEIGHT) %>%
  mutate(BMIBL = WEIGHTBL / (HEIGHTBL / 100)^2)

# --- Derive MMSE total from QS ---
mmse <- qs %>%
  filter(QSTESTCD == "MMSETOT" & VISIT == "SCREENING") %>%
  distinct(USUBJID, .keep_all = TRUE) %>%
  select(USUBJID, MMSETOT = QSSTRESC) %>%
  mutate(MMSETOT = as.numeric(MMSETOT))

adsl <- adsl %>% left_join(mmse, by = "USUBJID")

# --- Derive disposition from DS ---
ds_discon <- ds %>%
  filter(DSCAT == "DISPOSITION TRIAL" & DSDECOD != "COMPLETED") %>%
  distinct(USUBJID)

adsl <- adsl %>%
  mutate(
    DISCONFL = if_else(USUBJID %in% ds_discon$USUBJID, "Y", "N"),
    EOSSTT   = if_else(USUBJID %in% ds_discon$USUBJID, "Discontinued", "Completed")
  )

ds_ae <- ds %>%
  filter(DSDECOD == "ADVERSE EVENT") %>%
  distinct(USUBJID)

adsl <- adsl %>%
  mutate(DSRAEFL = if_else(USUBJID %in% ds_ae$USUBJID, "Y", ""))

# --- Treatment duration ---
ex_range <- ex %>%
  group_by(USUBJID) %>%
  summarise(
    TRTSDT = min(as.Date(EXSTDTC), na.rm = TRUE),
    TRTEDT = max(as.Date(EXENDTC), na.rm = TRUE)
  )

adsl <- adsl %>%
  left_join(ex_range, by = "USUBJID") %>%
  mutate(TRTDURD = as.integer(TRTEDT - TRTSDT) + 1L)

# --- Apply ADaM metadata and export ---
adsl <- adsl %>%
  xportr_type(path = "path/to/adam_spec.xlsx", domain = "ADSL") %>%
  xportr_label(path = "path/to/adam_spec.xlsx", domain = "ADSL")

write_xpt(adsl, path = "path/to/output/adsl.xpt")
