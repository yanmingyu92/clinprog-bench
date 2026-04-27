# ================================================================
# Table 14-4.02: AE by System Organ Class and Preferred Term
# Study: CDISCPilot01
# Population: Safety, Treatment-Emergent AEs
# Packages: Tplyr, haven, dplyr
# ================================================================

library(Tplyr)
library(haven)
library(dplyr)

# --- Read ADAE and ADSL ---
adae <- read_xpt("path/to/adam/adae.xpt")
adsl <- read_xpt("path/to/adam/adsl.xpt") %>%
  filter(SAFFL == "Y")

# --- Treatment group counts ---
pop_counts <- adsl %>%
  count(TRT01P) %>%
  deframe()

# --- Filter treatment-emergent AEs ---
adae_t <- adae %>%
  filter(SAFFL == "Y" & TRTEMFL == "Y")

# --- Build Tplyr table ---
t <- tplyr_table(adae_t, TRT01P) %>%
  set_pop_data(adsl) %>%
  set_pop_treat_var(TRT01P) %>%
  set_distinct_by(USUBJID) %>%
  set_pop_where(SAFFL == "Y") %>%
  set_treatment_groups(
    "Placebo" = pop_counts["Placebo"],
    "Xanomeline Low Dose" = pop_counts["Xanomeline Low Dose"],
    "Xanomeline High Dose" = pop_counts["Xanomeline High Dose"]
  ) %>%
  add_total_group() %>%

  # Any AE summary row
  add_layer(
    group_count(AEBODSYS) %>%
      set_distinct_by(USUBJID) %>%
      add_nested_layer(
        group_count(AEDECOD) %>%
          set_distinct_by(USUBJID)
      ) %>%
      set_where(TRTEMFL == "Y") %>%
      set_format_strings(
        n_counts = set_format_strings(
          "n (%)",
          n = get_option("n_counts_n"),
          pct = get_option("n_counts_pct")
        )
      )
  )

# --- Build and apply 5% threshold ---
result <- build(t)

# --- Apply 5% incidence filter ---
result_filtered <- result %>%
  filter_at(vars(starts_with("var1_")), any_vars(. >= 5))

# --- Sort by SOC frequency then PT alphabetically ---
result_sorted <- result_filtered %>%
  arrange(desc(order_layer))

# --- Export RTF ---
write_rtf(result_sorted, file = "path/to/output/tlf-ae-soc-pt.rtf")
