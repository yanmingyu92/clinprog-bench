"""Generate T3 (spec_extract) benchmark tasks from eSubmission-Benchmark substrate.

Creates 50 task JSON files under tasks/T3_spec/ and corresponding gold
outputs under gold/<task_id>/.

Usage:
    python scripts/build_T3.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks" / "T3_spec"
GOLD_ROOT = ROOT / "gold"

SEED_REPO = "anonymous/eSubmission-Benchmark"
SEED_COMMIT = "658fcc05506b169a27dee6e2c3a1ccdaaf64a716"
DERIVATION_SCRIPT = "scripts/build_T3.py"

# ── Shared building blocks ──────────────────────────────────────────


def _provenance() -> dict:
    return {
        "seed_repo": SEED_REPO,
        "seed_commit": SEED_COMMIT,
        "derivation_script": DERIVATION_SCRIPT,
        "human_authors": ["R01"],
        "human_reviewers": ["R03"],
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
        "category": "T3",
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
            "kind": "json",
            "gold_path": gold_path,
            "oracle": {"type": "slot_fill", "params": oracle_params},
        },
        "scoring": {"scorer": "spec_extract", "weight": 1.0},
        "leakage_audit": {"fixture_sha256_overlap": False, "prompt_ngram_hits": 0},
    }


# ── Task definitions ────────────────────────────────────────────────

TASKS: list[dict] = [
    # ── T3.1 SDTM spec extraction ────────────────────────────────
    _task(
        task_id="T3.1.sdtm_dm_extract.001",
        subcategory="T3.1",
        title="Extract SDTM DM domain variable-level metadata from specification",
        complexity="simple",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#DM",
        prompt=(
            "Extract all variable-level metadata for the SDTM DM (Demographics) "
            "domain from the specification file. For each variable, return: "
            "variable_name, type (Char/Num), length, label, origin "
            "(CRF/Derived/Assigned), and any controlled terminology or codelist "
            "reference. Return as a JSON object with a 'variables' array."
        ),
        gold_path="gold/T3.1.sdtm_dm_extract.001/",
        oracle_params={
            "slots": [
                "variables[].variable_name",
                "variables[].type",
                "variables[].label",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T3.1.sdtm_ae_extract.001",
        subcategory="T3.1",
        title="Extract SDTM AE domain variable metadata and controlled terminology",
        complexity="complex",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#AE",
        prompt=(
            "Extract the SDTM AE (Adverse Events) domain variable metadata. "
            "For each variable provide: variable_name, type, length, label, "
            "origin, and controlled terminology notes (especially MedDRA "
            "coding fields: AELLT, AEDECOD, AEHLT, AEHLGT, AEBODSYS). "
            "Return as a JSON object with 'variables' array."
        ),
        gold_path="gold/T3.1.sdtm_ae_extract.001/",
        oracle_params={
            "slots": [
                "variables[].variable_name",
                "variables[].type",
                "variables[].label",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T3.1.sdtm_ex_extract.001",
        subcategory="T3.1",
        title="Extract SDTM EX domain exposure variable metadata",
        complexity="mixed",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#EX",
        prompt=(
            "Extract the SDTM EX (Exposure) domain variable metadata. Focus "
            "on dose-related variables (EXDOSE, EXDOSU, EXDOSFRM), route "
            "(EXROUTE), and date variables (EXSTDTC, EXENDTC). For each "
            "variable return: variable_name, type, length, label, origin. "
            "Return as a JSON object with 'variables' array."
        ),
        gold_path="gold/T3.1.sdtm_ex_extract.001/",
        oracle_params={
            "slots": [
                "variables[].variable_name",
                "variables[].type",
                "variables[].label",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T3.1.sdtm_lb_extract.001",
        subcategory="T3.1",
        title="Extract SDTM LB domain laboratory test variable metadata",
        complexity="complex",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#LB",
        prompt=(
            "Extract the SDTM LB (Laboratory) domain variable metadata. "
            "This domain contains 54,828 records. For each variable return: "
            "variable_name, type, length, label, origin. Pay special "
            "attention to LBTESTCD, LBORRES, LBORRESU, LBSTRESC, "
            "LBSTRESN, LBSTRESU, and reference range variables. Return "
            "as a JSON object with 'variables' array."
        ),
        gold_path="gold/T3.1.sdtm_lb_extract.001/",
        oracle_params={
            "slots": [
                "variables[].variable_name",
                "variables[].type",
                "variables[].label",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T3.1.sdtm_domain_list.001",
        subcategory="T3.1",
        title="Extract complete SDTM domain inventory with record counts and classes",
        complexity="simple",
        fixtures=[
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md",
        prompt=(
            "Extract the complete inventory of all 22 SDTM domains from the "
            "specification. For each domain return: domain_code (e.g., DM, AE), "
            "domain_label, cdisc_class (e.g., Special Purpose, Events, "
            "Interventions, Findings, Trial Design), record_count, and "
            "filename. Return as a JSON object with 'domains' array."
        ),
        gold_path="gold/T3.1.sdtm_domain_list.001/",
        oracle_params={
            "slots": [
                "domains[].domain_code",
                "domains[].cdisc_class",
                "domains[].record_count",
            ],
            "match_mode": "exact",
        },
    ),
    # ── T3.2 ADaM spec extraction ────────────────────────────────
    _task(
        task_id="T3.2.adam_adsl_extract.001",
        subcategory="T3.2",
        title="Extract ADSL analysis dataset key variable metadata and derivation logic",
        complexity="complex",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADSL",
        prompt=(
            "Extract the ADSL (Subject-Level Analysis Dataset) key variable "
            "metadata. Focus on: treatment variables (TRT01PN, TRT01P, "
            "TRT01AN, TRT01A), population flags (ITTFL, SAFFL, EFFFL, "
            "COMP24FL), baseline measures (HEIGHTBL, WEIGHTBL, BMIBL, "
            "MMSETOT), and disposition (DISCONFL, DSRAEFL, EOSSTT). For "
            "each variable return: variable_name, type, length, label, "
            "origin, derivation_notes. Return as JSON with 'variables' array."
        ),
        gold_path="gold/T3.2.adam_adsl_extract.001/",
        oracle_params={
            "slots": [
                "variables[].variable_name",
                "variables[].type",
                "variables[].derivation_notes",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T3.2.adam_adadas_extract.001",
        subcategory="T3.2",
        title="Extract ADADAS derivation parameters and visit windowing rules",
        complexity="complex",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADADAS",
        prompt=(
            "Extract the ADADAS (ADAS-Cog Analysis Dataset) derivation "
            "parameters. Focus on: PARAMCD definitions (ACTOT and ACITM01-11), "
            "visit windowing rules (AWTARGET, AWLO, AWHI for Baseline, "
            "Week 8, Week 16, Week 24), LOCF handling (DTYPE), analysis "
            "flag (ANL01FL), and variable derivation (AVAL, BASE, CHG, PCHG). "
            "Return as JSON with 'parameters' and 'visit_windows' arrays."
        ),
        gold_path="gold/T3.2.adam_adadas_extract.001/",
        oracle_params={
            "slots": [
                "parameters[].paramcd",
                "parameters[].description",
                "visit_windows[].visit",
                "visit_windows[].awtarget",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T3.2.adam_adae_extract.001",
        subcategory="T3.2",
        title="Extract ADAE analysis variables including treatment-emergent flag logic",
        complexity="mixed",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADAE",
        prompt=(
            "Extract the ADAE (Adverse Events Analysis Dataset) key variable "
            "metadata. Focus on: treatment-emergent flag (TRTEMFL) derivation "
            "logic, analysis treatment variables (TRTPN, TRTA), relative day "
            "calculations (ASTDY, AENDY), and severity/seriousness flags. "
            "For each variable return: variable_name, type, label, "
            "derivation_notes. Return as JSON with 'variables' array."
        ),
        gold_path="gold/T3.2.adam_adae_extract.001/",
        oracle_params={
            "slots": ["variables[].variable_name", "variables[].derivation_notes"],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T3.2.adam_adtte_extract.001",
        subcategory="T3.2",
        title="Extract ADTTE time-to-event parameter definitions and censoring rules",
        complexity="mixed",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADTTE",
        prompt=(
            "Extract the ADTTE (Time-to-Event Analysis Dataset) parameter "
            "definitions. Focus on: PARAMCD values, PARAM descriptions, "
            "censoring variable (CNSR) logic, time variable (AVAL) derivation, "
            "start date (ADT) and event date definitions, and treatment "
            "variables. Return as JSON with 'parameters' array."
        ),
        gold_path="gold/T3.2.adam_adtte_extract.001/",
        oracle_params={
            "slots": [
                "parameters[].paramcd",
                "parameters[].param",
                "parameters[].cnsr_logic",
            ],
            "match_mode": "exact",
        },
    ),
    # ── T3.3 Study metadata extraction ───────────────────────────
    _task(
        task_id="T3.3.study_design_meta.001",
        subcategory="T3.3",
        title="Extract study design metadata from clinical trial protocol",
        complexity="mixed",
        fixtures=[
            "fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        spec="fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
        prompt=(
            "Extract key study design metadata from the clinical trial "
            "protocol. Return: study_id, phase, indication, treatment_name, "
            "treatment_route, treatment_groups (with planned enrollment), "
            "randomization_ratio, study_duration, primary_endpoint "
            "(name, measurement_tool, timepoint, statistical_method), "
            "secondary_endpoints (list), and analysis_populations (list "
            "with definitions). Return as a single JSON object."
        ),
        gold_path="gold/T3.3.study_design_meta.001/",
        oracle_params={
            "slots": [
                "study_id",
                "phase",
                "indication",
                "primary_endpoint.name",
                "primary_endpoint.statistical_method",
                "analysis_populations",
            ],
            "match_mode": "exact",
        },
    ),
]

# ── Scale-task parameter lists ──────────────────────────────────────

_SDTM_P: list[tuple[str, str, str, int, str, str]] = [
    (
        "cm",
        "CM",
        "Concomitant Medications",
        2982,
        "complex",
        "Extract CM domain variable metadata. Focus on medication coding (CMDECOD, CMTRT), ATC classification (CMCLAS, CMCLASCD), route (CMROUTE), dose (CMDOSU, CMDOSFRQ), and date variables (CMSTDTC, CMENDTC). Return as JSON with 'variables' array.",
    ),
    (
        "ds",
        "DS",
        "Disposition",
        562,
        "mixed",
        "Extract DS domain variable metadata. Focus on disposition terms (DSDECOD, DSTERM), categories (DSCAT), visit association (VISIT, VISITNUM), and date variables. Return as JSON with 'variables' array.",
    ),
    (
        "mh",
        "MH",
        "Medical History",
        1116,
        "complex",
        "Extract MH domain variable metadata. Focus on MedDRA coding (MHTERM, MHDECOD, MHBODSYS), history category (MHCAT), and date handling (MHSTDTC, MHENDTC). Return as JSON with 'variables' array.",
    ),
    (
        "qs",
        "QS",
        "Questionnaires",
        30096,
        "complex",
        "Extract QS domain variable metadata. Focus on questionnaire test codes (QSTESTCD, QSTEST), scoring (QSORRES, QSSTRESC, QSSTRESN), and visit alignment. Return as JSON with 'variables' array.",
    ),
    (
        "sc",
        "SC",
        "Subject Characteristics",
        508,
        "simple",
        "Extract SC domain variable metadata. Focus on characteristic test codes (SCTESTCD, SCTEST) and results (SCORRES, SCSTRESC). Return as JSON with 'variables' array.",
    ),
    (
        "sv",
        "SV",
        "Subject Visits",
        3640,
        "mixed",
        "Extract SV domain variable metadata. Focus on visit identification (VISITNUM, VISIT), visit dates (SVSTDTC, SVENDTC), and study day derivation (SVDY). Return as JSON with 'variables' array.",
    ),
    (
        "se",
        "SE",
        "Subject Elements",
        5056,
        "simple",
        "Extract SE domain variable metadata. Focus on element identification (ETCD, ELEMENT), element dates (SESTDTC, SEENDTC), and arm ordering (TAETORD). Return as JSON with 'variables' array.",
    ),
    (
        "ta",
        "TA",
        "Trial Arms",
        3,
        "simple",
        "Extract TA domain variable metadata. Focus on arm definitions (ARMCD, ARM), element ordering (TAETORD), and element references (ETCD). Return as JSON with 'variables' array.",
    ),
    (
        "te",
        "TE",
        "Trial Elements",
        3,
        "simple",
        "Extract TE domain variable metadata. Focus on element definitions (ETCD, ELEMENT), start/end rules (TESTR, TEENRL), and duration (TEDUR). Return as JSON with 'variables' array.",
    ),
    (
        "ti",
        "TI",
        "Inclusion/Exclusion Criteria",
        21,
        "mixed",
        "Extract TI domain variable metadata. Focus on criterion parameters (TSPARMCD, TSPARM) and values (TSVAL). Return as JSON with 'variables' array.",
    ),
    (
        "ts",
        "TS",
        "Trial Summary",
        24,
        "simple",
        "Extract TS domain variable metadata. Focus on trial summary parameters (TSPARMCD, TSPARM) and values (TSVAL). Return as JSON with 'variables' array.",
    ),
    (
        "tv",
        "TV",
        "Trial Visits",
        11,
        "simple",
        "Extract TV domain variable metadata. Focus on visit numbering (VISITNUM, VISIT) and timing (VISTPT, VISTPTREF). Return as JSON with 'variables' array.",
    ),
    (
        "relrec",
        "RELREC",
        "Related Records",
        38,
        "mixed",
        "Extract RELREC domain variable metadata. Focus on relationship variables (RDOMAIN, IDVAR, IDVARVAL, RELTYPE, RELID). Return as JSON with 'variables' array.",
    ),
    (
        "suppdm",
        "SUPPDM",
        "Supplemental DM",
        558,
        "mixed",
        "Extract SUPPDM domain variable metadata. Focus on supplemental qualifier structure (RDOMAIN, USUBJID, IDVAR, QNAM, QVAL, QLABEL). Return as JSON with 'variables' array.",
    ),
    (
        "suppae",
        "SUPPAE",
        "Supplemental AE",
        1191,
        "mixed",
        "Extract SUPPAE domain variable metadata. Focus on qualifier definitions (QNAM, QVAL, QLABEL) for AE-specific metadata. Return as JSON with 'variables' array.",
    ),
    (
        "supplb",
        "SUPPLB",
        "Supplemental LB",
        22152,
        "mixed",
        "Extract SUPPLB domain variable metadata. Focus on qualifier definitions for lab-specific metadata including fasted status. Return as JSON with 'variables' array.",
    ),
]

_ADAM_P: list[tuple[str, str, str, int, str, str]] = [
    (
        "adlbc",
        "ADLBC",
        "Laboratory Analysis",
        7778,
        "complex",
        "Extract ADLBC analysis dataset variable metadata. Focus on PARAMCD definitions, reference range indicators (ANRIND, BNRIND), shift variables (SHIFT), toxicity grading (ATOXGR, BTOXGR), and analysis value chain (AVAL, BASE, CHG). Return as JSON with 'variables' and 'parameters' arrays.",
    ),
    (
        "adtte",
        "ADTTE",
        "Time-to-Event Analysis",
        254,
        "complex",
        "Extract ADTTE parameter definitions and censoring rules. Focus on PARAMCD values, CNSR censoring logic, AVAL time derivation, event date definitions, and treatment variables. Return as JSON with 'parameters' array.",
    ),
    (
        "adsl_treat",
        "ADSL",
        "Treatment Variables",
        254,
        "mixed",
        "Extract ADSL treatment variable derivation rules. Focus on TRT01P/TRT01PN (planned) and TRT01A/TRT01AN (actual) mapping from ARMCD/ACTARMCD. Return as JSON with 'variables' array.",
    ),
    (
        "adsl_pop",
        "ADSL",
        "Population Flags",
        254,
        "mixed",
        "Extract ADSL population flag derivation rules. Focus on ITTFL, SAFFL, EFFFL, COMP24FL definitions and criteria. Return as JSON with 'variables' array.",
    ),
    (
        "adsl_bl",
        "ADSL",
        "Baseline Measures",
        254,
        "mixed",
        "Extract ADSL baseline measure derivation. Focus on HEIGHTBL, WEIGHTBL, BMIBL computation, and MMSETOT from QS domain. Return as JSON with 'variables' array.",
    ),
    (
        "adsl_disp",
        "ADSL",
        "Disposition Variables",
        254,
        "mixed",
        "Extract ADSL disposition variable derivation. Focus on DISCONFL, DSRAEFL, EOSSTT, DCSREAS definitions from DS domain. Return as JSON with 'variables' array.",
    ),
    (
        "adae_treat",
        "ADAE",
        "Treatment Variables",
        1191,
        "mixed",
        "Extract ADAE treatment variable propagation rules. Focus on TRTPN (planned) vs TRTAN (actual) derivation from ADSL. Return as JSON with 'variables' array.",
    ),
    (
        "adae_flag",
        "ADAE",
        "Analysis Flags",
        1191,
        "complex",
        "Extract ADAE treatment-emergent flag derivation. Focus on TRTEMFL logic (ASTDT >= TRTSDT), ASEV (max severity), and relatedness flags. Return as JSON with 'variables' array.",
    ),
    (
        "adadas_param",
        "ADADAS",
        "Parameter Definitions",
        2718,
        "complex",
        "Extract ADADAS PARAMCD/PARAM definitions. Focus on ACTOT total score and ACITM01-11 individual items, their scoring rules and ranges. Return as JSON with 'parameters' array.",
    ),
    (
        "adadas_visit",
        "ADADAS",
        "Visit Windowing",
        2718,
        "complex",
        "Extract ADADAS visit windowing rules. Focus on AWTARGET, AWLO, AWHI for Baseline (0), Week 8 (56), Week 16 (112), Week 24 (168). Return as JSON with 'visit_windows' array.",
    ),
    (
        "adlbc_ref",
        "ADLBC",
        "Reference Range Logic",
        7778,
        "mixed",
        "Extract ADLBC reference range indicator derivation. Focus on ANRIND, BNRIND logic (LOW/NORMAL/HIGH), SHIFT derivation, and ATOXGR grading. Return as JSON with 'variables' array.",
    ),
    (
        "adtte_event",
        "ADTTE",
        "Event Classification",
        254,
        "mixed",
        "Extract ADTTE event and censoring definitions. Focus on CNSR values (0=event, 1=censored), EVNTDESC, and PARAM-specific censoring rules. Return as JSON with 'parameters' array.",
    ),
    (
        "adadas_locf",
        "ADADAS",
        "LOCF Imputation",
        2718,
        "mixed",
        "Extract ADADAS LOCF imputation rules. Focus on DTYPE flag, baseline exclusion from carry-forward, and analysis flag ANL01FL per SAP. Return as JSON with 'variables' array.",
    ),
    (
        "adlbc_shift",
        "ADLBC",
        "Shift Analysis Variables",
        7778,
        "mixed",
        "Extract ADLBC shift analysis variable derivation. Focus on SHIFT variable (baseline category to post-baseline category transition) and its relationship to ANRIND/BNRIND. Return as JSON with 'variables' array.",
    ),
]

_STUDY_P: list[tuple[str, str, str, str]] = [
    (
        "treatment_groups",
        "Extract treatment group definitions and coding",
        "mixed",
        "Extract treatment group information from protocol and SAP. Return: group names (Placebo, Xanomeline Low, Xanomeline High), ARMCD values (Pbo, Xan_Lo, Xan_Hi), TRT01PN numeric codes (0, 54, 81), route (Transdermal), planned enrollment (100 each). Return as JSON.",
    ),
    (
        "populations",
        "Extract analysis population definitions and counts",
        "mixed",
        "Extract analysis population definitions from SAP. Return: ITT (all randomized, N=254), Safety (received at least 1 dose, N=254), Efficacy (post-baseline assessment, N=234), Completers Week 24. Include derivation criteria for each. Return as JSON.",
    ),
    (
        "primary_endpoint",
        "Extract primary endpoint specification from SAP",
        "complex",
        "Extract primary endpoint specification. Return: endpoint name (ADAS-Cog CFB Week 24), measurement tool (ADAS-Cog 11 items), timepoint (Week 24), statistical method (ANCOVA with treatment, site group, baseline), missing data (LOCF), model formula, Type III SS, proportional weighting. Return as JSON.",
    ),
    (
        "secondary_endpoints",
        "Extract secondary endpoint specifications",
        "mixed",
        "Extract secondary endpoint specifications from SAP. Return: list of secondary endpoints (CIBIC+, NPI-X, safety), their measurement tools, timepoints, and statistical methods. Return as JSON.",
    ),
    (
        "study_design",
        "Extract study design elements from protocol",
        "mixed",
        "Extract study design metadata. Return: design type (randomized, double-blind, placebo-controlled, parallel-group), randomization ratio (1:1:1), blinding method, number of arms (3), treatment duration (24 weeks), follow-up (2 weeks), number of sites. Return as JSON.",
    ),
    (
        "schedule_assess",
        "Extract assessment schedule and visit structure",
        "complex",
        "Extract visit and assessment schedule. Return: visit list (Screening, Baseline, Week 8, Week 16, Week 24, Follow-up), assessments per visit (vital signs, lab, ADAS-Cog, CIBIC+, NPI), visit windows, and scheduled timepoints. Return as JSON.",
    ),
    (
        "safety_spec",
        "Extract safety analysis specifications from SAP",
        "mixed",
        "Extract safety analysis specifications. Return: AE collection method, TEAE definition (onset >= first dose), SAE criteria, AE severity grading, causality assessment, safety populations, and analysis methods. Return as JSON.",
    ),
    (
        "indications",
        "Extract indication and eligibility criteria",
        "simple",
        "Extract indication (Alzheimer's Disease mild to moderate) and key eligibility criteria from protocol. Return: target population, age range, MMSE score range, diagnostic criteria, key exclusion criteria. Return as JSON.",
    ),
    (
        "data_standards",
        "Extract data standards and regulatory compliance info",
        "simple",
        "Extract data standards used. Return: SDTM version (IG 3.1.2), ADaM version (IG 1.1), Define-XML version (2.0), MedDRA version (8.0), CDISC controlled terminology version, Pinnacle 21 compliance status. Return as JSON.",
    ),
    (
        "sample_size",
        "Extract sample size and power calculation details",
        "mixed",
        "Extract sample size calculation from SAP. Return: planned N per group (100), total planned N (300), actual screened (306), actual randomized (254), power calculation parameters, effect size assumptions, alpha level, dropout assumptions. Return as JSON.",
    ),
]

# ── SDTM gold variable mapping ──────────────────────────────────────

_SDTM_VARS: dict[str, list[tuple[str, str, int, str, str]]] = {
    "CM": [
        ("CMTRT", "Char", 200, "Reported Name of Concomitant Medication", "CRF"),
        ("CMDECOD", "Char", 100, "Standardized Medication Name", "Assigned"),
        ("CMINDC", "Char", 200, "Indication", "CRF"),
        ("CMROUTE", "Char", 30, "Route of Administration", "Assigned"),
        ("CMSTDTC", "Char", 20, "Start Date/Time", "CRF"),
    ],
    "DS": [
        ("DSDECOD", "Char", 40, "Standardized Disposition Term", "Derived"),
        ("DSTERM", "Char", 200, "Reported Term for Disposition", "CRF"),
        ("DSCAT", "Char", 40, "Category for Disposition Event", "Assigned"),
        ("DSSTDTC", "Char", 20, "Start Date/Time", "CRF"),
        ("VISIT", "Char", 20, "Visit Name", "Derived"),
    ],
    "MH": [
        ("MHTERM", "Char", 100, "Reported Term for Medical History", "CRF"),
        ("MHDECOD", "Char", 100, "Standardized Term", "Assigned"),
        ("MHBODSYS", "Char", 100, "Body System or Organ Class", "Assigned"),
        ("MHCAT", "Char", 40, "Category", "Assigned"),
        ("MHSTDTC", "Char", 20, "Start Date/Time", "CRF"),
    ],
    "QS": [
        ("QSTESTCD", "Char", 8, "Question Short Name", "Assigned"),
        ("QSTEST", "Char", 40, "Question Name", "Assigned"),
        ("QSORRES", "Char", 20, "Original Result", "CRF"),
        ("QSSTRESC", "Char", 20, "Standardized Result (Char)", "Derived"),
        ("QSSTRESN", "Num", 8, "Standardized Result (Num)", "Derived"),
    ],
    "SC": [
        ("SCTESTCD", "Char", 8, "Characteristic Short Name", "Assigned"),
        ("SCTEST", "Char", 40, "Characteristic Name", "Assigned"),
        ("SCORRES", "Char", 20, "Original Result", "CRF"),
        ("SCSTRESC", "Char", 20, "Standardized Result", "Derived"),
    ],
    "SV": [
        ("VISITNUM", "Num", 8, "Visit Number", "Derived"),
        ("VISIT", "Char", 20, "Visit Name", "Derived"),
        ("SVSTDTC", "Char", 20, "Visit Start Date", "Derived"),
        ("SVENDTC", "Char", 20, "Visit End Date", "Derived"),
        ("SVDY", "Num", 8, "Study Day", "Derived"),
    ],
    "SE": [
        ("ETCD", "Char", 8, "Element Code", "Assigned"),
        ("ELEMENT", "Char", 40, "Element Description", "Assigned"),
        ("SESTDTC", "Char", 20, "Start Date", "Derived"),
        ("TAETORD", "Num", 8, "Order Within Arm", "Derived"),
    ],
    "TA": [
        ("ARMCD", "Char", 8, "Arm Code", "Assigned"),
        ("ARM", "Char", 40, "Arm Description", "Assigned"),
        ("TAETORD", "Num", 8, "Order", "Assigned"),
        ("ETCD", "Char", 8, "Element Code", "Assigned"),
    ],
    "TE": [
        ("ETCD", "Char", 8, "Element Code", "Assigned"),
        ("ELEMENT", "Char", 40, "Element Description", "Assigned"),
        ("TESTR", "Char", 200, "Start Rule", "Assigned"),
        ("TEDUR", "Num", 8, "Planned Duration", "Assigned"),
    ],
    "TI": [
        ("TSPARMCD", "Char", 8, "Parameter Code", "Assigned"),
        ("TSPARM", "Char", 40, "Parameter Description", "Assigned"),
        ("TSVAL", "Char", 200, "Parameter Value", "Assigned"),
    ],
    "TS": [
        ("TSPARMCD", "Char", 8, "Parameter Code", "Assigned"),
        ("TSPARM", "Char", 40, "Parameter Description", "Assigned"),
        ("TSVAL", "Char", 200, "Parameter Value", "Assigned"),
    ],
    "TV": [
        ("VISITNUM", "Num", 8, "Visit Number", "Assigned"),
        ("VISIT", "Char", 20, "Visit Name", "Assigned"),
        ("VISTPT", "Char", 20, "Visit Time Point", "Assigned"),
    ],
    "RELREC": [
        ("RDOMAIN", "Char", 2, "Related Domain", "Assigned"),
        ("IDVAR", "Char", 8, "Identifying Variable", "Assigned"),
        ("IDVARVAL", "Char", 20, "Identifying Variable Value", "Derived"),
        ("RELTYPE", "Char", 1, "Relationship Type", "Assigned"),
        ("RELID", "Char", 20, "Relationship ID", "Derived"),
    ],
    "SUPPDM": [
        ("RDOMAIN", "Char", 2, "Related Domain", "Assigned"),
        ("IDVAR", "Char", 8, "Identifying Variable", "Derived"),
        ("QNAM", "Char", 8, "Qualifier Variable Name", "Assigned"),
        ("QVAL", "Char", 200, "Data Value", "Derived"),
        ("QLABEL", "Char", 40, "Qualifier Variable Label", "Assigned"),
    ],
    "SUPPAE": [
        ("RDOMAIN", "Char", 2, "Related Domain", "Assigned"),
        ("IDVAR", "Char", 8, "Identifying Variable", "Derived"),
        ("QNAM", "Char", 8, "Qualifier Variable Name", "Assigned"),
        ("QVAL", "Char", 200, "Data Value", "Derived"),
        ("QLABEL", "Char", 40, "Qualifier Variable Label", "Assigned"),
    ],
    "SUPPLB": [
        ("RDOMAIN", "Char", 2, "Related Domain", "Assigned"),
        ("IDVAR", "Char", 8, "Identifying Variable", "Derived"),
        ("QNAM", "Char", 8, "Qualifier Variable Name", "Assigned"),
        ("QVAL", "Char", 200, "Data Value", "Derived"),
        ("QLABEL", "Char", 40, "Qualifier Variable Label", "Assigned"),
    ],
}


def _sdtm_spec_gold(
    DOMAIN: str, variables: list[tuple[str, str, int, str, str]]
) -> dict:
    """Build gold output for an SDTM spec extraction task."""
    return {
        "variables": [
            {
                "variable_name": v[0],
                "type": v[1],
                "length": v[2],
                "label": v[3],
                "origin": v[4],
            }
            for v in variables
        ],
    }


# ── _build_scale ────────────────────────────────────────────────────


def _build_scale() -> tuple[list[dict], dict[str, dict]]:
    """Build SCALE_TASKS and SCALE_GOLD from parameter lists."""
    tasks: list[dict] = []
    gold: dict[str, dict] = {}
    idx = 2  # continue from .001 used by original tasks

    # T3.1 SDTM scale tasks
    for domain, DOMAIN, label, records, complexity, prompt_focus in _SDTM_P:
        tid = f"T3.1.sdtm_{domain}_extract.{idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T3.1",
                title=f"Extract SDTM {DOMAIN} ({label}) domain variable metadata",
                complexity=complexity,
                fixtures=["fixtures/04_sdtm/SDTM_Specifications.md"],
                spec=f"fixtures/04_sdtm/SDTM_Specifications.md#{DOMAIN}",
                prompt=(
                    f"Extract the SDTM {DOMAIN} ({label}) domain variable metadata. "
                    f"This domain contains {records} records. {prompt_focus}"
                ),
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "variables[].variable_name",
                        "variables[].type",
                        "variables[].label",
                    ],
                    "match_mode": "exact",
                },
            ),
        )
        gold[tid] = _sdtm_spec_gold(DOMAIN, _SDTM_VARS[DOMAIN])
        idx += 1

    # T3.2 ADaM scale tasks
    for name, DATASET, focus_label, records, complexity, prompt_focus in _ADAM_P:
        tid = f"T3.2.adam_{name}_extract.{idx:03d}"
        # Determine oracle slots based on prompt focus keywords
        if (
            "parameters" in prompt_focus.lower()
            and "visit_windows" not in prompt_focus.lower()
        ):
            oracle_slots = ["parameters[].paramcd", "parameters[].description"]
            match_mode = "exact"
        elif "visit_windows" in prompt_focus.lower():
            oracle_slots = ["visit_windows[].visit", "visit_windows[].awtarget"]
            match_mode = "exact"
        else:
            oracle_slots = ["variables[].variable_name", "variables[].derivation_notes"]
            match_mode = "superset"

        tasks.append(
            _task(
                task_id=tid,
                subcategory="T3.2",
                title=f"Extract {DATASET} ({focus_label}) variable metadata and derivation rules",
                complexity=complexity,
                fixtures=["fixtures/05_adam/ADaM_Specifications.md"],
                spec=f"fixtures/05_adam/ADaM_Specifications.md#{DATASET}",
                prompt=(
                    f"Extract the {DATASET} ({focus_label}) analysis dataset metadata. "
                    f"This dataset contains {records} records. {prompt_focus}"
                ),
                gold_path=f"gold/{tid}/",
                oracle_params={"slots": oracle_slots, "match_mode": match_mode},
            ),
        )
        # Build gold based on focus
        gold[tid] = _build_adam_scale_gold(name, DATASET, prompt_focus)
        idx += 1

    # T3.3 Study metadata scale tasks
    for name, title, complexity, prompt_focus in _STUDY_P:
        tid = f"T3.3.{name}.{idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T3.3",
                title=title,
                complexity=complexity,
                fixtures=[
                    "fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
                    "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
                ],
                spec="fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
                prompt=prompt_focus,
                gold_path=f"gold/{tid}/",
                oracle_params={"slots": [], "match_mode": "superset"},
            ),
        )
        gold[tid] = _build_study_scale_gold(name)
        idx += 1

    return tasks, gold


def _build_adam_scale_gold(name: str, DATASET: str, prompt_focus: str) -> dict:
    """Build gold output for an ADaM scale task based on its focus."""
    focus_lower = prompt_focus.lower()

    if "visit_windows" in focus_lower:
        return {
            "visit_windows": [
                {
                    "visit": "Baseline",
                    "avisitn": 0,
                    "awtarget": 0,
                    "awlo": None,
                    "awhi": 1,
                },
                {
                    "visit": "Week 8",
                    "avisitn": 8,
                    "awtarget": 56,
                    "awlo": 29,
                    "awhi": 84,
                },
                {
                    "visit": "Week 16",
                    "avisitn": 16,
                    "awtarget": 112,
                    "awlo": 85,
                    "awhi": 140,
                },
                {
                    "visit": "Week 24",
                    "avisitn": 24,
                    "awtarget": 168,
                    "awlo": 141,
                    "awhi": 336,
                },
            ],
        }

    if name == "adlbc":
        return {
            "variables": [
                {
                    "variable_name": "PARAMCD",
                    "type": "Char",
                    "length": 8,
                    "label": "Parameter Code",
                    "origin": "Assigned",
                },
                {
                    "variable_name": "AVAL",
                    "type": "Num",
                    "length": 8,
                    "label": "Analysis Value",
                    "origin": "Derived",
                },
                {
                    "variable_name": "BASE",
                    "type": "Num",
                    "length": 8,
                    "label": "Baseline Value",
                    "origin": "Derived",
                },
                {
                    "variable_name": "CHG",
                    "type": "Num",
                    "length": 8,
                    "label": "Change from Baseline",
                    "origin": "Derived",
                },
                {
                    "variable_name": "ANRIND",
                    "type": "Char",
                    "length": 10,
                    "label": "Reference Range Indicator (Analysis)",
                    "origin": "Derived",
                },
                {
                    "variable_name": "BNRIND",
                    "type": "Char",
                    "length": 10,
                    "label": "Reference Range Indicator (Baseline)",
                    "origin": "Derived",
                },
                {
                    "variable_name": "SHIFT",
                    "type": "Char",
                    "length": 20,
                    "label": "Shift from Baseline Reference Range",
                    "origin": "Derived",
                },
                {
                    "variable_name": "ATOXGR",
                    "type": "Char",
                    "length": 10,
                    "label": "Analysis Toxicity Grade",
                    "origin": "Derived",
                },
            ],
            "parameters": [
                {"paramcd": "ALB", "description": "Albumin (g/L)"},
                {"paramcd": "ALKPH", "description": "Alkaline Phosphatase (U/L)"},
                {"paramcd": "ALT", "description": "Alanine Aminotransferase (U/L)"},
                {"paramcd": "AST", "description": "Aspartate Aminotransferase (U/L)"},
                {"paramcd": "BILI", "description": "Bilirubin (umol/L)"},
                {"paramcd": "CHOL", "description": "Cholesterol (mmol/L)"},
            ],
        }

    if name == "adtte" or name == "adtte_event":
        return {
            "parameters": [
                {
                    "paramcd": "TTDE",
                    "param": "Time to First Dermatologic Event",
                    "cnsr_logic": "CNSR=1 if no event occurred before cutoff (censored), CNSR=0 if event occurred",
                    "aval_unit": "days",
                },
            ],
        }

    if name == "adsl_treat":
        return {
            "variables": [
                {
                    "variable_name": "TRT01P",
                    "type": "Char",
                    "length": 20,
                    "label": "Planned Treatment for Period 01",
                    "origin": "Derived",
                    "derivation_notes": "Mapped from DM.ARMCD",
                },
                {
                    "variable_name": "TRT01PN",
                    "type": "Num",
                    "length": 8,
                    "label": "Planned Treatment (N) for Period 01",
                    "origin": "Derived",
                    "derivation_notes": "0=Placebo, 54=Xan_Lo, 81=Xan_Hi from ARMCD",
                },
                {
                    "variable_name": "TRT01A",
                    "type": "Char",
                    "length": 20,
                    "label": "Actual Treatment for Period 01",
                    "origin": "Derived",
                    "derivation_notes": "Mapped from DM.ACTARM",
                },
                {
                    "variable_name": "TRT01AN",
                    "type": "Num",
                    "length": 8,
                    "label": "Actual Treatment (N) for Period 01",
                    "origin": "Derived",
                    "derivation_notes": "Numeric code from ACTARMCD",
                },
            ],
        }

    if name == "adsl_pop":
        return {
            "variables": [
                {
                    "variable_name": "ITTFL",
                    "type": "Char",
                    "length": 1,
                    "label": "Intent-to-Treat Population Flag",
                    "origin": "Derived",
                    "derivation_notes": "Y if subject randomized (ACTARMCD ne 'Scrnfail')",
                },
                {
                    "variable_name": "SAFFL",
                    "type": "Char",
                    "length": 1,
                    "label": "Safety Population Flag",
                    "origin": "Derived",
                    "derivation_notes": "Y if subject received at least one dose of study drug",
                },
                {
                    "variable_name": "EFFFL",
                    "type": "Char",
                    "length": 1,
                    "label": "Efficacy Population Flag",
                    "origin": "Derived",
                    "derivation_notes": "Y if subject has at least one post-baseline efficacy assessment",
                },
                {
                    "variable_name": "COMP24FL",
                    "type": "Char",
                    "length": 1,
                    "label": "Completers of Week 24 Population Flag",
                    "origin": "Derived",
                    "derivation_notes": "Y if subject completed Week 24 visit",
                },
            ],
        }

    if name == "adsl_bl":
        return {
            "variables": [
                {
                    "variable_name": "HEIGHTBL",
                    "type": "Num",
                    "length": 8,
                    "label": "Height at Baseline (cm)",
                    "origin": "CRF",
                    "derivation_notes": "From VS domain where VSTESTCD='HEIGHT' and baseline visit",
                },
                {
                    "variable_name": "WEIGHTBL",
                    "type": "Num",
                    "length": 8,
                    "label": "Weight at Baseline (kg)",
                    "origin": "CRF",
                    "derivation_notes": "From VS domain where VSTESTCD='WEIGHT' and baseline visit",
                },
                {
                    "variable_name": "BMIBL",
                    "type": "Num",
                    "length": 8,
                    "label": "BMI at Baseline (kg/m2)",
                    "origin": "Derived",
                    "derivation_notes": "Computed as WEIGHTBL / (HEIGHTBL/100)^2",
                },
                {
                    "variable_name": "MMSETOT",
                    "type": "Num",
                    "length": 8,
                    "label": "MMSE Total Score",
                    "origin": "CRF",
                    "derivation_notes": "From QS domain, Mini-Mental State Examination total score at screening",
                },
            ],
        }

    if name == "adsl_disp":
        return {
            "variables": [
                {
                    "variable_name": "DISCONFL",
                    "type": "Char",
                    "length": 1,
                    "label": "Disposition Discontinued Flag",
                    "origin": "Derived",
                    "derivation_notes": "Y if subject discontinued from study early",
                },
                {
                    "variable_name": "DSRAEFL",
                    "type": "Char",
                    "length": 1,
                    "label": "Discontinued Due to AE Flag",
                    "origin": "Derived",
                    "derivation_notes": "Y if DCSREAS indicates adverse event as reason",
                },
                {
                    "variable_name": "EOSSTT",
                    "type": "Char",
                    "length": 20,
                    "label": "End of Study Status",
                    "origin": "Derived",
                    "derivation_notes": "Completed or Discontinued from DS domain",
                },
                {
                    "variable_name": "DCSREAS",
                    "type": "Char",
                    "length": 40,
                    "label": "Reason for Discontinuation",
                    "origin": "Derived",
                    "derivation_notes": "Derived from DS domain disposition term",
                },
            ],
        }

    if name == "adae_treat":
        return {
            "variables": [
                {
                    "variable_name": "TRTPN",
                    "type": "Num",
                    "length": 8,
                    "label": "Planned Treatment (N)",
                    "origin": "Derived",
                    "derivation_notes": "Numeric treatment code from ADSL.TRT01PN, populated at AE onset time",
                },
                {
                    "variable_name": "TRTAN",
                    "type": "Num",
                    "length": 8,
                    "label": "Actual Treatment (N)",
                    "origin": "Derived",
                    "derivation_notes": "Numeric actual treatment code from ADSL.TRT01AN",
                },
                {
                    "variable_name": "TRTP",
                    "type": "Char",
                    "length": 20,
                    "label": "Planned Treatment",
                    "origin": "Derived",
                    "derivation_notes": "Character planned treatment from ADSL.TRT01P",
                },
                {
                    "variable_name": "TRTA",
                    "type": "Char",
                    "length": 20,
                    "label": "Actual Treatment",
                    "origin": "Derived",
                    "derivation_notes": "Character actual treatment from ADSL.TRT01A",
                },
            ],
        }

    if name == "adae_flag":
        return {
            "variables": [
                {
                    "variable_name": "TRTEMFL",
                    "type": "Char",
                    "length": 1,
                    "label": "Treatment Emergent Analysis Flag",
                    "origin": "Derived",
                    "derivation_notes": "Y if AE start date >= first dose date (ASTDT >= TRTSDT)",
                },
                {
                    "variable_name": "ASEV",
                    "type": "Char",
                    "length": 20,
                    "label": "Analysis Severity/Intensity",
                    "origin": "Derived",
                    "derivation_notes": "Maximum severity across all records for the same AE",
                },
                {
                    "variable_name": "AREL",
                    "type": "Char",
                    "length": 20,
                    "label": "Analysis Causality",
                    "origin": "Derived",
                    "derivation_notes": "Relatedness assessment from AEREL",
                },
            ],
        }

    if name == "adadas_param":
        return {
            "parameters": [
                {
                    "paramcd": "ACTOT",
                    "description": "ADAS-Cog (11) Total Score",
                    "type": "Composite of 11 ADAS-Cog items",
                },
                {
                    "paramcd": "ACITM01",
                    "description": "Word Recall Task",
                    "type": "ADAS-Cog Item 1",
                },
                {
                    "paramcd": "ACITM02",
                    "description": "Naming Objects and Fingers",
                    "type": "ADAS-Cog Item 2",
                },
                {
                    "paramcd": "ACITM03",
                    "description": "Commands",
                    "type": "ADAS-Cog Item 3",
                },
                {
                    "paramcd": "ACITM04",
                    "description": "Constructional Praxis",
                    "type": "ADAS-Cog Item 4",
                },
                {
                    "paramcd": "ACITM05",
                    "description": "Ideational Praxis",
                    "type": "ADAS-Cog Item 5",
                },
                {
                    "paramcd": "ACITM06",
                    "description": "Orientation",
                    "type": "ADAS-Cog Item 6",
                },
                {
                    "paramcd": "ACITM07",
                    "description": "Word Recognition",
                    "type": "ADAS-Cog Item 7",
                },
                {
                    "paramcd": "ACITM08",
                    "description": "Remembering Test Instructions",
                    "type": "ADAS-Cog Item 8",
                },
                {
                    "paramcd": "ACITM09",
                    "description": "Spoken Language Ability",
                    "type": "ADAS-Cog Item 9",
                },
                {
                    "paramcd": "ACITM10",
                    "description": "Comprehension",
                    "type": "ADAS-Cog Item 10",
                },
                {
                    "paramcd": "ACITM11",
                    "description": "Word-Finding Difficulty",
                    "type": "ADAS-Cog Item 11",
                },
            ],
        }

    if name == "adadas_locf":
        return {
            "variables": [
                {
                    "variable_name": "DTYPE",
                    "type": "Char",
                    "length": 10,
                    "label": "Derivation Type",
                    "origin": "Derived",
                    "derivation_notes": "LOCF flag indicates last observation carried forward; baseline records excluded from carry-forward",
                },
                {
                    "variable_name": "ANL01FL",
                    "type": "Char",
                    "length": 1,
                    "label": "Analysis Record Flag 01",
                    "origin": "Derived",
                    "derivation_notes": "Y for records meeting SAP analysis criteria, including LOCF records",
                },
                {
                    "variable_name": "AVAL",
                    "type": "Num",
                    "length": 8,
                    "label": "Analysis Value",
                    "origin": "Derived",
                    "derivation_notes": "Analysis value; LOCF-imputed when DTYPE='LOCF'",
                },
                {
                    "variable_name": "BASE",
                    "type": "Num",
                    "length": 8,
                    "label": "Baseline Value",
                    "origin": "Derived",
                    "derivation_notes": "Value at baseline visit, not subject to LOCF",
                },
            ],
        }

    if name == "adlbc_ref":
        return {
            "variables": [
                {
                    "variable_name": "ANRIND",
                    "type": "Char",
                    "length": 10,
                    "label": "Reference Range Indicator (Analysis)",
                    "origin": "Derived",
                    "derivation_notes": "LOW/NORMAL/HIGH based on AVAL vs ANRLO/ANRHI",
                },
                {
                    "variable_name": "BNRIND",
                    "type": "Char",
                    "length": 10,
                    "label": "Reference Range Indicator (Baseline)",
                    "origin": "Derived",
                    "derivation_notes": "LOW/NORMAL/HIGH based on BASE vs ANRLO/ANRHI",
                },
                {
                    "variable_name": "SHIFT",
                    "type": "Char",
                    "length": 20,
                    "label": "Shift from Baseline Reference Range",
                    "origin": "Derived",
                    "derivation_notes": "Derived as BNRIND to ANRIND transition",
                },
                {
                    "variable_name": "ATOXGR",
                    "type": "Char",
                    "length": 10,
                    "label": "Analysis Toxicity Grade",
                    "origin": "Derived",
                    "derivation_notes": "Grading based on CTCAE criteria from AVAL",
                },
                {
                    "variable_name": "BTOXGR",
                    "type": "Char",
                    "length": 10,
                    "label": "Baseline Toxicity Grade",
                    "origin": "Derived",
                    "derivation_notes": "Grading based on CTCAE criteria from BASE",
                },
            ],
        }

    if name == "adlbc_shift":
        return {
            "variables": [
                {
                    "variable_name": "SHIFT",
                    "type": "Char",
                    "length": 20,
                    "label": "Shift from Baseline Reference Range",
                    "origin": "Derived",
                    "derivation_notes": "Represents baseline category to post-baseline category transition (e.g., NORMAL-LOW)",
                },
                {
                    "variable_name": "ANRIND",
                    "type": "Char",
                    "length": 10,
                    "label": "Reference Range Indicator (Analysis)",
                    "origin": "Derived",
                    "derivation_notes": "LOW/NORMAL/HIGH based on AVAL vs reference range",
                },
                {
                    "variable_name": "BNRIND",
                    "type": "Char",
                    "length": 10,
                    "label": "Reference Range Indicator (Baseline)",
                    "origin": "Derived",
                    "derivation_notes": "LOW/NORMAL/HIGH based on BASE vs reference range",
                },
            ],
        }

    # Fallback: generic variables entry
    return {"variables": []}


def _build_study_scale_gold(name: str) -> dict:
    """Build gold output for a T3.3 study metadata scale task."""
    study_gold_map: dict[str, dict] = {
        "treatment_groups": {
            "treatment_groups": [
                {
                    "group": "Placebo",
                    "armcd": "Pbo",
                    "trt01pn": 0,
                    "route": "Transdermal",
                    "planned_enrollment": 100,
                },
                {
                    "group": "Xanomeline Low Dose",
                    "armcd": "Xan_Lo",
                    "trt01pn": 54,
                    "route": "Transdermal",
                    "planned_enrollment": 100,
                },
                {
                    "group": "Xanomeline High Dose",
                    "armcd": "Xan_Hi",
                    "trt01pn": 81,
                    "route": "Transdermal",
                    "planned_enrollment": 100,
                },
            ],
        },
        "populations": {
            "populations": [
                {
                    "name": "ITT (Intent-to-Treat)",
                    "definition": "All randomized subjects",
                    "n": 254,
                    "criteria": "All subjects who were randomized to treatment",
                },
                {
                    "name": "Safety",
                    "definition": "All subjects who received at least one dose",
                    "n": 254,
                    "criteria": "Received at least 1 dose of study drug",
                },
                {
                    "name": "Efficacy",
                    "definition": "All subjects with post-baseline efficacy assessment",
                    "n": 234,
                    "criteria": "At least one post-baseline efficacy assessment",
                },
                {
                    "name": "Completers Week 24",
                    "definition": "Subjects who completed Week 24 visit",
                    "criteria": "Completed the Week 24 study visit",
                },
            ],
        },
        "primary_endpoint": {
            "primary_endpoint": {
                "name": "Change from Baseline to Week 24 in ADAS-Cog (11) Score",
                "measurement_tool": "ADAS-Cog (Alzheimer's Disease Assessment Scale - Cognitive Subscale, 11 items)",
                "timepoint": "Week 24",
                "statistical_method": "ANCOVA with treatment, pooled site group, and baseline score as covariates",
                "missing_data": "LOCF (Last Observation Carried Forward)",
                "model_formula": "CHG = TRT + SITE_GROUP + BASE",
                "type_iii_ss": True,
                "weighting": "Proportional",
            },
        },
        "secondary_endpoints": {
            "secondary_endpoints": [
                {
                    "name": "CIBIC+",
                    "measurement_tool": "Clinician's Interview-Based Impression of Change",
                    "timepoint": "Week 24",
                    "statistical_method": "ANCOVA",
                },
                {
                    "name": "NPI-X",
                    "measurement_tool": "Neuropsychiatric Inventory",
                    "timepoint": "Week 24",
                    "statistical_method": "ANCOVA",
                },
                {
                    "name": "Safety",
                    "measurement_tool": "AE monitoring, lab tests, vital signs",
                    "timepoint": "Throughout",
                    "statistical_method": "Descriptive statistics",
                },
            ],
        },
        "study_design": {
            "design_type": "Randomized, double-blind, placebo-controlled, parallel-group",
            "randomization_ratio": "1:1:1",
            "blinding_method": "Double-blind",
            "number_of_arms": 3,
            "treatment_duration": "24 weeks",
            "follow_up": "2 weeks",
            "number_of_sites": 6,
        },
        "schedule_assess": {
            "visits": [
                "Screening",
                "Baseline",
                "Week 8",
                "Week 16",
                "Week 24",
                "Follow-up",
            ],
            "assessments_per_visit": {
                "Screening": ["Vital Signs", "Lab Tests", "MMSE", "Medical History"],
                "Baseline": ["Vital Signs", "Lab Tests", "ADAS-Cog", "CIBIC+", "NPI"],
                "Week 8": ["Vital Signs", "Lab Tests", "ADAS-Cog", "CIBIC+"],
                "Week 16": ["Vital Signs", "Lab Tests", "ADAS-Cog", "CIBIC+"],
                "Week 24": ["Vital Signs", "Lab Tests", "ADAS-Cog", "CIBIC+", "NPI"],
                "Follow-up": ["Vital Signs", "Lab Tests"],
            },
            "visit_windows": {
                "Week 8": "56 +/- 28 days",
                "Week 16": "112 +/- 28 days",
                "Week 24": "168 +/- 14 days",
            },
        },
        "safety_spec": {
            "ae_collection": "Spontaneous reporting and investigator assessment",
            "teae_definition": "Adverse event with onset on or after first dose of study drug",
            "sae_criteria": "Results in death, life-threatening, requires hospitalization, disabling, or medically important",
            "ae_severity_grading": "Mild, Moderate, Severe",
            "causality_assessment": "Investigator assessment of relationship to study drug",
            "safety_populations": ["Safety (all treated subjects)"],
            "analysis_methods": [
                "Incidence tables by treatment group",
                "Summary of severity and relationship",
            ],
        },
        "indications": {
            "indication": "Alzheimer's Disease (Mild to Moderate)",
            "target_population": "Patients with mild to moderate Alzheimer's Disease",
            "age_range": "50-85 years",
            "mmse_score_range": "10-26",
            "diagnostic_criteria": "DSM-IV criteria for dementia of the Alzheimer's type, NINCDS-ADRDA criteria",
            "key_exclusion_criteria": [
                "Other neurological disorders",
                "Significant psychiatric illness",
                "Severe or unstable medical conditions",
            ],
        },
        "data_standards": {
            "sdtm_version": "SDTM IG 3.1.2",
            "adam_version": "ADaM IG 1.1",
            "define_xml_version": "Define-XML 2.0",
            "meddra_version": "8.0",
            "cdisc_ct_version": "CDISC Controlled Terminology",
            "pinnacle_21_compliance": True,
        },
        "sample_size": {
            "planned_n_per_group": 100,
            "total_planned_n": 300,
            "actual_screened": 306,
            "actual_randomized": 254,
            "power_calculation": {
                "alpha": 0.05,
                "power": 0.80,
                "effect_size": "Clinically meaningful difference in ADAS-Cog",
                "dropout_assumption": "20%",
            },
        },
    }
    return study_gold_map.get(name, {})


SCALE_TASKS, SCALE_GOLD = _build_scale()

# ── Gold outputs ─────────────────────────────────────────────────────

GOLD_OUTPUTS: dict[str, dict] = {
    "T3.1.sdtm_dm_extract.001": {
        "variables": [
            {
                "variable_name": "STUDYID",
                "type": "Char",
                "length": 12,
                "label": "Study Identifier",
                "origin": "Assigned",
            },
            {
                "variable_name": "USUBJID",
                "type": "Char",
                "length": 11,
                "label": "Unique Subject Identifier",
                "origin": "Derived",
            },
            {
                "variable_name": "SUBJID",
                "type": "Char",
                "length": 4,
                "label": "Subject Identifier for the Study",
                "origin": "CRF",
            },
            {
                "variable_name": "SITEID",
                "type": "Char",
                "length": 2,
                "label": "Study Site Identifier",
                "origin": "Derived",
            },
            {
                "variable_name": "ARMCD",
                "type": "Char",
                "length": 8,
                "label": "Planned Arm Code",
                "origin": "Derived",
            },
            {
                "variable_name": "ARM",
                "type": "Char",
                "length": 40,
                "label": "Description of Planned Arm",
                "origin": "Derived",
            },
            {
                "variable_name": "ACTARMCD",
                "type": "Char",
                "length": 8,
                "label": "Actual Arm Code",
                "origin": "Derived",
            },
            {
                "variable_name": "ACTARM",
                "type": "Char",
                "length": 40,
                "label": "Description of Actual Arm",
                "origin": "Derived",
            },
            {
                "variable_name": "AGE",
                "type": "Num",
                "length": 8,
                "label": "Age",
                "origin": "CRF",
            },
            {
                "variable_name": "AGEU",
                "type": "Char",
                "length": 10,
                "label": "Age Units",
                "origin": "Assigned",
            },
            {
                "variable_name": "SEX",
                "type": "Char",
                "length": 2,
                "label": "Sex",
                "origin": "CRF",
            },
            {
                "variable_name": "RACE",
                "type": "Char",
                "length": 40,
                "label": "Race",
                "origin": "CRF",
            },
            {
                "variable_name": "ETHNIC",
                "type": "Char",
                "length": 22,
                "label": "Ethnicity",
                "origin": "CRF",
            },
            {
                "variable_name": "COUNTRY",
                "type": "Char",
                "length": 3,
                "label": "Country",
                "origin": "Derived",
            },
            {
                "variable_name": "RFICDEC",
                "type": "Num",
                "length": 8,
                "label": "Date/Time of Informed Consent",
                "origin": "CRF",
            },
        ],
    },
    "T3.1.sdtm_ae_extract.001": {
        "variables": [
            {
                "variable_name": "STUDYID",
                "type": "Char",
                "length": 12,
                "label": "Study Identifier",
                "origin": "Assigned",
            },
            {
                "variable_name": "USUBJID",
                "type": "Char",
                "length": 11,
                "label": "Unique Subject Identifier",
                "origin": "Derived",
            },
            {
                "variable_name": "AESEQ",
                "type": "Num",
                "length": 8,
                "label": "Sequence Number",
                "origin": "Derived",
            },
            {
                "variable_name": "AETERM",
                "type": "Char",
                "length": 100,
                "label": "Reported Term for the Adverse Event",
                "origin": "CRF",
            },
            {
                "variable_name": "AELLT",
                "type": "Char",
                "length": 100,
                "label": "Lowest Level Term",
                "origin": "Assigned",
            },
            {
                "variable_name": "AEDECOD",
                "type": "Char",
                "length": 100,
                "label": "Dictionary-Derived Term",
                "origin": "Assigned",
            },
            {
                "variable_name": "AEHLT",
                "type": "Char",
                "length": 100,
                "label": "High Level Term",
                "origin": "Assigned",
            },
            {
                "variable_name": "AEHLGT",
                "type": "Char",
                "length": 100,
                "label": "High Level Group Term",
                "origin": "Assigned",
            },
            {
                "variable_name": "AEBODSYS",
                "type": "Char",
                "length": 100,
                "label": "Body System or Organ Class",
                "origin": "Assigned",
            },
            {
                "variable_name": "AESEV",
                "type": "Char",
                "length": 20,
                "label": "Severity/Intensity",
                "origin": "CRF",
            },
            {
                "variable_name": "AESER",
                "type": "Char",
                "length": 1,
                "label": "Serious Event",
                "origin": "Derived",
            },
            {
                "variable_name": "AEACN",
                "type": "Char",
                "length": 30,
                "label": "Action Taken with Study Treatment",
                "origin": "CRF",
            },
            {
                "variable_name": "AEREL",
                "type": "Char",
                "length": 20,
                "label": "Causality",
                "origin": "CRF",
            },
            {
                "variable_name": "AEOUT",
                "type": "Char",
                "length": 30,
                "label": "Outcome of Adverse Event",
                "origin": "CRF",
            },
            {
                "variable_name": "AESTDTC",
                "type": "Char",
                "length": 20,
                "label": "Start Date/Time of Adverse Event",
                "origin": "CRF",
            },
            {
                "variable_name": "AEENDTC",
                "type": "Char",
                "length": 20,
                "label": "End Date/Time of Adverse Event",
                "origin": "CRF",
            },
        ],
    },
    "T3.1.sdtm_ex_extract.001": {
        "variables": [
            {
                "variable_name": "STUDYID",
                "type": "Char",
                "length": 12,
                "label": "Study Identifier",
                "origin": "Assigned",
            },
            {
                "variable_name": "USUBJID",
                "type": "Char",
                "length": 11,
                "label": "Unique Subject Identifier",
                "origin": "Derived",
            },
            {
                "variable_name": "EXSEQ",
                "type": "Num",
                "length": 8,
                "label": "Sequence Number",
                "origin": "Derived",
            },
            {
                "variable_name": "EXTRT",
                "type": "Char",
                "length": 40,
                "label": "Name of Actual Treatment",
                "origin": "CRF",
            },
            {
                "variable_name": "EXDOSE",
                "type": "Num",
                "length": 8,
                "label": "Dose per Administration",
                "origin": "CRF",
            },
            {
                "variable_name": "EXDOSU",
                "type": "Char",
                "length": 20,
                "label": "Dose Units",
                "origin": "Assigned",
            },
            {
                "variable_name": "EXDOSFRM",
                "type": "Char",
                "length": 20,
                "label": "Dose Form",
                "origin": "Assigned",
            },
            {
                "variable_name": "EXROUTE",
                "type": "Char",
                "length": 30,
                "label": "Route of Administration",
                "origin": "Assigned",
            },
            {
                "variable_name": "EXSTDTC",
                "type": "Char",
                "length": 20,
                "label": "Start Date/Time of Treatment",
                "origin": "CRF",
            },
            {
                "variable_name": "EXENDTC",
                "type": "Char",
                "length": 20,
                "label": "End Date/Time of Treatment",
                "origin": "CRF",
            },
        ],
    },
    "T3.1.sdtm_lb_extract.001": {
        "variables": [
            {
                "variable_name": "STUDYID",
                "type": "Char",
                "length": 12,
                "label": "Study Identifier",
                "origin": "Assigned",
            },
            {
                "variable_name": "USUBJID",
                "type": "Char",
                "length": 11,
                "label": "Unique Subject Identifier",
                "origin": "Derived",
            },
            {
                "variable_name": "LBSEQ",
                "type": "Num",
                "length": 8,
                "label": "Sequence Number",
                "origin": "Derived",
            },
            {
                "variable_name": "LBTESTCD",
                "type": "Char",
                "length": 8,
                "label": "Lab Test or Examination Short Name",
                "origin": "Assigned",
            },
            {
                "variable_name": "LBTEST",
                "type": "Char",
                "length": 40,
                "label": "Lab Test or Examination Name",
                "origin": "Assigned",
            },
            {
                "variable_name": "LBORRES",
                "type": "Char",
                "length": 20,
                "label": "Result or Finding in Original Units",
                "origin": "CRF",
            },
            {
                "variable_name": "LBORRESU",
                "type": "Char",
                "length": 10,
                "label": "Original Units",
                "origin": "CRF",
            },
            {
                "variable_name": "LBSTRESC",
                "type": "Char",
                "length": 20,
                "label": "Character Result/Finding in Std Format",
                "origin": "Derived",
            },
            {
                "variable_name": "LBSTRESN",
                "type": "Num",
                "length": 8,
                "label": "Numeric Result/Finding in Standard Units",
                "origin": "Derived",
            },
            {
                "variable_name": "LBSTRESU",
                "type": "Char",
                "length": 10,
                "label": "Standard Units",
                "origin": "Derived",
            },
        ],
    },
    "T3.1.sdtm_domain_list.001": {
        "domains": [
            {
                "domain_code": "DM",
                "domain_label": "Demographics",
                "cdisc_class": "Special Purpose",
                "record_count": 306,
                "filename": "dm.xpt",
            },
            {
                "domain_code": "AE",
                "domain_label": "Adverse Events",
                "cdisc_class": "Events",
                "record_count": 1191,
                "filename": "ae.xpt",
            },
            {
                "domain_code": "CM",
                "domain_label": "Concomitant Medications",
                "cdisc_class": "Interventions",
                "record_count": 2982,
                "filename": "cm.xpt",
            },
            {
                "domain_code": "DS",
                "domain_label": "Disposition",
                "cdisc_class": "Events",
                "record_count": 562,
                "filename": "ds.xpt",
            },
            {
                "domain_code": "EX",
                "domain_label": "Exposure",
                "cdisc_class": "Interventions",
                "record_count": 2772,
                "filename": "ex.xpt",
            },
            {
                "domain_code": "LB",
                "domain_label": "Laboratory Test Results",
                "cdisc_class": "Findings",
                "record_count": 54828,
                "filename": "lb.xpt",
            },
            {
                "domain_code": "MH",
                "domain_label": "Medical History",
                "cdisc_class": "Events",
                "record_count": 1116,
                "filename": "mh.xpt",
            },
            {
                "domain_code": "QS",
                "domain_label": "Questionnaires",
                "cdisc_class": "Findings",
                "record_count": 30096,
                "filename": "qs.xpt",
            },
            {
                "domain_code": "VS",
                "domain_label": "Vital Signs",
                "cdisc_class": "Findings",
                "record_count": 7024,
                "filename": "vs.xpt",
            },
            {
                "domain_code": "SC",
                "domain_label": "Subject Characteristics",
                "cdisc_class": "Findings",
                "record_count": 508,
                "filename": "sc.xpt",
            },
            {
                "domain_code": "SV",
                "domain_label": "Subject Visits",
                "cdisc_class": "Special Purpose",
                "record_count": 3640,
                "filename": "sv.xpt",
            },
            {
                "domain_code": "SE",
                "domain_label": "Subject Elements",
                "cdisc_class": "Special Purpose",
                "record_count": 5056,
                "filename": "se.xpt",
            },
            {
                "domain_code": "TA",
                "domain_label": "Trial Arms",
                "cdisc_class": "Trial Design",
                "record_count": 3,
                "filename": "ta.xpt",
            },
            {
                "domain_code": "TE",
                "domain_label": "Trial Elements",
                "cdisc_class": "Trial Design",
                "record_count": 3,
                "filename": "te.xpt",
            },
            {
                "domain_code": "TI",
                "domain_label": "Trial Inclusion/Exclusion Criteria",
                "cdisc_class": "Trial Design",
                "record_count": 21,
                "filename": "ti.xpt",
            },
            {
                "domain_code": "TS",
                "domain_label": "Trial Summary",
                "cdisc_class": "Trial Design",
                "record_count": 24,
                "filename": "ts.xpt",
            },
            {
                "domain_code": "TV",
                "domain_label": "Trial Visits",
                "cdisc_class": "Trial Design",
                "record_count": 11,
                "filename": "tv.xpt",
            },
            {
                "domain_code": "RELREC",
                "domain_label": "Related Records",
                "cdisc_class": "Relationship",
                "record_count": 38,
                "filename": "relrec.xpt",
            },
            {
                "domain_code": "SUPPAE",
                "domain_label": "Supplemental Qualifiers for AE",
                "cdisc_class": "Supplemental",
                "record_count": 1191,
                "filename": "suppae.xpt",
            },
            {
                "domain_code": "SUPPDM",
                "domain_label": "Supplemental Qualifiers for DM",
                "cdisc_class": "Supplemental",
                "record_count": 558,
                "filename": "suppdm.xpt",
            },
            {
                "domain_code": "SUPPDS",
                "domain_label": "Supplemental Qualifiers for DS",
                "cdisc_class": "Supplemental",
                "record_count": 466,
                "filename": "suppds.xpt",
            },
            {
                "domain_code": "SUPPLB",
                "domain_label": "Supplemental Qualifiers for LB",
                "cdisc_class": "Supplemental",
                "record_count": 22152,
                "filename": "supplb.xpt",
            },
        ],
    },
    "T3.2.adam_adsl_extract.001": {
        "variables": [
            {
                "variable_name": "TRT01PN",
                "type": "Num",
                "length": 8,
                "label": "Planned Treatment (N) for Period 01",
                "origin": "Derived",
                "derivation_notes": "Numeric treatment code: 0=Placebo, 54=Xan_Lo, 81=Xan_Hi",
            },
            {
                "variable_name": "TRT01P",
                "type": "Char",
                "length": 20,
                "label": "Planned Treatment for Period 01",
                "origin": "Derived",
                "derivation_notes": "Character treatment mapped from DM.ARMCD",
            },
            {
                "variable_name": "TRT01AN",
                "type": "Num",
                "length": 8,
                "label": "Actual Treatment (N) for Period 01",
                "origin": "Derived",
                "derivation_notes": "Numeric actual treatment code from ACTARMCD",
            },
            {
                "variable_name": "TRT01A",
                "type": "Char",
                "length": 20,
                "label": "Actual Treatment for Period 01",
                "origin": "Derived",
                "derivation_notes": "Character actual treatment from DM.ACTARM",
            },
            {
                "variable_name": "ITTFL",
                "type": "Char",
                "length": 1,
                "label": "Intent-to-Treat Population Flag",
                "origin": "Derived",
                "derivation_notes": "Y if subject randomized (ACTARMCD ne 'Scrnfail')",
            },
            {
                "variable_name": "SAFFL",
                "type": "Char",
                "length": 1,
                "label": "Safety Population Flag",
                "origin": "Derived",
                "derivation_notes": "Y if subject received at least one dose of study drug",
            },
            {
                "variable_name": "EFFFL",
                "type": "Char",
                "length": 1,
                "label": "Efficacy Population Flag",
                "origin": "Derived",
                "derivation_notes": "Y if subject has at least one post-baseline efficacy assessment",
            },
            {
                "variable_name": "COMP24FL",
                "type": "Char",
                "length": 1,
                "label": "Completers of Week 24 Population Flag",
                "origin": "Derived",
                "derivation_notes": "Y if subject completed Week 24 visit",
            },
            {
                "variable_name": "HEIGHTBL",
                "type": "Num",
                "length": 8,
                "label": "Height at Baseline (cm)",
                "origin": "CRF",
                "derivation_notes": "From VS domain where VSTESTCD='HEIGHT' and baseline visit",
            },
            {
                "variable_name": "WEIGHTBL",
                "type": "Num",
                "length": 8,
                "label": "Weight at Baseline (kg)",
                "origin": "CRF",
                "derivation_notes": "From VS domain where VSTESTCD='WEIGHT' and baseline visit",
            },
            {
                "variable_name": "BMIBL",
                "type": "Num",
                "length": 8,
                "label": "BMI at Baseline (kg/m2)",
                "origin": "Derived",
                "derivation_notes": "Computed as WEIGHTBL / (HEIGHTBL/100)^2",
            },
            {
                "variable_name": "MMSETOT",
                "type": "Num",
                "length": 8,
                "label": "MMSE Total Score",
                "origin": "CRF",
                "derivation_notes": "From QS domain, Mini-Mental State Examination total score at screening",
            },
            {
                "variable_name": "DISCONFL",
                "type": "Char",
                "length": 1,
                "label": "Disposition Discontinued Flag",
                "origin": "Derived",
                "derivation_notes": "Y if subject discontinued from study early",
            },
            {
                "variable_name": "DSRAEFL",
                "type": "Char",
                "length": 1,
                "label": "Discontinued Due to AE Flag",
                "origin": "Derived",
                "derivation_notes": "Y if DCSREAS indicates adverse event as reason",
            },
            {
                "variable_name": "EOSSTT",
                "type": "Char",
                "length": 20,
                "label": "End of Study Status",
                "origin": "Derived",
                "derivation_notes": "Completed or Discontinued from DS domain",
            },
        ],
    },
    "T3.2.adam_adadas_extract.001": {
        "parameters": [
            {
                "paramcd": "ACTOT",
                "description": "ADAS-Cog (11) Total Score",
                "type": "Composite of 11 ADAS-Cog items",
            },
            {
                "paramcd": "ACITM01",
                "description": "Word Recall Task",
                "type": "ADAS-Cog Item 1",
            },
            {
                "paramcd": "ACITM02",
                "description": "Naming Objects and Fingers",
                "type": "ADAS-Cog Item 2",
            },
            {
                "paramcd": "ACITM03",
                "description": "Commands",
                "type": "ADAS-Cog Item 3",
            },
            {
                "paramcd": "ACITM04",
                "description": "Constructional Praxis",
                "type": "ADAS-Cog Item 4",
            },
            {
                "paramcd": "ACITM05",
                "description": "Ideational Praxis",
                "type": "ADAS-Cog Item 5",
            },
            {
                "paramcd": "ACITM06",
                "description": "Orientation",
                "type": "ADAS-Cog Item 6",
            },
            {
                "paramcd": "ACITM07",
                "description": "Word Recognition",
                "type": "ADAS-Cog Item 7",
            },
            {
                "paramcd": "ACITM08",
                "description": "Remembering Test Instructions",
                "type": "ADAS-Cog Item 8",
            },
            {
                "paramcd": "ACITM09",
                "description": "Spoken Language Ability",
                "type": "ADAS-Cog Item 9",
            },
            {
                "paramcd": "ACITM10",
                "description": "Comprehension",
                "type": "ADAS-Cog Item 10",
            },
            {
                "paramcd": "ACITM11",
                "description": "Word-Finding Difficulty",
                "type": "ADAS-Cog Item 11",
            },
        ],
        "visit_windows": [
            {"visit": "Baseline", "avisitn": 0, "awtarget": 0, "awlo": None, "awhi": 1},
            {"visit": "Week 8", "avisitn": 8, "awtarget": 56, "awlo": 29, "awhi": 84},
            {
                "visit": "Week 16",
                "avisitn": 16,
                "awtarget": 112,
                "awlo": 85,
                "awhi": 140,
            },
            {
                "visit": "Week 24",
                "avisitn": 24,
                "awtarget": 168,
                "awlo": 141,
                "awhi": 336,
            },
        ],
    },
    "T3.2.adam_adae_extract.001": {
        "variables": [
            {
                "variable_name": "TRTEMFL",
                "type": "Char",
                "length": 1,
                "label": "Treatment Emergent Analysis Flag",
                "derivation_notes": "Y if AE start date >= first dose date (ASTDT >= TRTSDT), derived from comparison of AE onset and treatment start dates",
            },
            {
                "variable_name": "TRTPN",
                "type": "Num",
                "length": 8,
                "label": "Planned Treatment (N)",
                "derivation_notes": "Numeric treatment code from ADSL.TRT01PN, populated at AE onset time",
            },
            {
                "variable_name": "TRTA",
                "type": "Char",
                "length": 20,
                "label": "Actual Treatment",
                "derivation_notes": "Character actual treatment from ADSL.TRT01A",
            },
            {
                "variable_name": "ASTDY",
                "type": "Num",
                "length": 8,
                "label": "Analysis Start Relative Day",
                "derivation_notes": "AE start date minus treatment start date plus 1",
            },
            {
                "variable_name": "AENDY",
                "type": "Num",
                "length": 8,
                "label": "Analysis End Relative Day",
                "derivation_notes": "AE end date minus treatment start date plus 1",
            },
            {
                "variable_name": "ASEV",
                "type": "Char",
                "length": 20,
                "label": "Analysis Severity/Intensity",
                "derivation_notes": "Maximum severity across all records for the same AE",
            },
        ],
    },
    "T3.2.adam_adtte_extract.001": {
        "parameters": [
            {
                "paramcd": "TTDE",
                "param": "Time to First Dermatologic Event",
                "cnsr_logic": "CNSR=1 if no event occurred before cutoff (censored), CNSR=0 if event occurred",
                "aval_unit": "days",
            },
        ],
    },
    "T3.3.study_design_meta.001": {
        "study_id": "CDISCPilot01",
        "phase": "Phase 2/3",
        "indication": "Alzheimer's Disease (Mild to Moderate)",
        "treatment_name": "Xanomeline Transdermal Therapeutic System (TTS)",
        "treatment_route": "Transdermal",
        "treatment_groups": [
            {
                "group": "Placebo",
                "description": "Transdermal patch (placebo)",
                "planned_enrollment": 100,
            },
            {
                "group": "Xanomeline Low Dose",
                "description": "Xanomeline TTS 50 cm2",
                "planned_enrollment": 100,
            },
            {
                "group": "Xanomeline High Dose",
                "description": "Xanomeline TTS 75 cm2",
                "planned_enrollment": 100,
            },
        ],
        "randomization_ratio": "1:1:1",
        "study_duration": "24 weeks treatment + 2 weeks follow-up",
        "primary_endpoint": {
            "name": "Change from Baseline to Week 24 in ADAS-Cog (11) Score",
            "measurement_tool": "ADAS-Cog (Alzheimer's Disease Assessment Scale - Cognitive Subscale)",
            "timepoint": "Week 24",
            "statistical_method": "ANCOVA with treatment, pooled site group, and baseline score as covariates; LOCF for missing data",
        },
        "secondary_endpoints": [
            "CIBIC+ (Clinician's Interview-Based Impression of Change)",
            "NPI-X (Neuropsychiatric Inventory) Change from Baseline",
            "Safety and Tolerability (descriptive statistics)",
        ],
        "analysis_populations": [
            {"name": "ITT (Intent-to-Treat)", "definition": "All randomized subjects"},
            {
                "name": "Safety",
                "definition": "All subjects who received at least one dose of study drug",
            },
            {
                "name": "Efficacy",
                "definition": "All subjects with at least one post-baseline efficacy assessment",
            },
        ],
    },
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
        gold_file = gold_dir / "expected_output.json"
        gold_data = all_gold[tid]
        gold_file.write_text(json.dumps(gold_data, indent=2) + "\n", encoding="utf-8")
        print(f"  wrote {gold_file}")

    print(f"\nGenerated {len(all_tasks)} T3 tasks in {TASKS_DIR}")
    print(f"Gold outputs in {GOLD_ROOT}")


if __name__ == "__main__":
    main()
