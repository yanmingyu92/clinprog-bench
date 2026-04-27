# ================================================================
# Figure 14-5.01: Kaplan-Meier Plot - Time to First Dermatologic Event
# Study: CDISCPilot01
# Population: Safety
# Packages: ggplot2, survival, survminer, haven, dplyr
# ================================================================

library(ggplot2)
library(survival)
library(survminer)
library(haven)
library(dplyr)

# --- Read ADTTE and ADSL ---
adtte <- read_xpt("path/to/adam/adtte.xpt")
adsl  <- read_xpt("path/to/adam/adsl.xpt") %>%
  filter(SAFFL == "Y")

# --- Filter to Safety population ---
adtte_saf <- adtte %>%
  filter(USUBJID %in% adsl$USUBJID) %>%
  mutate(
    event = 1 - CNSR,  # CNSR=1 censored, CNSR=0 event
    TRT01P = factor(TRT01P,
      levels = c("Placebo", "Xanomeline Low Dose", "Xanomeline High Dose")
    )
  )

# --- Fit Kaplan-Meier curves ---
km_fit <- survfit(
  Surv(AVAL, event) ~ TRT01P,
  data = adtte_saf
)

# --- Log-rank test ---
logrank <- survdiff(Surv(AVAL, event) ~ TRT01P, data = adtte_saf)
p_value <- 1 - pchisq(logrank$chisq, df = length(logrank$n) - 1)

# --- Median time-to-event ---
median_ci <- surv_median(km_fit)

# --- Plot KM curves ---
km_plot <- ggsurvplot(
  km_fit,
  data = adtte_saf,
  risk.table = TRUE,
  risk.table.col = "strata",
  risk.table.height = 0.3,
  conf.int = TRUE,
  conf.int.style = "ribbon",
  censor = TRUE,
  pval = paste0("Log-rank p = ", formatC(p_value, digits=3, format="f")),
  pval.method = TRUE,
  surv.median.line = "hv",
  palette = c("#E7B800", "#2E9FDF", "#FC4E07"),
  xlab = "Days Since First Dose",
  ylab = "Probability of No Dermatologic Event",
  title = "Figure 14-5.01: Time to First Dermatologic Event",
  legend.labs = c("Placebo", "Xanomeline Low", "Xanomeline High"),
  legend.title = "Treatment Group",
  font.main = c(14, "bold"),
  font.x = c(12),
  font.y = c(12),
  ggtheme = theme_bw()
)

# --- Export PDF ---
pdf("path/to/output/tlf-kmplot.pdf", width = 10, height = 8)
print(km_plot)
dev.off()
