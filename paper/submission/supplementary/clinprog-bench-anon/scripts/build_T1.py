"""Generate T1 (codegen) benchmark tasks from eSubmission-Benchmark substrate.

Creates 10 task JSON files under tasks/T1_codegen/ and corresponding gold
SAS/R program outputs under gold/<task_id>/.

Usage:
    python scripts/build_T1.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks" / "T1_codegen"
GOLD_ROOT = ROOT / "gold"

SEED_REPO = "anonymous/eSubmission-Benchmark"
SEED_COMMIT = "658fcc05506b169a27dee6e2c3a1ccdaaf64a716"
DERIVATION_SCRIPT = "scripts/build_T1.py"

# ── Shared building blocks ──────────────────────────────────────────


def _provenance() -> dict:
    return {
        "seed_repo": SEED_REPO,
        "seed_commit": SEED_COMMIT,
        "derivation_script": DERIVATION_SCRIPT,
        "human_authors": ["R01"],
        "human_reviewers": ["R02"],
    }


def _task(
    task_id: str,
    subcategory: str,
    title: str,
    complexity: str,
    fixtures: list[str],
    spec: str,
    prompt: str,
    gold_path: str,
    oracle_params: dict,
) -> dict:
    return {
        "task_id": task_id,
        "category": "T1",
        "subcategory": subcategory,
        "title": title,
        "complexity": complexity,
        "license": "CC-BY-4.0",
        "provenance": _provenance(),
        "inputs": {
            "fixtures": fixtures,
            "spec": spec,
            "prompt": prompt,
        },
        "expected_outputs": {
            "kind": "sas_program",
            "gold_path": gold_path,
            "oracle": {"type": "slot_fill", "params": oracle_params},
        },
        "scoring": {"scorer": "codegen", "weight": 1.0},
        "leakage_audit": {"fixture_sha256_overlap": False, "prompt_ngram_hits": 0},
    }


# ── Task definitions ────────────────────────────────────────────────

TASKS: list[dict] = [
    # ── T1.1 SDTM domain programs ──────────────────────────────────
    _task(
        task_id="T1.1.sdtm_dm_gen.001",
        subcategory="T1.1",
        title="Generate SAS program to create SDTM DM domain from raw demographics",
        complexity="mixed",
        fixtures=[
            "fixtures/03_raw_data/create_missing_raw_data.R",
            "fixtures/04_sdtm/SDTM_Specifications.md",
            "fixtures/04_sdtm/programs/path.R",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#DM",
        prompt=(
            "Write a SAS program to create the SDTM DM (Demographics) domain "
            "dataset from raw source data. The program must: (1) Read raw "
            "demographics data, (2) Derive USUBJID as STUDYID-SITEID-SUBJID, "
            "(3) Map ARMCD/ARM from randomization data (Pbo, Xan_Lo, Xan_Hi), "
            "(4) Calculate RFICDTC from informed consent date, (5) Derive "
            "COUNTRY from SITEID, (6) Assign all required CDISC variables "
            "(STUDYID, DOMAIN, USUBJID, SUBJID, SITEID, ARMCD, ARM, "
            "ACTARMCD, ACTARM, AGE, AGEU, SEX, RACE, ETHNIC, COUNTRY, "
            "RFICDTC, RFXSTDTC, RFICDEC), (7) Apply variable attributes per "
            "SDTM specification, (8) Create a permanent SAS dataset with "
            "xport format. Include data step programming with proper labels "
            "and lengths per the SDTM specification."
        ),
        gold_path="gold/T1.1.sdtm_dm_gen.001/",
        oracle_params={
            "slots": [
                "required_variables[]",
                "usubjid_derivation",
                "arm_mapping_logic",
                "output_format",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T1.1.sdtm_ae_gen.001",
        subcategory="T1.1",
        title="Generate SAS program to create SDTM AE domain with MedDRA coding",
        complexity="complex",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
            "fixtures/04_sdtm/programs/path.R",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#AE",
        prompt=(
            "Write a SAS program to create the SDTM AE (Adverse Events) domain "
            "dataset. The program must: (1) Read raw adverse event data, "
            "(2) Derive USUBJID, AESEQ (sequential numbering per subject), "
            "(3) Map MedDRA coding hierarchy (AELLT → AEDECOD → AEHLT → "
            "AEHLGT → AEBODSYS), (4) Derive seriousness flags (AESER, "
            "AESCAN, AESCONG, AESDEATH, AESHOSP, AESLIFE, AESOD) from raw "
            "seriousness criteria, (5) Format AESTDTC and AEENDTC in ISO 8601, "
            "(6) Map AESEV, AEACN, AEREL, AEOUT per CDISC controlled "
            "terminology, (7) Handle supplemental qualifiers (SUPPAE) for "
            "variables that exceed SDTM model constraints, (8) Apply variable "
            "attributes per SDTM specification, (9) Output as transport file. "
            "The study uses MedDRA v8.0 for adverse event coding."
        ),
        gold_path="gold/T1.1.sdtm_ae_gen.001/",
        oracle_params={
            "slots": [
                "required_variables[]",
                "meddra_hierarchy",
                "seriousness_flag_logic",
                "date_handling",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T1.1.sdtm_vs_gen.001",
        subcategory="T1.1",
        title="Generate SAS program to create SDTM VS domain for vital signs",
        complexity="mixed",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
            "fixtures/04_sdtm/programs/path.R",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#VS",
        prompt=(
            "Write a SAS program to create the SDTM VS (Vital Signs) domain "
            "dataset. The program must: (1) Read raw vital signs data in wide "
            "format and transpose to long structure (one record per test per "
            "visit per subject), (2) Map VSTESTCD from raw test names to CDISC "
            "controlled terminology (HEIGHT, WEIGHT, DIABP, SYSBP, PULSE, "
            "TEMP, RESP), (3) Populate VSTEST, VSORRES, VSORRESU (original "
            "result/units), VSSTRESC, VSSTRESN, VSSTRESU (standardized), "
            "(4) Derive VSBLFL (baseline flag) for the last pre-treatment "
            "measurement, (5) Map visit information (VISITNUM, VISIT, VISITDY) "
            "from the SV domain, (6) Derive VSDY/VSDY_D (study day of "
            "measurement relative to first dose), (7) Handle unit "
            "standardization (e.g., Fahrenheit to Celsius if needed, lbs to kg), "
            "(8) Apply variable attributes and create xport output."
        ),
        gold_path="gold/T1.1.sdtm_vs_gen.001/",
        oracle_params={
            "slots": [
                "required_variables[]",
                "testcd_mapping",
                "baseline_flag_logic",
                "unit_standardization",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T1.1.sdtm_lb_gen.001",
        subcategory="T1.1",
        title="Generate SAS program to create SDTM LB domain for laboratory data",
        complexity="complex",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
            "fixtures/04_sdtm/programs/path.R",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#LB",
        prompt=(
            "Write a SAS program to create the SDTM LB (Laboratory) domain "
            "dataset for 54,828 laboratory test records. The program must: "
            "(1) Read raw lab data and transpose to findings structure, "
            "(2) Map LBTESTCD/LBTEST using CDISC controlled terminology for "
            "chemistry, hematology, and urinalysis panels, (3) Standardize "
            "units (LBORRESU → LBSTRESU) and convert values (LBORRES → "
            "LBSTRESC/LBSTRESN) for numeric results, (4) Populate reference "
            "range variables (LBORNRLO, LBORNRHI, LBNRNRLO, LBNRNRHI), "
            "(5) Derive LBSPEC, LBREASND, LBFAST where applicable, "
            "(6) Assign LBSEQ per subject, (7) Handle supplemental qualifiers "
            "(SUPPLB) for lab-specific metadata, (8) Map visit windows from "
            "SV domain, (9) Apply all variable attributes per specification, "
            "(10) Create xport output."
        ),
        gold_path="gold/T1.1.sdtm_lb_gen.001/",
        oracle_params={
            "slots": [
                "required_variables[]",
                "testcd_mapping",
                "unit_conversion_logic",
                "reference_range_handling",
            ],
            "match_mode": "superset",
        },
    ),
    # ── T1.2 ADaM dataset programs ─────────────────────────────────
    _task(
        task_id="T1.2.adam_adsl_gen.001",
        subcategory="T1.2",
        title="Generate R program to derive ADSL from SDTM DM and supplemental domains",
        complexity="complex",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md",
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADSL",
        prompt=(
            "Write an R program using the admiral package to create the ADSL "
            "(Subject-Level Analysis Dataset). The program must: (1) Read SDTM "
            "DM, DS, EX, VS, SC, and SUPPDM xpt datasets, (2) Derive "
            "treatment variables: TRT01P/TRT01PN (planned) and TRT01A/TRT01AN "
            "(actual) from ARMCD/ACTARMCD with mapping Pbo→0, Xan_Lo→54, "
            "Xan_Hi→81, (3) Derive population flags: ITTFL (randomized), "
            "SAFFL (received at least 1 dose), EFFFL (post-baseline efficacy), "
            "COMP24FL (completed Week 24), (4) Derive baseline characteristics: "
            "HEIGHTBL, WEIGHTBL from VS, BMIBL computed, (5) Derive MMSETOT "
            "from QS domain, (6) Derive disposition flags: DISCONFL, DSRAEFL, "
            "EOSSTT from DS, (7) Calculate RFSTDTC/RFENDTC from EX, (8) "
            "Compute treatment duration (TRTDURD), (9) Handle screen failures "
            "(exclude ARMCD='Scrnfail' from ADSL), (10) Apply ADaM variable "
            "attributes and metadata per specification."
        ),
        gold_path="gold/T1.2.adam_adsl_gen.001/",
        oracle_params={
            "slots": [
                "required_variables[]",
                "treatment_derivation",
                "population_flag_logic",
                "baseline_measure_handling",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T1.2.adam_adae_gen.001",
        subcategory="T1.2",
        title="Generate R program to derive ADAE from SDTM AE and ADSL",
        complexity="mixed",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md",
            "fixtures/04_sdtm/SDTM_Specifications.md#AE",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADAE",
        prompt=(
            "Write an R program using admiral to create the ADAE (Adverse "
            "Events Analysis Dataset). The program must: (1) Read SDTM AE "
            "and merge with ADSL for treatment and population variables, "
            "(2) Derive TRTEMFL (treatment-emergent flag): Y if AE start "
            "date >= first dose date (ASTDT >= TRTSDT), (3) Propagate "
            "treatment variables (TRTPN, TRTA, TRTP, TRTA), (4) Calculate "
            "analysis relative days (ASTDY = ASTDT - TRTSDT + 1, AENDY = "
            "AENDT - TRTSDT + 1), (5) Derive analysis severity ASEV (max "
            "severity per AE), (6) Create CQ01NAM for custom query if "
            "specified, (7) Apply ADaM BDS-like variable attributes, (8) "
            "Handle date imputation for partial AESTDTC/AEENDTC values, "
            "(9) Output xpt dataset with proper labels and formats."
        ),
        gold_path="gold/T1.2.adam_adae_gen.001/",
        oracle_params={
            "slots": [
                "required_variables[]",
                "trtemfl_derivation",
                "relative_day_calculation",
                "treatment_propagation",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T1.2.adam_adadas_gen.001",
        subcategory="T1.2",
        title="Generate R program to derive ADADAS with LOCF imputation for primary efficacy",
        complexity="complex",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADADAS",
        prompt=(
            "Write an R program using admiral to create the ADADAS (ADAS-Cog "
            "Analysis Dataset) as a BDS (Basic Data Structure) dataset. The "
            "program must: (1) Read SDTM QS domain and filter for ADAS-Cog "
            "questionnaire (QSCAT='ADAS-COG'), (2) Derive PARAMCD/PARAM: "
            "ACTOT (total score) and ACITM01-ACITM11 (individual items), "
            "(3) Apply visit windowing: Baseline (AWTARGET=0), Week 8 "
            "(56), Week 16 (112), Week 24 (168) with windows AWLO/AWHI, "
            "(4) Compute AVAL (analysis value), BASE (baseline value), "
            "CHG (change from baseline = AVAL - BASE), PCHG (percent change), "
            "(5) Derive ANL01FL (analysis flag) per SAP, (6) Implement LOCF "
            "imputation: carry forward last observation within subject for "
            "missing post-baseline visits, flag with DTYPE='LOCF', "
            "(7) Merge with ADSL for treatment variables and population flags, "
            "(8) Filter to Efficacy population (EFFFL='Y'), (9) Apply ADaM "
            "BDS variable attributes per specification."
        ),
        gold_path="gold/T1.2.adam_adadas_gen.001/",
        oracle_params={
            "slots": [
                "required_variables[]",
                "paramcd_definitions",
                "visit_windowing_logic",
                "locf_imputation",
            ],
            "match_mode": "superset",
        },
    ),
    # ── T1.3 TLF generation programs ───────────────────────────────
    _task(
        task_id="T1.3.tlf_demo_gen.001",
        subcategory="T1.3",
        title="Generate R program for Table 14-1.03 demographics summary by treatment group",
        complexity="mixed",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-1-03_demographic.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADSL",
        ],
        spec="fixtures/06_tlfs/mock_templates/t_mock_14-1-03_demographic.md",
        prompt=(
            "Write an R program using rtables or Tplyr to generate Table "
            "14-1.03: Summary of Demographic and Baseline Characteristics "
            "by treatment group. The program must: (1) Read ADSL dataset, "
            "(2) Filter to ITT population (ITTFL='Y'), (3) Calculate for "
            "each treatment group (Placebo, Xanomeline Low, Xanomeline High) "
            "and total: N (count), (4) For continuous variables (AGE, HEIGHTBL, "
            "WEIGHTBL, BMIBL, MMSETOT): n, mean, SD, median, min, max, "
            "(5) For categorical variables (SEX, RACE, ETHNIC): n (%), "
            "(6) Format table with column headers: Placebo (N=XX), Xan Low "
            "(N=XX), Xan High (N=XX), Total (N=XX), (7) Include mock shell "
            "footnotes, (8) Output as RTF document matching mock shell layout."
        ),
        gold_path="gold/T1.3.tlf_demo_gen.001/",
        oracle_params={
            "slots": [
                "population_filter",
                "continuous_stats",
                "categorical_stats",
                "output_format",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T1.3.tlf_ae_gen.001",
        subcategory="T1.3",
        title="Generate R program for Table 14-4.02 AE by SOC and PT with 5% threshold",
        complexity="complex",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-4-02_ae_by_soc_pt.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADAE",
        ],
        spec="fixtures/06_tlfs/mock_templates/t_mock_14-4-02_ae_by_soc_pt.md",
        prompt=(
            "Write an R program using rtables or Tplyr to generate Table "
            "14-4.02: Adverse Events by System Organ Class and Preferred "
            "Term. The program must: (1) Read ADAE and ADSL datasets, "
            "(2) Filter to Safety population (SAFFL='Y') and treatment-emergent "
            "AEs (TRTEMFL='Y'), (3) For each SOC/PT, count subjects with at "
            "least one AE: n (%), where % denominator is N within treatment "
            "group, (4) Apply 5% threshold: show only PTs where any treatment "
            "group has >= 5% incidence, (5) Sort by SOC frequency (descending), "
            "then PT alphabetically within SOC, (6) Include an 'Any AE' "
            "summary row at top, (7) Format columns: Placebo (N=XX), Xan Low "
            "(N=XX), Xan High (N=XX), (8) Handle MedDRA hierarchy sorting, "
            "(9) Output RTF matching mock shell specifications."
        ),
        gold_path="gold/T1.3.tlf_ae_gen.001/",
        oracle_params={
            "slots": [
                "population_filter",
                "teae_filter",
                "percent_threshold",
                "sorting_logic",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T1.3.tlf_km_gen.001",
        subcategory="T1.3",
        title="Generate R program for Figure 14-5.01 Kaplan-Meier plot with risk table",
        complexity="complex",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/f_mock_14-5-01_km_plot.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADTTE",
        ],
        spec="fixtures/06_tlfs/mock_templates/f_mock_14-5-01_km_plot.md",
        prompt=(
            "Write an R program using ggplot2 and survival packages to "
            "generate Figure 14-5.01: Kaplan-Meier Plot of Time to First "
            "Dermatologic Event. The program must: (1) Read ADTTE and ADSL "
            "datasets, (2) Filter to Safety population (SAFFL='Y'), "
            "(3) Fit Kaplan-Meier survival curves by treatment group using "
            "survfit(Surv(AVAL, 1-CNSR) ~ TRTP), (4) Plot KM curves with "
            "confidence bands (95% CI), (5) Add censoring marks (tick marks "
            "on the curve where censoring occurs), (6) Add risk table below "
            "the plot showing number at risk at each time point, (7) Perform "
            "log-rank test for treatment comparison and report p-value, "
            "(8) Calculate median time-to-event per group with 95% CI, "
            "(9) Format: X-axis (Days Since First Dose), Y-axis (Probability "
            "of No Event), legend with treatment groups, (10) Output as PDF "
            "matching mock shell dimensions and styling."
        ),
        gold_path="gold/T1.3.tlf_km_gen.001/",
        oracle_params={
            "slots": [
                "population_filter",
                "km_model_specification",
                "risk_table_logic",
                "log_rank_test",
            ],
            "match_mode": "superset",
        },
    ),
]

# ── Scale-task parameter lists ───────────────────────────────────────

_SDTM_P: list[tuple] = [
    (
        "cm",
        "CM",
        "Concomitant Medications",
        2982,
        "complex",
        "CMTRT, CMDECOD, CMINDC, CMCLAS, CMROUTE, CMSTDTC, CMENDTC, CMDOSU, CMDOSFRQ",
        "ATC classification mapping, medication coding from verbatim, indication mapping, route of administration, dose frequency standardization",
    ),
    (
        "ds",
        "DS",
        "Disposition",
        562,
        "mixed",
        "DSDECOD, DSTERM, DSCAT, DSSTDTC, DSENDTC, VISIT, VISITNUM",
        "disposition category derivation, standardized disposition terms, completion and discontinuation logic",
    ),
    (
        "ex",
        "EX",
        "Exposure",
        2772,
        "mixed",
        "EXTRT, EXDOSE, EXDOSU, EXROUTE, EXSTDTC, EXENDTC",
        "dose mapping, route of administration, treatment period derivation from dosing records",
    ),
    (
        "mh",
        "MH",
        "Medical History",
        1116,
        "complex",
        "MHTERM, MHDECOD, MHBODSYS, MHSTDTC, MHENDTC, MHCAT",
        "MedDRA coding hierarchy, body system mapping, history category classification, date handling",
    ),
    (
        "qs",
        "QS",
        "Questionnaires",
        30096,
        "complex",
        "QSTESTCD, QSTEST, QSORRES, QSSTRESC, QSSTRESN, VISITNUM",
        "questionnaire mapping for ADAS-Cog and MMSE, test scoring, visit alignment",
    ),
    (
        "sc",
        "SC",
        "Subject Characteristics",
        508,
        "simple",
        "SCTESTCD, SCTEST, SCORRES, SCSTRESC, SCSTRESN",
        "characteristic type mapping, standardized results derivation",
    ),
    (
        "sv",
        "SV",
        "Subject Visits",
        3640,
        "mixed",
        "VISITNUM, VISIT, SVSTDTC, SVENDTC, SVDY",
        "visit derivation from subject elements, visit date handling, study day calculation",
    ),
    (
        "se",
        "SE",
        "Subject Elements",
        5056,
        "simple",
        "ETCD, ELEMENT, SESTDTC, SEENDTC, TAETORD",
        "element assignment from trial design, element date derivation",
    ),
    (
        "relrec",
        "RELREC",
        "Related Records",
        38,
        "mixed",
        "RDOMAIN, USUBJID, IDVAR, IDVARVAL, RELTYPE, RELID",
        "inter-domain relationship identification, RELID assignment, IDVAR mapping",
    ),
    (
        "ta",
        "TA",
        "Trial Arms",
        3,
        "simple",
        "ARMCD, ARM, TAETORD, ETCD, ELEMENT",
        "arm definition, element ordering within treatment arms",
    ),
    (
        "te",
        "TE",
        "Trial Elements",
        3,
        "simple",
        "ETCD, ELEMENT, TESTRL, TEENRL, TEDUR",
        "element definition with start and end rules, duration calculation",
    ),
    (
        "ti",
        "TI",
        "Trial Inclusion/Exclusion",
        21,
        "mixed",
        "TSPARMCD, TSPARM, TSVAL",
        "criterion definitions, parameter coding, value mapping for eligibility criteria",
    ),
    (
        "ts",
        "TS",
        "Trial Summary",
        24,
        "simple",
        "TSPARMCD, TSPARM, TSVAL",
        "trial summary parameters, study-level metadata extraction",
    ),
    (
        "tv",
        "TV",
        "Trial Visits",
        11,
        "simple",
        "VISITNUM, VISIT, VISTPT, VISTPTREF",
        "visit numbering, visit timing reference points",
    ),
    (
        "suppdm",
        "SUPPDM",
        "Supplemental DM",
        558,
        "mixed",
        "RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL",
        "supplemental qualifier structure for DM-specific variables",
    ),
    (
        "suppae",
        "SUPPAE",
        "Supplemental AE",
        1191,
        "mixed",
        "RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL",
        "supplemental qualifier derivation for AE-specific metadata",
    ),
    (
        "suppds",
        "SUPPDS",
        "Supplemental DS",
        466,
        "mixed",
        "RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL",
        "supplemental qualifier derivation for disposition variables",
    ),
    (
        "supplb",
        "SUPPLB",
        "Supplemental LB",
        22152,
        "mixed",
        "RDOMAIN, USUBJID, IDVAR, IDVARVAL, QNAM, QVAL, QLABEL",
        "supplemental qualifier derivation for laboratory metadata",
    ),
]

_ADAM_P: list[tuple] = [
    (
        "adlbc",
        "ADLBC",
        "Laboratory Analysis",
        7778,
        "complex",
        "PARAMCD, AVAL, BASE, CHG, AVALC, ANRIND, BNRIND, SHIFT",
        "PARAMCD derivation from LBTESTCD, baseline computation, change from baseline, reference range indicators, shift analysis flags",
    ),
    (
        "adtte",
        "ADTTE",
        "Time-to-Event Analysis",
        254,
        "complex",
        "PARAMCD, PARAM, AVAL, CNSR, ADT, TRTP, TRTPN",
        "parameter definitions, censoring variable logic, time variable derivation, event date definitions",
    ),
    (
        "adsl_disp",
        "ADSL",
        "Subject-Level (disposition focus)",
        254,
        "mixed",
        "DISCONFL, DSRAEFL, EOSSTT, DCSREAS, TRTDURD",
        "disposition flag derivation, discontinuation reasons, end-of-study status, treatment duration calculation",
    ),
    (
        "adae_cq",
        "ADAE",
        "Adverse Events (custom query)",
        1191,
        "mixed",
        "CQ01NAM, TRTEMFL, ASEV, AREL, ASTDY",
        "custom query derivation, treatment-emergent flag refinement, analysis severity",
    ),
    (
        "adadas_vw",
        "ADADAS",
        "ADAS-Cog (visit windowing)",
        2718,
        "mixed",
        "AWTARGET, AWLO, AWHI, AVISITN, AVISIT",
        "visit windowing rules, AWTARGET/AWLO/AWHI derivation, visit assignment logic",
    ),
    (
        "adlbc_rr",
        "ADLBC",
        "Lab (reference ranges)",
        7778,
        "complex",
        "ANRIND, BNRIND, SHIFT, AVAL, BASE, ATOXGR, BTOXGR",
        "reference range indicator derivation, toxicity grading, shift table variables",
    ),
    (
        "adtte_sub",
        "ADTTE",
        "Time-to-Event (subgroup)",
        254,
        "complex",
        "PARAMCD, AVAL, CNSR, SUBGP, TRTP, ADT",
        "subgroup-specific time-to-event analysis, stratified log-rank, subgroup derivation",
    ),
    (
        "adsl_bl",
        "ADSL",
        "Subject-Level (baseline focus)",
        254,
        "mixed",
        "HEIGHTBL, WEIGHTBL, BMIBL, MMSETOT, AGEGR1",
        "baseline characteristic derivation from VS and QS domains, BMI computation, age grouping",
    ),
    (
        "adae_sev",
        "ADAE",
        "Adverse Events (severity focus)",
        1191,
        "mixed",
        "ASEV, AESEV, TRTEMFL, ASTDY, AENDY",
        "maximum severity derivation per AE, severity analysis, relative day calculations",
    ),
    (
        "adadas_item",
        "ADADAS",
        "ADAS-Cog (item analysis)",
        2718,
        "complex",
        "PARAMCD, ACITM01, ACITM02, ACITM03, ACTOT, AVAL, BASE",
        "individual item parameter derivation, total score computation, item-level change analysis",
    ),
    (
        "adlbc_shift",
        "ADLBC",
        "Lab (shift analysis)",
        7778,
        "complex",
        "SHIFT, ANRIND, BNRIND, AVAL, BASE, PARAMCD",
        "shift from baseline to post-baseline reference range category, shift table derivation",
    ),
    (
        "adtte_cr",
        "ADTTE",
        "Time-to-Event (competing risk)",
        254,
        "complex",
        "PARAMCD, CNSR, EVNTDESC, AVAL, TRTP",
        "competing risk analysis, event type classification, censoring refinement",
    ),
    (
        "adsl_dur",
        "ADSL",
        "Subject-Level (treatment duration)",
        254,
        "mixed",
        "TRTSDT, TRTEDT, TRTDURD, TRT01P, TRT01PN",
        "treatment start/end date derivation from EX, duration computation, treatment variable mapping",
    ),
    (
        "adae_rel",
        "ADAE",
        "Adverse Events (relatedness)",
        1191,
        "mixed",
        "AREL, ARELNUM, TRTEMFL, TRTP, TRTA",
        "causality assessment mapping, relatedness analysis flag, planned vs actual treatment propagation",
    ),
    (
        "adadas_comp",
        "ADADAS",
        "ADAS-Cog (completers)",
        2718,
        "mixed",
        "COMP24FL, ANL01FL, DTYPE, AVISITN",
        "completer population flag, analysis flag for completers, LOCF sensitivity analysis",
    ),
]

_TLF_P: list[tuple] = [
    (
        "primary",
        "14-3.01",
        "Primary Endpoint Analysis",
        "Efficacy",
        "complex",
        "ADADAS",
        "t_mock_14-3-01_primary_endpoint.md",
        "ANCOVA model with treatment, site group, and baseline covariate; LOCF imputation; Type III SS; dose-response trend test; pairwise comparisons with LS means and 95% CI",
    ),
    (
        "ae_overview",
        "14-4.01",
        "AE Overview Summary",
        "Safety",
        "mixed",
        "ADAE",
        "t_mock_14-4-01_ae_overview.md",
        "AE summary counts, TEAE subjects, SAE counts, AE leading to discontinuation, AE by severity",
    ),
    (
        "disposition",
        "14-2.01",
        "Disposition Summary",
        "ITT",
        "mixed",
        "ADSL",
        "t_mock_14-2-01_disposition.md",
        "completion and discontinuation counts by reason and treatment group",
    ),
    (
        "conmed",
        "14-2.02",
        "Concomitant Medications",
        "Safety",
        "complex",
        "ADCM",
        "t_mock_14-2-02_conmed.md",
        "ATC class grouping, medication prevalence by treatment, most common medications",
    ),
    (
        "lab_summary",
        "14-6.01",
        "Laboratory Summary Over Time",
        "Safety",
        "complex",
        "ADLBC",
        "t_mock_14-6-01_lab_summary.md",
        "lab parameters by visit, descriptive statistics, reference range flags",
    ),
    (
        "cfb",
        "14-3.02",
        "Change from Baseline Over Time",
        "Efficacy",
        "mixed",
        "ADADAS",
        "t_mock_14-3-02_cfb.md",
        "visit-wise change from baseline with standard errors, confidence intervals, and treatment comparisons",
    ),
    (
        "exposure",
        "14-2.03",
        "Exposure and Compliance",
        "Safety",
        "mixed",
        "ADSL",
        "t_mock_14-2-03_exposure.md",
        "treatment duration, dose compliance, treatment intensity by group",
    ),
    (
        "responder",
        "14-3.03",
        "Responder Analysis",
        "Efficacy",
        "complex",
        "ADADAS",
        "t_mock_14-3-03_responder.md",
        "responder definition, response rates by treatment group, Cochran-Mantel-Haenszel test",
    ),
    (
        "shift",
        "14-6.02",
        "Laboratory Shift Table",
        "Safety",
        "complex",
        "ADLBC",
        "t_mock_14-6-02_shift.md",
        "reference range shifts from baseline to post-baseline, high/low/normal transitions",
    ),
    (
        "medhist",
        "14-1.04",
        "Medical History Summary",
        "ITT",
        "mixed",
        "ADMH",
        "t_mock_14-1-04_medhist.md",
        "SOC/PT prevalence, system organ class grouping, most common medical conditions",
    ),
    (
        "ecg",
        "14-6.03",
        "ECG Parameters Listing",
        "Safety",
        "mixed",
        "ADEC",
        "t_mock_14-6-03_ecg.md",
        "ECG intervals, QTc changes from baseline, categorical analysis by treatment",
    ),
    (
        "screen",
        "14-1.01",
        "Screening Summary",
        "All Screened",
        "simple",
        "ADSL",
        "t_mock_14-1-01_screen.md",
        "screening counts, screen failure reasons, enrollment summary",
    ),
    (
        "protocol_dev",
        "14-1.02",
        "Protocol Deviations",
        "ITT",
        "mixed",
        "ADSL",
        "t_mock_14-1-02_deviation.md",
        "deviation categories by treatment group, important vs minor deviations",
    ),
    (
        "forest",
        "14-5.02",
        "Forest Plot (Subgroup)",
        "Efficacy",
        "complex",
        "ADADAS",
        "f_mock_14-5-02_forest.md",
        "subgroup analysis forest plot, treatment-by-subgroup interaction, odds ratios with 95% CI",
    ),
    (
        "visit_comp",
        "14-2.04",
        "Visit Compliance",
        "ITT",
        "mixed",
        "ADSL",
        "t_mock_14-2-04_visit.md",
        "visit completion rates by treatment, early termination patterns, visit window compliance",
    ),
    (
        "safety_sum",
        "14-4.03",
        "Safety Summary Dashboard",
        "Safety",
        "complex",
        "ADAE",
        "t_mock_14-4-03_safety.md",
        "overall safety profile, key AE categories, lab abnormality summary",
    ),
    (
        "ae_severity",
        "14-4.04",
        "AE by Maximum Severity",
        "Safety",
        "mixed",
        "ADAE",
        "t_mock_14-4-04_severity.md",
        "severity distribution by treatment, worst-case severity per subject, grade analysis",
    ),
]


# ── Scale-task gold template functions ────────────────────────────────


def _sdtm_gold_t(
    domain: str, DOMAIN: str, label: str, key_vars: str, records: int
) -> str:
    """Return a SAS gold-program template for an SDTM scale task."""
    return f"""/* ================================================================
   SDTM {DOMAIN} Domain Creation Program
   Study: CDISCPilot01
   Domain: {DOMAIN} ({label})
   Standard: SDTM IG v3.1.2
   ================================================================ */

libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

data work.{domain}_raw;
    set raw.{domain};
run;

proc sort data=work.{domain}_raw; by USUBJID; run;

data sdtm.{domain};
    length STUDYID $12 DOMAIN $2 USUBJID $11 {DOMAIN}SEQ 8;

    retain {DOMAIN}SEQ;
    by USUBJID;

    STUDYID = "&studyid";
    DOMAIN  = "{DOMAIN}";

    if first.USUBJID then {DOMAIN}SEQ = 0;
    {DOMAIN}SEQ = {DOMAIN}SEQ + 1;

    /* Domain-specific variable mappings for {label} */
    /* {key_vars} */

    keep STUDYID DOMAIN USUBJID {DOMAIN}SEQ {key_vars};
run;

proc datasets library=sdtm nolist;
    modify {domain};
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              {DOMAIN}SEQ = "Sequence Number";
run; quit;

proc export data=sdtm.{domain}
    outfile="path/to/output/{domain}.xpt"
    dbms=xport replace;
run;
"""


def _adam_gold_t(
    name: str, DATASET: str, label: str, key_vars: str, records: int
) -> str:
    """Return an R gold-program template for an ADaM scale task."""
    lower = DATASET.lower()
    return f"""# ================================================================
# {DATASET} ({label}) Creation Program
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

# --- Derive {DATASET} key variables ---
# Key variables: {key_vars}
# Records: {records}

# --- Apply ADaM metadata ---
write_xpt({lower}, path = "path/to/output/{lower}.xpt")
"""


def _tlf_gold_t(
    name: str, tlf_id: str, title: str, population: str, data_source: str
) -> str:
    """Return an R gold-program template for a TLF scale task."""
    return f"""# ================================================================
# {tlf_id}: {title}
# Study: CDISCPilot01
# Population: {population}
# ================================================================

library(rtables)
library(haven)
library(dplyr)

# --- Read {data_source} ---
data <- read_xpt("path/to/adam/{data_source}.xpt") %>%
  filter(...)

# --- Build table ---
lyt <- basic_table(show_colcounts = TRUE) %>%
  split_cols_by("TRT01P")

tbl <- build_table(lyt, data)

# --- Export RTF ---
as_rtf(tbl, file = "path/to/output/tlf-{name}.rtf")
"""


# ── Scale-task builder ────────────────────────────────────────────────


def _build_scale() -> tuple[list[dict], dict[str, str]]:
    """Build SCALE_TASKS and SCALE_GOLD from parameter lists."""
    tasks: list[dict] = []
    golds: dict[str, str] = {}
    idx = 2  # start at .002 so first scale task follows .001 originals

    # T1.1 SDTM
    for domain, DOMAIN, label, records, complexity, key_vars_str, focus in _SDTM_P:
        tid = f"T1.1.sdtm_{domain}_gen.{idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T1.1",
                title=f"Generate SAS program to create SDTM {DOMAIN} ({label}) domain",
                complexity=complexity,
                fixtures=[
                    "fixtures/04_sdtm/SDTM_Specifications.md",
                    "fixtures/04_sdtm/programs/path.R",
                ],
                spec=f"fixtures/04_sdtm/SDTM_Specifications.md#{DOMAIN}",
                prompt=(
                    f"Write a SAS program to create the SDTM {DOMAIN} ({label}) "
                    f"domain dataset. The program must: (1) Read raw {label.lower()} data, "
                    f"(2) Derive USUBJID and {DOMAIN}SEQ (sequential numbering per subject), "
                    f"(3) Map key variables: {key_vars_str}, "
                    f"(4) Handle {focus}, "
                    f"(5) Apply variable attributes per SDTM specification, "
                    f"(6) Create a permanent SAS dataset with xport format. "
                    f"The dataset contains approximately {records} records."
                ),
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "required_variables[]",
                        f"{domain}_variable_mapping",
                        f"{domain}_derivation_logic",
                        "output_format",
                    ],
                    "match_mode": "superset",
                },
            )
        )
        golds[tid] = _sdtm_gold_t(domain, DOMAIN, label, key_vars_str, records)
        idx += 1

    # T1.2 ADaM
    for name, DATASET, label, records, complexity, key_vars_str, focus in _ADAM_P:
        tid = f"T1.2.adam_{name}_gen.{idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T1.2",
                title=f"Generate R program to derive {DATASET} ({label})",
                complexity=complexity,
                fixtures=[
                    "fixtures/05_adam/ADaM_Specifications.md",
                    "fixtures/04_sdtm/SDTM_Specifications.md",
                ],
                spec=f"fixtures/05_adam/ADaM_Specifications.md#{DATASET}",
                prompt=(
                    f"Write an R program using the admiral package to create the {DATASET} "
                    f"({label}) analysis dataset. The program must: (1) Read relevant SDTM "
                    f"source datasets and merge with ADSL, (2) Derive key variables: "
                    f"{key_vars_str}, (3) Handle {focus}, "
                    f"(4) Apply ADaM variable attributes and metadata per specification, "
                    f"(5) Output xpt dataset with proper labels. "
                    f"The dataset contains approximately {records} records."
                ),
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "required_variables[]",
                        f"{name}_derivation_logic",
                        f"{name}_key_mappings",
                        "output_format",
                    ],
                    "match_mode": "superset",
                },
            )
        )
        golds[tid] = _adam_gold_t(name, DATASET, label, key_vars_str, records)
        idx += 1

    # T1.3 TLF
    for (
        name,
        tlf_id,
        title,
        population,
        complexity,
        data_source,
        mock_file,
        focus,
    ) in _TLF_P:
        tid = f"T1.3.tlf_{name}_gen.{idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T1.3",
                title=f"Generate R program for {tlf_id} {title}",
                complexity=complexity,
                fixtures=[
                    f"fixtures/06_tlfs/mock_templates/{mock_file}",
                    f"fixtures/05_adam/ADaM_Specifications.md#{data_source}",
                ],
                spec=f"fixtures/06_tlfs/mock_templates/{mock_file}",
                prompt=(
                    f"Write an R program using rtables or Tplyr to generate {tlf_id}: "
                    f"{title}. The program must: (1) Read {data_source} dataset, "
                    f"(2) Filter to {population} population, (3) Implement analysis: "
                    f"{focus}, "
                    f"(4) Format table with treatment group columns "
                    f"(Placebo, Xanomeline Low, Xanomeline High), "
                    f"(5) Output as RTF document matching mock shell layout."
                ),
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "population_filter",
                        f"{name}_analysis_logic",
                        "table_structure",
                        "output_format",
                    ],
                    "match_mode": "superset",
                },
            )
        )
        golds[tid] = _tlf_gold_t(name, tlf_id, title, population, data_source)
        idx += 1

    return tasks, golds


SCALE_TASKS, SCALE_GOLD = _build_scale()

# ── Gold outputs (reference SAS/R programs) ──────────────────────────

GOLD_OUTPUTS: dict[str, str] = {
    "T1.1.sdtm_dm_gen.001": """/* ================================================================
   SDTM DM Domain Creation Program
   Study: CDISCPilot01
   Domain: DM (Demographics)
   Standard: SDTM IG v3.1.2
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw demographics data --- */
data work.dm_raw;
    set raw.dm;
run;

/* --- Derive SDTM DM variables --- */
data sdtm.dm;
    length STUDYID $12 DOMAIN $2 USUBJID $11 SUBJID $4 SITEID $2
           RFICDTC $20 RFXSTDTC $20 ARMCD $8 ARM $40
           ACTARMCD $8 ACTARM $40 AGE 8 AGEU $10
           SEX $2 RACE $40 ETHNIC $22 COUNTRY $3;

    /* Core identifiers */
    STUDYID = "&studyid";
    DOMAIN  = "DM";

    /* Derive USUBJID: concatenation of STUDYID-SITEID-SUBJID */
    USUBJID = cats(STUDYID, "-", SITEID, "-", SUBJID);

    /* Treatment arm mapping from randomization */
    select (ARMCD_RAW);
        when ("Pbo")    do; ARMCD = "Pbo";    ARM = "Placebo"; end;
        when ("Xan_Lo") do; ARMCD = "Xan_Lo"; ARM = "Xanomeline Low Dose"; end;
        when ("Xan_Hi") do; ARMCD = "Xan_Hi"; ARM = "Xanomeline High Dose"; end;
        when ("Scrnfail") do; ARMCD = "Scrnfail"; ARM = "Screen Failure"; end;
        otherwise do; ARMCD = ""; ARM = ""; end;
    end;

    /* Actual arm = planned arm unless early discontinuation */
    ACTARMCD = ARMCD;
    ACTARM   = ARM;

    /* Age from birth date and reference date */
    AGE = int(yrdif(BRTHDTC, RFICDTC, 'ACTUAL'));

    AGEU = "YEARS";

    /* Demographics from CRF */
    SEX    = SEX_RAW;
    RACE   = RACE_RAW;
    ETHNIC = ETHNIC_RAW;

    /* Country derived from site */
    COUNTRY = "US";

    /* Dates */
    RFICDTC  = put(consent_dt, is8601da.);
    RFXSTDTC = put(first_dose_dt, is8601da.);

    /* Keep only required variables */
    keep STUDYID DOMAIN USUBJID SUBJID SITEID
         RFICDTC RFXSTDTC ARMCD ARM ACTARMCD ACTARM
         AGE AGEU SEX RACE ETHNIC COUNTRY RFICDEC;
run;

/* --- Apply variable labels --- */
proc datasets library=sdtm nolist;
    modify dm;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              SUBJID   = "Subject Identifier for the Study"
              SITEID   = "Study Site Identifier"
              RFICDTC  = "Date/Time of Informed Consent"
              RFXSTDTC = "Date/Time of First Study Treatment"
              ARMCD    = "Planned Arm Code"
              ARM      = "Description of Planned Arm"
              ACTARMCD = "Actual Arm Code"
              ACTARM   = "Description of Actual Arm"
              AGE      = "Age"
              AGEU     = "Age Units"
              SEX      = "Sex"
              RACE     = "Race"
              ETHNIC   = "Ethnicity"
              COUNTRY  = "Country";
run; quit;

/* --- Export to transport file --- */
proc export data=sdtm.dm
    outfile="path/to/output/dm.xpt"
    dbms=xport replace;
run;
""",
    "T1.1.sdtm_ae_gen.001": """/* ================================================================
   SDTM AE Domain Creation Program
   Study: CDISCPilot01
   Domain: AE (Adverse Events)
   Standard: SDTM IG v3.1.2, MedDRA v8.0
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw adverse event data --- */
data work.ae_raw;
    set raw.ae;
run;

/* --- Derive SDTM AE variables --- */
proc sort data=work.ae_raw; by USUBJID AESTDTC; run;

data sdtm.ae;
    length STUDYID $12 DOMAIN $2 USUBJID $11 AESEQ 8
           AETERM $100 AELLT $100 AEDECOD $100
           AEHLT $100 AEHLGT $100 AEBODSYS $100
           AESEV $20 AESER $1 AEACN $30 AEREL $20
           AEOUT $30 AESTDTC $20 AEENDTC $20;

    retain AESEQ;
    by USUBJID AESTDTC;

    /* Core identifiers */
    STUDYID = "&studyid";
    DOMAIN  = "AE";

    /* Sequence number per subject */
    if first.USUBJID then AESEQ = 0;
    AESEQ = AESEQ + 1;

    /* Reported term from CRF */
    AETERM = strip(AETERM_RAW);

    /* MedDRA coding hierarchy (v8.0) */
    AELLT   = strip(LLT_RAW);
    AEDECOD = strip(PT_RAW);
    AEHLT   = strip(HLT_RAW);
    AEHLGT  = strip(HLGT_RAW);
    AEBODSYS = strip(SOC_RAW);

    /* Severity from CRF */
    AESEV = strip(AESEV_RAW);

    /* Seriousness flag: derived from seriousness criteria */
    if AESCAN_RAW = "Y" or AESCONG_RAW = "Y" or AESDEATH_RAW = "Y"
       or AESHOSP_RAW = "Y" or AESLIFE_RAW = "Y" or AESOD_RAW = "Y"
    then AESER = "Y";
    else AESER = "N";

    /* Action taken, causality, outcome from CRF */
    AEACN = strip(AEACN_RAW);
    AEREL = strip(AEREL_RAW);
    AEOUT = strip(AEOUT_RAW);

    /* Dates in ISO 8601 format */
    AESTDTC = strip(put(AESTDT, is8601da.));
    AEENDTC = strip(put(AEENDT, is8601da.));

    keep STUDYID DOMAIN USUBJID AESEQ AETERM AELLT AEDECOD
         AEHLT AEHLGT AEBODSYS AESEV AESER AEACN AEREL
         AEOUT AESTDTC AEENDTC AESCAN AESCONG AESDEATH
         AESHOSP AESLIFE AESOD;
run;

/* --- Apply variable labels --- */
proc datasets library=sdtm nolist;
    modify ae;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              AESEQ    = "Sequence Number"
              AETERM   = "Reported Term for the Adverse Event"
              AELLT    = "Lowest Level Term"
              AEDECOD  = "Dictionary-Derived Term"
              AEHLT    = "High Level Term"
              AEHLGT   = "High Level Group Term"
              AEBODSYS = "Body System or Organ Class"
              AESEV    = "Severity/Intensity"
              AESER    = "Serious Event"
              AEACN    = "Action Taken with Study Treatment"
              AEREL    = "Causality"
              AEOUT    = "Outcome of Adverse Event"
              AESTDTC  = "Start Date/Time of Adverse Event"
              AEENDTC  = "End Date/Time of Adverse Event";
run; quit;

/* --- Export to transport file --- */
proc export data=sdtm.ae
    outfile="path/to/output/ae.xpt"
    dbms=xport replace;
run;
""",
    "T1.1.sdtm_vs_gen.001": """/* ================================================================
   SDTM VS Domain Creation Program
   Study: CDISCPilot01
   Domain: VS (Vital Signs)
   Standard: SDTM IG v3.1.2
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw vital signs data (wide format) --- */
data work.vs_raw;
    set raw.vs;
run;

/* --- Transpose to long format (one row per test per visit) --- */
proc transpose data=work.vs_raw out=vs_long prefix=V;
    by USUBJID VISIT VISITNUM VISITDY;
    var HEIGHT WEIGHT DIABP SYSBP PULSE TEMP;
run;

/* --- Map test codes and standardize --- */
data work.vs_mapped;
    set vs_long;
    length VSTESTCD $8 VSTEST $40 VSORRES $20 VSORRESU $10
           VSSTRESC $20 VSSTRESN 8 VSSTRESU $10 VSBLFL $1
           VSDY 8 VSDY_D 8;

    /* Determine test code from transposed variable name */
    VSTESTCD = scan(_NAME_, 1, "_");

    select (VSTESTCD);
        when ("HEIGHT")
            do; VSTEST = "Height"; VSORRESU = "cm"; VSSTRESU = "cm"; end;
        when ("WEIGHT")
            do; VSTEST = "Weight"; VSORRESU = "kg"; VSSTRESU = "kg"; end;
        when ("DIABP")
            do; VSTEST = "Diastolic Blood Pressure"; VSORRESU = "mmHg"; VSSTRESU = "mmHg"; end;
        when ("SYSBP")
            do; VSTEST = "Systolic Blood Pressure"; VSORRESU = "mmHg"; VSSTRESU = "mmHg"; end;
        when ("PULSE")
            do; VSTEST = "Pulse Rate"; VSORRESU = "BEATS/MIN"; VSSTRESU = "BEATS/MIN"; end;
        when ("TEMP")
            do; VSTEST = "Temperature"; VSORRESU = "C"; VSSTRESU = "C"; end;
        otherwise;
    end;

    /* Original and standardized results */
    VSORRES  = strip(put(COL1, best12.));
    VSSTRESC = strip(put(COL1, best12.));
    VSSTRESN = input(strip(put(COL1, best12.)), 8.);

    /* Baseline flag: last measurement before first dose */
    if VISITDY <= 0 then VSBLFL = "Y";
    else VSBLFL = "";

    keep USUBJID VISIT VISITNUM VISITDY VSTESTCD VSTEST
         VSORRES VSORRESU VSSTRESC VSSTRESN VSSTRESU VSBLFL;
run;

/* --- Create final SDTM VS dataset --- */
proc sort data=work.vs_mapped; by USUBJID VSTESTCD VISITNUM; run;

data sdtm.vs;
    length STUDYID $12 DOMAIN $2 USUBJID $11 VSSEQ 8;
    set work.vs_mapped;
    by USUBJID VSTESTCD VISITNUM;

    retain VSSEQ;
    if first.USUBJID then VSSEQ = 0;
    VSSEQ = VSSEQ + 1;

    STUDYID = "&studyid";
    DOMAIN  = "VS";

    /* Study day relative to first dose */
    VSDY = VISITDY;
run;

/* --- Apply labels and export --- */
proc datasets library=sdtm nolist;
    modify vs;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              VSSEQ    = "Sequence Number"
              VSTESTCD = "Vital Signs Test Short Name"
              VSTEST   = "Vital Signs Test Name"
              VSORRES  = "Result in Original Units"
              VSORRESU = "Original Units"
              VSSTRESC = "Character Result in Standard Units"
              VSSTRESN = "Numeric Result in Standard Units"
              VSSTRESU = "Standard Units"
              VSBLFL   = "Baseline Flag"
              VISIT    = "Visit Name"
              VISITNUM = "Visit Number"
              VSDY     = "Study Day of Vital Signs";
run; quit;

proc export data=sdtm.vs
    outfile="path/to/output/vs.xpt"
    dbms=xport replace;
run;
""",
    "T1.1.sdtm_lb_gen.001": """/* ================================================================
   SDTM LB Domain Creation Program
   Study: CDISCPilot01
   Domain: LB (Laboratory Test Results)
   Standard: SDTM IG v3.1.2
   ================================================================ */

/* --- Setup --- */
libname raw "path/to/raw/data" access=readonly;
libname sdtm "path/to/sdtm/output";
%let studyid = CDISCPilot01;

/* --- Read raw lab data --- */
data work.lb_raw;
    set raw.lb;
run;

/* --- Map test codes and standardize units --- */
data work.lb_mapped;
    set work.lb_raw;

    length LBTESTCD $8 LBTEST $40 LBORRES $20 LBORRESU $10
           LBSTRESC $20 LBSTRESN 8 LBSTRESU $10
           LBORNRLO 8 LBORNRHI 8 LBNRNRLO 8 LBNRNRHI 8;

    /* CDISC controlled terminology mapping */
    select (LBTEST_RAW);
        when ("Sodium")       LBTESTCD = "SODIUM";
        when ("Potassium")    LBTESTCD = "K";
        when ("Chloride")     LBTESTCD = "CL";
        when ("Glucose")      LBTESTCD = "GLUC";
        when ("BUN")          LBTESTCD = "BUN";
        when ("Creatinine")   LBTESTCD = "CREAT";
        when ("Albumin")      LBTESTCD = "ALB";
        when ("Total Protein") LBTESTCD = "TP";
        when ("ALT")          LBTESTCD = "ALT";
        when ("AST")          LBTESTCD = "AST";
        when ("Alkaline Phos") LBTESTCD = "ALKPH";
        when ("Total Bilirubin") LBTESTCD = "BILI";
        when ("Hemoglobin")   LBTESTCD = "HGB";
        when ("WBC")          LBTESTCD = "WBC";
        when ("Platelet Count") LBTESTCD = "PLAT";
        otherwise LBTESTCD = "OTHER";
    end;

    LBTEST   = LBTEST_RAW;
    LBORRES  = strip(put(RESULT_RAW, best12.));
    LBORRESU = strip(UNIT_RAW);

    /* Standardize numeric results */
    LBSTRESC = strip(put(RESULT_RAW, best12.));
    LBSTRESN = RESULT_RAW;
    LBSTRESU = strip(UNIT_STD);

    /* Reference ranges */
    LBORNRLO = REF_LO_RAW;
    LBORNRHI = REF_HI_RAW;
    LBNRNRLO = REF_LO_STD;
    LBNRNRHI = REF_HI_STD;

    keep USUBJID VISIT VISITNUM LBTESTCD LBTEST LBORRES LBORRESU
         LBSTRESC LBSTRESN LBSTRESU LBORNRLO LBORNRHI
         LBNRNRLO LBNRNRHI LBSPEC LBREASND LBFAST;
run;

/* --- Assign sequence numbers --- */
proc sort data=work.lb_mapped; by USUBJID LBTESTCD VISITNUM; run;

data sdtm.lb;
    length STUDYID $12 DOMAIN $2 USUBJID $11 LBSEQ 8;
    set work.lb_mapped;
    by USUBJID LBTESTCD VISITNUM;

    retain LBSEQ;
    if first.USUBJID then LBSEQ = 0;
    LBSEQ = LBSEQ + 1;

    STUDYID = "&studyid";
    DOMAIN  = "LB";
run;

/* --- Labels and export --- */
proc datasets library=sdtm nolist;
    modify lb;
        label STUDYID  = "Study Identifier"
              DOMAIN   = "Domain Abbreviation"
              USUBJID  = "Unique Subject Identifier"
              LBSEQ    = "Sequence Number"
              LBTESTCD = "Lab Test Short Name"
              LBTEST   = "Lab Test Name"
              LBORRES  = "Result in Original Units"
              LBORRESU = "Original Units"
              LBSTRESC = "Character Result in Standard Format"
              LBSTRESN = "Numeric Result in Standard Units"
              LBSTRESU = "Standard Units"
              LBORNRLO = "Reference Range Lower Limit (Original)"
              LBORNRHI = "Reference Range Upper Limit (Original)"
              LBNRNRLO = "Reference Range Lower Limit (Standard)"
              LBNRNRHI = "Reference Range Upper Limit (Standard)";
run; quit;

proc export data=sdtm.lb
    outfile="path/to/output/lb.xpt"
    dbms=xport replace;
run;
""",
    "T1.2.adam_adsl_gen.001": """# ================================================================
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
""",
    "T1.2.adam_adae_gen.001": """# ================================================================
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
ae   <- read_xpt("path/to/sdtm/ae.xpt")
adsl <- read_xpt("path/to/adam/adsl.xpt")

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
  xportr_type(path = "path/to/adam_spec.xlsx", domain = "ADAE") %>%
  xportr_label(path = "path/to/adam_spec.xlsx", domain = "ADAE")

write_xpt(adae, path = "path/to/output/adae.xpt")
""",
    "T1.2.adam_adadas_gen.001": """# ================================================================
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
qs   <- read_xpt("path/to/sdtm/qs.xpt")
adsl <- read_xpt("path/to/adam/adsl.xpt")

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
  xportr_type(path = "path/to/adam_spec.xlsx", domain = "ADADAS") %>%
  xportr_label(path = "path/to/adam_spec.xlsx", domain = "ADADAS")

write_xpt(adadas, path = "path/to/output/adadas.xpt")
""",
    "T1.3.tlf_demo_gen.001": """# ================================================================
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
""",
    "T1.3.tlf_ae_gen.001": """# ================================================================
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
""",
    "T1.3.tlf_km_gen.001": """# ================================================================
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
""",
}

# ── Main ─────────────────────────────────────────────────────────────


def main() -> None:
    TASKS_DIR.mkdir(parents=True, exist_ok=True)
    all_tasks = TASKS + SCALE_TASKS
    all_gold = {**GOLD_OUTPUTS, **SCALE_GOLD}

    for task_def in all_tasks:
        tid = task_def["task_id"]
        task_file = TASKS_DIR / f"{tid}.json"
        task_file.write_text(json.dumps(task_def, indent=2) + "\n", encoding="utf-8")
        print(f"  wrote {task_file}")

        gold_dir = GOLD_ROOT / tid
        gold_dir.mkdir(parents=True, exist_ok=True)
        gold_data = all_gold[tid]
        ext = ".sas" if gold_data.lstrip().startswith("/*") else ".R"
        gold_file = gold_dir / f"expected_output{ext}"
        gold_file.write_text(gold_data + "\n", encoding="utf-8")
        print(f"  wrote {gold_file}")

    print(f"\nGenerated {len(all_tasks)} T1 tasks in {TASKS_DIR}")
    print(f"Gold outputs in {GOLD_ROOT}")


if __name__ == "__main__":
    main()
