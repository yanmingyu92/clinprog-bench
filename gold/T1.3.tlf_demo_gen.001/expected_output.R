# ================================================================
# Table 14-1.03: Summary of Demographic and Baseline Characteristics
# Study: CDISCPilot01
# Population: ITT
# Packages: rtables, haven, dplyr
# ================================================================

library(rtables)
library(haven)
library(dplyr)

# --- Read ADSL ---
adsl <- read_xpt("path/to/adam/adsl.xpt") %>%
  filter(ITTFL == "Y")

# --- Define factor for treatment ---
adsl <- adsl %>%
  mutate(
    TRT01P = factor(TRT01P,
      levels = c("Placebo", "Xanomeline Low Dose", "Xanomeline High Dose")
    )
  )

# --- Build table ---
lyt <- basic_table(show_colcounts = TRUE) %>%
  split_cols_by("TRT01P") %>%
  add_overall_col("Total") %>%

  # Continuous variables
  analyze_vars(
    vars = c("AGE", "HEIGHTBL", "WEIGHTBL", "BMIBL", "MMSETOT"),
    var_labels = c("Age (years)", "Height (cm)", "Weight (kg)",
                   "BMI (kg/m^2)", "MMSE Total Score"),
    stats = list(
      n = function(x) sum(!is.na(x)),
      mean_sd = function(x) {
        paste0(formatC(mean(x, na.rm=TRUE), digits=1, format="f"), " (",
               formatC(sd(x, na.rm=TRUE), digits=2, format="f"), ")")
      },
      median = function(x) formatC(median(x, na.rm=TRUE), digits=1, format="f"),
      range = function(x) paste0(min(x, na.rm=TRUE), "; ", max(x, na.rm=TRUE))
    ),
    formats = list(
      n = "xx", mean_sd = "xx.xx (xx.xx)",
      median = "xx.x", range = "xx.x; xx.x"
    )
  ) %>%

  # Categorical variables
  analyze_vars(
    vars = c("SEX", "RACE", "ETHNIC"),
    var_labels = c("Sex", "Race", "Ethnicity"),
    stats = list(count_pct = function(x) {
      tbl <- table(x)
      n <- as.numeric(tbl)
      pct <- formatC(n / sum(!is.na(x)) * 100, digits=1, format="f")
      paste0(n, " (", pct, "%)")
    })
  )

# --- Build and output ---
tbl <- build_table(lyt, adsl)

# --- Export RTF ---
as_rtf(tbl, file = "path/to/output/tlf-demographic.rtf")
