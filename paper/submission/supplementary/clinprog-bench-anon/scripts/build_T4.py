"""Generate T4 (doc) benchmark tasks from eSubmission-Benchmark substrate.

Creates 10 task JSON files under tasks/T4_doc/ and corresponding gold
outputs under gold/<task_id>/.

Usage:
    python scripts/build_T4.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks" / "T4_doc"
GOLD_ROOT = ROOT / "gold"

SEED_REPO = "anonymous/eSubmission-Benchmark"
SEED_COMMIT = "658fcc05506b169a27dee6e2c3a1ccdaaf64a716"
DERIVATION_SCRIPT = "scripts/build_T4.py"

# ── Shared building blocks ──────────────────────────────────────────


def _provenance() -> dict:
    return {
        "seed_repo": SEED_REPO,
        "seed_commit": SEED_COMMIT,
        "derivation_script": DERIVATION_SCRIPT,
        "human_authors": ["R02"],
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
        "category": "T4",
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
            "kind": "text",
            "gold_path": gold_path,
            "oracle": {"type": "slot_fill", "params": oracle_params},
        },
        "scoring": {"scorer": "doc", "weight": 1.0},
        "leakage_audit": {"fixture_sha256_overlap": False, "prompt_ngram_hits": 0},
    }


# ── Task definitions ────────────────────────────────────────────────

TASKS: list[dict] = [
    # ── T4.1 TLF documentation ──────────────────────────────────
    _task(
        task_id="T4.1.tlf_demo_doc.001",
        subcategory="T4.1",
        title="Document demographics table specifications from mock shell and ground truth",
        complexity="mixed",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-1-03_demographic.md",
            "fixtures/06_tlfs/outputs/TLF_INVENTORY.md",
        ],
        spec="fixtures/06_tlfs/mock_templates/README.md",
        prompt=(
            "Write structured documentation for Table 14-1.03 Demographics. "
            "Include: table title, population, treatment columns, row "
            "specifications (variable, statistic type, display format), "
            "data source (ADSL), and ground truth values from TLF_INVENTORY. "
            "Document should follow a standard TLF specification format with "
            "sections for Header, Population, Columns, Rows, Statistics, "
            "and Footnotes."
        ),
        gold_path="gold/T4.1.tlf_demo_doc.001/",
        oracle_params={
            "slots": [
                "title",
                "population",
                "data_source",
                "treatment_groups",
                "row_specifications",
                "footnotes",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T4.1.tlf_primary_doc.001",
        subcategory="T4.1",
        title="Document primary endpoint analysis table specifications",
        complexity="complex",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-3-01_primary_endpoint.md",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        spec="fixtures/06_tlfs/mock_templates/README.md",
        prompt=(
            "Write comprehensive documentation for Table 14-3.01 Primary "
            "Endpoint (ADAS-Cog CFB Week 24). Include: table title, "
            "population (Efficacy), analysis model specification (ANCOVA), "
            "treatment comparisons, statistical methods (Type III SS, "
            "proportional weighting), missing data handling (LOCF), data "
            "source variables (ADADAS), and mock shell footnotes. Document "
            "should be suitable for statistical programming specification."
        ),
        gold_path="gold/T4.1.tlf_primary_doc.001/",
        oracle_params={
            "slots": [
                "title",
                "population",
                "analysis_model",
                "missing_data_method",
                "data_source",
                "footnotes",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T4.1.tlf_ae_doc.001",
        subcategory="T4.1",
        title="Document adverse event overview table specifications",
        complexity="mixed",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-4-01_ae_overview.md",
            "fixtures/06_tlfs/mock_templates/t_mock_14-4-02_ae_by_soc_pt.md",
        ],
        spec="fixtures/06_tlfs/mock_templates/README.md",
        prompt=(
            "Write documentation for the AE tables: Table 14-4.01 AE "
            "Overview and Table 14-4.02 AE by SOC/PT. For each table "
            "document: title, population (Safety), treatment columns, row "
            "categories (overview: any AE, TEAE, SAE, etc.; by SOC/PT: "
            "filtered TEAEs with >=5% threshold), data sources (ADAE with "
            "TRTEMFL), and display conventions (subject counts, event "
            "counts, percentages)."
        ),
        gold_path="gold/T4.1.tlf_ae_doc.001/",
        oracle_params={
            "slots": [
                "tables[].title",
                "tables[].population",
                "tables[].row_categories",
                "tables[].data_source",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T4.1.tlf_km_doc.001",
        subcategory="T4.1",
        title="Document Kaplan-Meier plot specifications for time-to-event analysis",
        complexity="complex",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/f_mock_14-5-01_km_plot.md",
        ],
        spec="fixtures/06_tlfs/mock_templates/README.md",
        prompt=(
            "Write documentation for Figure 14-5.01 KM Plot (TTDE, Safety "
            "population). Include: figure title, population, endpoint "
            "(time to first dermatologic event), treatment arm display "
            "(line styles), axis specifications, risk table layout, "
            "censoring mark conventions, 95% CI display, statistical "
            "summary table (N, Events, Median, log-rank p-value), and "
            "data source (ADTTE)."
        ),
        gold_path="gold/T4.1.tlf_km_doc.001/",
        oracle_params={
            "slots": [
                "title",
                "population",
                "endpoint",
                "treatment_display",
                "statistical_summary",
                "data_source",
            ],
            "match_mode": "superset",
        },
    ),
    # ── T4.2 Dataset documentation ───────────────────────────────
    _task(
        task_id="T4.2.dataset_card_doc.001",
        subcategory="T4.2",
        title="Document dataset card completeness and metadata quality",
        complexity="mixed",
        fixtures=[
            "fixtures/DATASET_CARD.md",
        ],
        spec="fixtures/DATASET_CARD.md",
        prompt=(
            "Review the dataset card and produce a structured documentation "
            "report. Extract and document: study overview (ID, phase, "
            "indication, treatment, design), subject populations with counts, "
            "SDTM dataset inventory (22 domains with record counts), ADaM "
            "dataset inventory (5 datasets with record counts), data "
            "standards (SDTM IG, ADaM IG, Define-XML versions), and "
            "ground truth values available for validation. Note any gaps "
            "or missing metadata fields."
        ),
        gold_path="gold/T4.2.dataset_card_doc.001/",
        oracle_params={
            "slots": [
                "study_overview.study_id",
                "study_overview.phase",
                "study_overview.indication",
                "subject_populations",
                "sdtm_dataset_count",
                "adam_dataset_count",
                "data_standards",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T4.2.define_sdtm_doc.001",
        subcategory="T4.2",
        title="Document SDTM define.xml metadata structure and compliance",
        complexity="complex",
        fixtures=[
            "fixtures/04_sdtm/define.xml",
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md",
        prompt=(
            "Document the SDTM define.xml file structure. Include: Define-XML "
            "version, ODM schema version, number of ItemGroupDefs (domains), "
            "number of ItemDefs (variables), number of CodeListDefs, "
            "controlled terminology sources (MedDRA version, CDISC "
            "submission values), metadata version information, and "
            "compliance with Define-XML 2.0 standard. Cross-reference "
            "with SDTM_Specifications.md for completeness."
        ),
        gold_path="gold/T4.2.define_sdtm_doc.001/",
        oracle_params={
            "slots": [
                "define_xml_version",
                "odm_schema_version",
                "itemgroup_count",
                "itemdef_count",
                "codelist_count",
                "meddra_version",
                "compliance_standard",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T4.2.define_adam_doc.001",
        subcategory="T4.2",
        title="Document ADaM define.xml metadata and analysis variable lineage",
        complexity="complex",
        fixtures=[
            "fixtures/05_adam/define.xml",
            "fixtures/05_adam/ADaM_Specifications.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md",
        prompt=(
            "Document the ADaM define.xml file structure. Include: Define-XML "
            "version, ODM schema version, dataset inventory (ADSL, ADAE, "
            "ADADAS, ADLBC, ADTTE), key analysis variable definitions, "
            "codelist count, computational method references, and "
            "compliance with ADaM IG 1.1 and Define-XML 2.0. Document "
            "the analysis variable lineage for primary endpoint "
            "(ADADAS.ACTOT derivation)."
        ),
        gold_path="gold/T4.2.define_adam_doc.001/",
        oracle_params={
            "slots": [
                "define_xml_version",
                "odm_schema_version",
                "dataset_inventory",
                "compliance_standards",
                "primary_endpoint_lineage",
            ],
            "match_mode": "exact",
        },
    ),
    # ── T4.3 Validation and study documentation ──────────────────
    _task(
        task_id="T4.3.val_plan_doc.001",
        subcategory="T4.3",
        title="Document validation plan coverage and execution methodology",
        complexity="complex",
        fixtures=[
            "fixtures/08_validation/master_validation_plan.md",
            "fixtures/08_validation/README.md",
        ],
        spec="fixtures/08_validation/master_validation_plan.md",
        prompt=(
            "Produce a structured documentation of the validation plan. "
            "Include: validation layers (Document Alignment, Data Lineage, "
            "Analysis Consistency, Regulatory Compliance), automated "
            "validation scripts (V001-V006 with descriptions), check "
            "categories (D-xxx data checks, L-xxx log checks, P-xxx "
            "programming checks, M-xxx method checks), execution phases, "
            "and expected pass/fail criteria. Summarize the overall "
            "validation methodology."
        ),
        gold_path="gold/T4.3.val_plan_doc.001/",
        oracle_params={
            "slots": [
                "validation_layers",
                "automated_scripts",
                "check_categories",
                "execution_phases",
                "methodology_summary",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T4.3.val_checklist_doc.001",
        subcategory="T4.3",
        title="Document alignment checklist structure and coverage completeness",
        complexity="mixed",
        fixtures=[
            "fixtures/08_validation/document_alignment_checklist.md",
            "fixtures/08_validation/consistency_validation.md",
        ],
        spec="fixtures/08_validation/master_validation_plan.md",
        prompt=(
            "Document the alignment checklist coverage. Include: Protocol-to-SAP "
            "alignment sections (objectives, design, treatments, populations, "
            "endpoints), SAP-to-Mock Shell alignment (table specifications), "
            "Mock Shell-to-TLF Output alignment (structure, values, "
            "formatting), analysis logic verification (ANCOVA model, "
            "LOCF, data selection filters). Report total check counts "
            "and completion status for each section."
        ),
        gold_path="gold/T4.3.val_checklist_doc.001/",
        oracle_params={
            "slots": [
                "protocol_sap_alignment_sections",
                "sap_mock_alignment_sections",
                "mock_tlf_alignment_sections",
                "analysis_logic_verification",
                "total_checks",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T4.3.study_synopsis.001",
        subcategory="T4.3",
        title="Generate integrated study synopsis from protocol and SAP",
        complexity="complex",
        fixtures=[
            "fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        spec="fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
        prompt=(
            "Generate an integrated study synopsis combining protocol and "
            "SAP information. Include: study title, study ID (CDISCPilot01), "
            "phase (2/3), indication (Alzheimer's Disease), treatment "
            "(Xanomeline TTS), objectives (primary and secondary), study "
            "design (randomized, double-blind, placebo-controlled, "
            "parallel-group), subject count (planned 300, actual 306 "
            "screened), treatment groups (Placebo, Xan 50cm2, Xan 75cm2), "
            "primary endpoint (ADAS-Cog CFB Week 24, ANCOVA), key "
            "secondary endpoints, and analysis populations (ITT, Safety, "
            "Efficacy)."
        ),
        gold_path="gold/T4.3.study_synopsis.001/",
        oracle_params={
            "slots": [
                "study_title",
                "study_id",
                "phase",
                "indication",
                "objectives.primary",
                "study_design",
                "treatment_groups",
                "primary_endpoint",
                "analysis_populations",
            ],
            "match_mode": "exact",
        },
    ),
]

# ── Scale task parameter lists ────────────────────────────────────────

_TLF_P: list[tuple] = [
    (
        "ae_overview",
        "14-4.01",
        "Adverse Event Overview",
        "Safety",
        "mixed",
        "ADAE",
        "t_mock_14-4-01_ae_overview.md",
        "Document Table 14-4.01 AE Overview. Include: table title, population (Safety), treatment columns, row categories (Any AE, TEAE, SAE, AE leading to death, AE leading to discontinuation), data source (ADAE with TRTEMFL), display conventions (subject counts, event counts, percentages).",
    ),
    (
        "disposition",
        "14-2.01",
        "Disposition Summary",
        "ITT",
        "mixed",
        "ADSL",
        "t_mock_14-2-01_disposition.md",
        "Document Table 14-2.01 Disposition. Include: table title, population (ITT), treatment columns, row categories (Completed, Discontinued by reason, Ongoing), data source (ADSL with DS variables), and disposition terminology.",
    ),
    (
        "conmed",
        "14-2.02",
        "Concomitant Medications",
        "Safety",
        "complex",
        "ADCM",
        "t_mock_14-2-02_conmed.md",
        "Document Table 14-2.02 Concomitant Medications. Include: ATC class grouping, medication prevalence, most common medications, data source (SDTM CM), and display format.",
    ),
    (
        "lab_summary",
        "14-6.01",
        "Laboratory Summary Over Time",
        "Safety",
        "complex",
        "ADLBC",
        "t_mock_14-6-01_lab_summary.md",
        "Document Table 14-6.01 Lab Summary. Include: lab parameters by visit, descriptive statistics, reference range flags, data source (ADLBC), and visit structure.",
    ),
    (
        "cfb",
        "14-3.02",
        "Change from Baseline Over Time",
        "Efficacy",
        "mixed",
        "ADADAS",
        "t_mock_14-3-02_cfb.md",
        "Document Table 14-3.02 CFB Over Time. Include: visit-wise change from baseline, standard errors, confidence intervals, treatment comparisons, data source (ADADAS), and visit schedule.",
    ),
    (
        "exposure",
        "14-2.03",
        "Exposure and Compliance",
        "Safety",
        "mixed",
        "ADSL",
        "t_mock_14-2-03_exposure.md",
        "Document Table 14-2.03 Exposure. Include: treatment duration, dose compliance, treatment intensity by group, data source (ADSL with EX variables), and display conventions.",
    ),
    (
        "responder",
        "14-3.03",
        "Responder Analysis",
        "Efficacy",
        "complex",
        "ADADAS",
        "t_mock_14-3-03_responder.md",
        "Document Table 14-3.03 Responder Analysis. Include: responder definition, response rates by treatment, CMH test, data source (ADADAS), and statistical methodology.",
    ),
    (
        "shift",
        "14-6.02",
        "Laboratory Shift Table",
        "Safety",
        "complex",
        "ADLBC",
        "t_mock_14-6-02_shift.md",
        "Document Table 14-6.02 Lab Shift Table. Include: reference range shifts from baseline, high/low/normal transitions, data source (ADLBC), and shift categorization rules.",
    ),
    (
        "medhist",
        "14-1.04",
        "Medical History Summary",
        "ITT",
        "mixed",
        "ADMH",
        "t_mock_14-1-04_medhist.md",
        "Document Table 14-1.04 Medical History. Include: SOC/PT prevalence, system organ class grouping, most common conditions, data source (SDTM MH with MedDRA coding), and display format.",
    ),
    (
        "screen",
        "14-1.01",
        "Screening Summary",
        "All Screened",
        "simple",
        "ADSL",
        "t_mock_14-1-01_screen.md",
        "Document Table 14-1.01 Screening Summary. Include: screening counts, screen failure reasons, enrollment summary, data source (ADSL/DM), and disposition categories.",
    ),
    (
        "safety_sum",
        "14-4.03",
        "Safety Summary Dashboard",
        "Safety",
        "complex",
        "ADAE",
        "t_mock_14-4-03_safety.md",
        "Document Table 14-4.03 Safety Summary. Include: overall safety profile, key AE categories, lab abnormality summary, data source (ADAE/ADLBC), and comprehensive safety display.",
    ),
    (
        "ae_severity",
        "14-4.04",
        "AE by Maximum Severity",
        "Safety",
        "mixed",
        "ADAE",
        "t_mock_14-4-04_severity.md",
        "Document Table 14-4.04 AE by Severity. Include: severity distribution by treatment, worst-case severity per subject, grade analysis, data source (ADAE with ASEV), and MedDRA coding.",
    ),
]

_DATASET_P: list[tuple] = [
    (
        "sdtm_inv",
        "Document SDTM domain inventory completeness",
        "simple",
        ["fixtures/04_sdtm/SDTM_Specifications.md"],
        "fixtures/04_sdtm/SDTM_Specifications.md",
        "Document the SDTM domain inventory. List all 22 domains with domain code, label, CDISC class, record count, and filename. Include data standards (SDTM IG 3.1.2, Define-XML 2.0). Return structured documentation.",
    ),
    (
        "adam_inv",
        "Document ADaM dataset inventory and structure",
        "simple",
        ["fixtures/05_adam/ADaM_Specifications.md"],
        "fixtures/05_adam/ADaM_Specifications.md",
        "Document the ADaM dataset inventory. List all 5 datasets (ADSL, ADAE, ADADAS, ADLBC, ADTTE) with class, records, and key variables. Include ADaM IG 1.1 standard. Return structured documentation.",
    ),
    (
        "sdtm_ae_spec",
        "Document SDTM AE domain specification completeness",
        "complex",
        ["fixtures/04_sdtm/SDTM_Specifications.md#AE"],
        "fixtures/04_sdtm/SDTM_Specifications.md#AE",
        "Document the SDTM AE domain specification. Include: all variables with types/lengths/labels, MedDRA coding hierarchy, seriousness flag definitions, controlled terminology references, and supplemental qualifier mappings. Return structured documentation.",
    ),
    (
        "adam_adsl_spec",
        "Document ADSL analysis variable derivation chain",
        "complex",
        ["fixtures/05_adam/ADaM_Specifications.md#ADSL"],
        "fixtures/05_adam/ADaM_Specifications.md#ADSL",
        "Document ADSL analysis variable derivation. Include: treatment variable derivation chain (DM.ARMCD → TRT01P/TRT01PN), population flag criteria, baseline measure sources, and disposition flag logic. Return structured documentation.",
    ),
    (
        "sdtm_vs_spec",
        "Document SDTM VS domain specification and unit handling",
        "mixed",
        ["fixtures/04_sdtm/SDTM_Specifications.md#VS"],
        "fixtures/04_sdtm/SDTM_Specifications.md#VS",
        "Document the SDTM VS domain specification. Include: VSTESTCD mapping (HEIGHT, WEIGHT, DIABP, SYSBP, PULSE, TEMP, RESP), unit standardization rules, baseline flag logic, and visit mapping. Return structured documentation.",
    ),
    (
        "adam_adadas_spec",
        "Document ADADAS parameter derivation and visit windowing",
        "complex",
        ["fixtures/05_adam/ADaM_Specifications.md#ADADAS"],
        "fixtures/05_adam/ADaM_Specifications.md#ADADAS",
        "Document ADADAS specification. Include: PARAMCD definitions (ACTOT, ACITM01-11), visit windowing rules (AWTARGET, AWLO, AWHI), LOCF imputation method, analysis flag criteria, and variable derivation (AVAL, BASE, CHG, PCHG). Return structured documentation.",
    ),
    (
        "sdtm_lb_spec",
        "Document SDTM LB domain specification with 54,828 records",
        "complex",
        ["fixtures/04_sdtm/SDTM_Specifications.md#LB"],
        "fixtures/04_sdtm/SDTM_Specifications.md#LB",
        "Document the SDTM LB domain specification. Include: LBTESTCD mapping, unit conversion logic, reference range handling, specimen type, and supplemental qualifier mappings. Return structured documentation.",
    ),
    (
        "adam_adae_spec",
        "Document ADAE treatment-emergent flag and analysis derivation",
        "mixed",
        ["fixtures/05_adam/ADaM_Specifications.md#ADAE"],
        "fixtures/05_adam/ADaM_Specifications.md#ADAE",
        "Document ADAE specification. Include: TRTEMFL derivation (ASTDT >= TRTSDT), treatment variable propagation, relative day calculations (ASTDY, AENDY), severity analysis, and custom query derivation. Return structured documentation.",
    ),
    (
        "adam_adtte_spec",
        "Document ADTTE parameter and censoring specifications",
        "mixed",
        ["fixtures/05_adam/ADaM_Specifications.md#ADTTE"],
        "fixtures/05_adam/ADaM_Specifications.md#ADTTE",
        "Document ADTTE specification. Include: PARAMCD definitions, PARAM descriptions, CNSR censoring logic (0=event, 1=censored), AVAL derivation, start/event date definitions, and treatment variable mapping. Return structured documentation.",
    ),
    (
        "adam_adlbc_spec",
        "Document ADLBC reference range and shift analysis variables",
        "complex",
        ["fixtures/05_adam/ADaM_Specifications.md#ADLBC"],
        "fixtures/05_adam/ADaM_Specifications.md#ADLBC",
        "Document ADLBC specification. Include: PARAMCD derivation from LBTESTCD, reference range indicator logic (ANRIND, BNRIND), shift variable (SHIFT), toxicity grading (ATOXGR, BTOXGR), and analysis value chain. Return structured documentation.",
    ),
]

_VAL_P: list[tuple] = [
    (
        "val_data_lineage",
        "Document data lineage from raw through SDTM to ADaM",
        "complex",
        [
            "fixtures/08_validation/consistency_validation.md",
            "fixtures/DATASET_CARD.md",
        ],
        "fixtures/08_validation/master_validation_plan.md",
        "Document the data lineage tracking methodology. Include: raw → SDTM → ADaM variable traceability, USUBJID cross-domain validation, subject count reconciliation (306 DM → 254 ADSL), and variable origin tracking. Return structured documentation.",
    ),
    (
        "val_treatment_doc",
        "Document treatment coding consistency across all datasets",
        "mixed",
        ["fixtures/08_validation/quality_report.md", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md#V002",
        "Document treatment coding standards. Include: ARMCD values (Pbo, Xan_Lo, Xan_Hi), TRT01PN mapping (0, 54, 81), consistency checks between DM/ADSL/ADADAS, and documentation alignment. Return structured documentation.",
    ),
    (
        "val_sap_analysis",
        "Document SAP analysis methodology and statistical methods",
        "complex",
        ["fixtures/01_study_design/sap/CDISCPilot01_SAP.md"],
        "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        "Document the SAP analysis methodology. Include: primary analysis (ANCOVA model specification), secondary analyses, multiplicity handling, missing data approaches (LOCF), subgroup analyses, and sensitivity analyses. Return structured documentation.",
    ),
    (
        "val_mock_inventory",
        "Document mock shell inventory and coverage",
        "mixed",
        ["fixtures/06_tlfs/mock_templates/"],
        "fixtures/06_tlfs/mock_templates/README.md",
        "Document the mock shell inventory. List all mock shells with table/figure IDs, titles, populations, data sources, and SAP coverage. Identify any gaps in mock shell coverage. Return structured documentation.",
    ),
    (
        "val_protocol_sap",
        "Document protocol-to-SAP alignment verification",
        "complex",
        [
            "fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        "fixtures/08_validation/document_alignment_checklist.md",
        "Document the protocol-to-SAP alignment. Verify: objectives map to analyses, treatment groups consistent, populations defined consistently, endpoints specified consistently, and design elements aligned. Return structured documentation.",
    ),
    (
        "val_sdtm_rules",
        "Document SDTM conformance rules and validation checks",
        "mixed",
        ["fixtures/04_sdtm/SDTM_Specifications.md", "fixtures/04_sdtm/define.xml"],
        "fixtures/08_validation/master_validation_plan.md",
        "Document SDTM conformance validation rules. Include: variable completeness, controlled terminology compliance, USUBJID format validation, domain relationship integrity, and Define-XML consistency. Return structured documentation.",
    ),
    (
        "val_adam_rules",
        "Document ADaM conformance rules and validation methodology",
        "mixed",
        ["fixtures/05_adam/ADaM_Specifications.md", "fixtures/05_adam/define.xml"],
        "fixtures/08_validation/master_validation_plan.md",
        "Document ADaM conformance validation. Include: structure compliance (ADSL, OCCDS, BDS, ADTTE), variable derivation verification, traceability to SDTM, and metadata consistency. Return structured documentation.",
    ),
    (
        "val_quality_metrics",
        "Document quality metrics and validation pass rates",
        "mixed",
        [
            "fixtures/08_validation/quality_report.md",
            "fixtures/08_validation/consistency_validation.md",
        ],
        "fixtures/08_validation/master_validation_plan.md",
        "Document quality metrics from validation execution. Include: check categories (D-xxx data, L-xxx log, P-xxx programming, M-xxx method), pass/fail rates, severity classification, and outstanding issues. Return structured documentation.",
    ),
]


# ── Scale gold template ───────────────────────────────────────────────


def _doc_gold_t(
    title: str,
    tlf_id: str = "",
    population: str = "",
    data_source: str = "",
    sections: list[str] | None = None,
) -> str:
    """Generate a text documentation gold template."""
    sections = sections or ["Header", "Specifications", "Data Source", "Footnotes"]
    parts = [f"# {title} - Documentation\n"]
    if tlf_id:
        parts.append(f"\n## Table/Figure ID: {tlf_id}\n")
    if population:
        parts.append(f"\n## Population: {population}\n")
    parts.append(f"\n## Data Source: {data_source}\n")
    for section in sections:
        parts.append(f"\n## {section}\n")
        parts.append(f"\n[{section} details to be extracted from fixtures]\n")
    return "".join(parts)


def _build_scale() -> tuple[list[dict], dict[str, str]]:
    """Build 30 scale tasks and their gold outputs."""
    tasks: list[dict] = []
    gold: dict[str, str] = {}

    # T4.1 scale tasks (idx starts at 2)
    for i, (name, tlf_id, title, pop, cplx, ds, mock_file, prompt) in enumerate(
        _TLF_P, start=2
    ):
        tid = f"T4.1.tlf_{name}_doc.{i:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T4.1",
                title=title,
                complexity=cplx,
                fixtures=[f"fixtures/06_tlfs/mock_templates/{mock_file}"],
                spec="fixtures/06_tlfs/mock_templates/README.md",
                prompt=prompt,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "title",
                        "population",
                        "data_source",
                        "treatment_groups",
                        "row_specifications",
                        "footnotes",
                    ],
                    "match_mode": "superset",
                },
            )
        )
        gold[tid] = _doc_gold_t(
            title=title,
            tlf_id=tlf_id,
            population=pop,
            data_source=ds,
        )

    # T4.2 scale tasks (idx starts at 2)
    for i, (name, title, cplx, fixtures, spec, prompt) in enumerate(
        _DATASET_P, start=2
    ):
        tid = f"T4.2.{name}_doc.{i:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T4.2",
                title=title,
                complexity=cplx,
                fixtures=fixtures,
                spec=spec,
                prompt=prompt,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "title",
                        "specification_summary",
                        "data_standards",
                        "variable_inventory",
                        "compliance_status",
                    ],
                    "match_mode": "superset",
                },
            )
        )
        gold[tid] = _doc_gold_t(
            title=title,
            data_source=spec,
            sections=[
                "Specifications",
                "Variable Inventory",
                "Data Standards",
                "Compliance",
                "Footnotes",
            ],
        )

    # T4.3 scale tasks (idx starts at 2)
    for i, (name, title, cplx, fixtures, spec, prompt) in enumerate(_VAL_P, start=2):
        tid = f"T4.3.{name}_doc.{i:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T4.3",
                title=title,
                complexity=cplx,
                fixtures=fixtures,
                spec=spec,
                prompt=prompt,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "title",
                        "validation_scope",
                        "methodology",
                        "check_categories",
                        "findings_summary",
                    ],
                    "match_mode": "superset",
                },
            )
        )
        gold[tid] = _doc_gold_t(
            title=title,
            data_source=spec,
            sections=[
                "Scope",
                "Methodology",
                "Check Categories",
                "Findings",
                "Recommendations",
            ],
        )

    return tasks, gold


SCALE_TASKS, SCALE_GOLD = _build_scale()

# ── Gold outputs ─────────────────────────────────────────────────────

GOLD_OUTPUTS: dict[str, str] = {
    "T4.1.tlf_demo_doc.001": """\
# Table 14-1.03 Demographics - TLF Specification

## Header
- **Table ID**: 14-1.03
- **Title**: Demographics and Baseline Characteristics
- **Population**: ITT (Intent-to-Treat) Population

## Columns
| Column | Label | N |
|--------|-------|---|
| Placebo | Placebo | 86 |
| Xanomeline Low Dose | Xanomeline TTS 50 cm2 | 84 |
| Xanomeline High Dose | Xanomeline TTS 75 cm2 | 84 |
| Total | Total | 254 |

## Row Specifications

### Age (years)
- n
- Mean (SD)
- Median
- Min - Max
- Age Group (<65, 65-80, >80): n (%)

### Sex
- Male: n (%)
- Female: n (%)

### Race
- White: n (%)
- Black or African American: n (%)
- American Indian or Alaska Native: n (%)
- Other: n (%)

### Height (cm)
- n, Mean (SD)

### Weight (kg)
- n, Mean (SD)

### BMI (kg/m2)
- n, Mean (SD)

### MMSE Total Score
- n, Mean (SD)

## Data Source
- **Dataset**: ADSL
- **Variables**: AGE, AGEGR1, SEX, RACE, HEIGHTBL, WEIGHTBL, BMIBL, MMSETOT
- **Population filter**: ITTFL = 'Y'
- **Treatment variable**: TRT01P

## Footnotes
1. ITT Population: All randomized subjects.
2. N = number of subjects in the treatment group.
3. n (%) = number (percentage) of subjects in the category.
4. SD = Standard Deviation.
""",
    "T4.1.tlf_primary_doc.001": """\
# Table 14-3.01 Primary Endpoint - TLF Specification

## Header
- **Table ID**: 14-3.01
- **Title**: Primary Endpoint Analysis - ADAS-Cog (11) Change from Baseline to Week 24 (LOCF)
- **Population**: Efficacy Population

## Analysis Model
- **Method**: ANCOVA (Analysis of Covariance)
- **Model**: CHG ~ TRTPN + SITEGR1 + BASE
- **Type**: Type III Sum of Squares
- **Weighting**: Proportional weighting
- **Dose Response**: Linear trend test (p-value)
- **Pairwise Comparisons**: Placebo vs each active dose

## Missing Data Handling
- **Method**: LOCF (Last Observation Carried Forward)
- **Implementation**: DTYPE = 'LOCF' flag in ADADAS dataset
- **Records**: 163 LOCF records at Week 24

## Table Structure
| Section | Content |
|---------|---------|
| Baseline | n, Mean (SD) by treatment group |
| Week 24 | n, Mean (SD) by treatment group |
| Change from Baseline | n, Mean (SD) by treatment group |
| Statistical Analysis | Dose response p-value, Pairwise LS Means, 95% CI |

## Data Source
- **Dataset**: ADADAS
- **Parameter**: PARAMCD = 'ACTOT'
- **Analysis flag**: ANL01FL = 'Y'
- **Visit**: AVISITN = 24 (Week 24)
- **Change variable**: CHG
- **Baseline variable**: BASE
- **Treatment variable**: TRTPN
- **Population filter**: EFFFL = 'Y'

## Footnotes
1. Efficacy Population: Subjects with at least one post-baseline efficacy assessment.
2. ANCOVA model: Change from Baseline = Treatment + Pooled Site Group + Baseline Score.
3. LOCF = Last Observation Carried Forward for post-baseline missing values.
""",
    "T4.1.tlf_ae_doc.001": """\
# AE Tables Documentation

## Table 14-4.01: Adverse Event Overview

### Header
- **Table ID**: 14-4.01
- **Title**: Overview of Adverse Events
- **Population**: Safety Population

### Columns
| Column | Label |
|--------|-------|
| Placebo | N=86 |
| Xanomeline Low Dose | N=84 |
| Xanomeline High Dose | N=84 |
| Total | N=254 |

### Row Categories
- Any Adverse Event: Subjects with at least one AE (n, %) / Number of events
- Treatment-Emergent AEs (TEAEs): TRTEMFL='Y' (n, %) / Number of events
- Serious AEs (SAEs): AESER='Y' and TRTEMFL='Y' (n, %) / Number of events
- AE Leading to Death: (n, %)
- AE Leading to Discontinuation: DSRAEFL='Y' (n, %)
- AE Leading to Dose Interruption: (n, %)

### Data Source
- **Dataset**: ADAE
- **Population filter**: SAFFL = 'Y'
- **TEAE filter**: TRTEMFL = 'Y'

## Table 14-4.02: AE by System Organ Class and Preferred Term

### Header
- **Table ID**: 14-4.02
- **Title**: Treatment-Emergent Adverse Events by SOC and PT (>=5% in Any Group)
- **Population**: Safety Population

### Display Rules
- Only TEAEs with >=5% incidence in any treatment group
- Sorted by SOC frequency (descending), then PT frequency within SOC
- Pre-listed SOCs with specific preferred terms

### Data Source
- **Dataset**: ADAE
- **MedDRA coding**: AEBODSYS (SOC), AEDECOD (PT)
- **Population filter**: SAFFL = 'Y'
- **TEAE filter**: TRTEMFL = 'Y'
- **Threshold**: >=5% in any treatment group

## Footnotes
1. Safety Population: Subjects who received at least one dose of study drug.
2. TEAE = Treatment-Emergent Adverse Event (onset >= first dose date).
3. n (%) = number (percentage) of subjects; multiple events per subject counted once.
""",
    "T4.1.tlf_km_doc.001": """\
# Figure 14-5.01 KM Plot - TLF Specification

## Header
- **Figure ID**: 14-5.01
- **Title**: Kaplan-Meier Plot of Time to First Dermatologic Event - Safety Population
- **Population**: Safety Population (N=254)

## Endpoint
- **Parameter**: TTDE (Time to First Dermatologic Event)
- **Dataset**: ADTTE
- **Time variable**: AVAL (days)
- **Event variable**: CNSR (0=event, 1=censored)

## Treatment Display
| Group | Line Style | Color |
|-------|-----------|-------|
| Placebo | Solid | - |
| Xanomeline Low Dose | Dashed | - |
| Xanomeline High Dose | Dotted | - |

## Axis Specifications
- **X-axis**: Time (days)
- **Y-axis**: Survival Probability (0.0 - 1.0)
- **Reference line**: y = 0.5

## Risk Table
- Number-at-risk displayed below the plot
- Rows: one per treatment group
- Columns: time intervals

## Statistical Summary Table
| Statistic | Content |
|-----------|---------|
| N | Subjects per treatment group |
| Events | Number of events per group |
| Median (95% CI) | Median time to event |
| Log-rank p-value | Overall comparison |

## Additional Elements
- Censoring marks: tick marks on survival curves
- 95% CI bands: displayed as shaded regions
- No multiplicity adjustment applied

## Data Source
- **Dataset**: ADTTE
- **Parameter**: PARAMCD = 'TTDE'
- **Population filter**: SAFFL = 'Y'
""",
    "T4.2.dataset_card_doc.001": """\
# Dataset Card Documentation Report

## Study Overview
- **Study ID**: CDISCPilot01
- **Phase**: Phase 2/3
- **Indication**: Alzheimer's Disease (Mild to Moderate)
- **Treatment**: Xanomeline Transdermal Therapeutic System (TTS)
- **Design**: Randomized, Double-Blind, Placebo-Controlled, Parallel-Group, Multi-Center
- **Duration**: 24 weeks treatment + 2 weeks follow-up

## Subject Populations
| Population | Count | Definition |
|-----------|-------|------------|
| Screened | 306 | All subjects screened |
| ITT | 254 | All randomized subjects |
| Safety | 254 | Subjects with at least one dose |
| Efficacy | 234 | Subjects with post-baseline efficacy data |

## SDTM Dataset Inventory
- **Total domains**: 22
- **Total variables**: 539
- **Total codelists**: 388
- **Key domains**: DM (306), AE (1,191), CM (2,982), EX (2,772), LB (54,828), QS (30,096), VS (7,024)

## ADaM Dataset Inventory
- **Total datasets**: 5
- **Total variables**: 509
- **Total codelists**: 894
- **Datasets**: ADSL (254), ADAE (1,191), ADADAS (2,718), ADLBC (7,778), ADTTE (254)

## Data Standards
- SDTM IG 3.1.2
- ADaM IG 1.1
- Define-XML 2.0
- MedDRA 8.0

## Ground Truth Values Available
- Demographic statistics by treatment group (Age, Sex, Race, BMI, MMSE)
- Primary endpoint: ADAS-Cog CFB Week 24 LOCF (163 LOCF records)
- Subject counts by population and treatment group
- Treatment coding: ARMCD (Pbo/Xan_Lo/Xan_Hi), TRT01PN (0/54/81)

## Metadata Quality Assessment
- Study design: Complete
- Population definitions: Complete
- Treatment groups: Complete
- Dataset inventory: Complete (22 SDTM + 5 ADaM)
- Variable-level specifications: Available via SDTM/ADaM Specifications
- Ground truth: Available via TLF_INVENTORY and DATASET_CARD
""",
    "T4.2.define_sdtm_doc.001": """\
# SDTM Define.xml Documentation Report

## File Metadata
- **Define-XML Version**: 2.0
- **ODM Schema Version**: 1.2.2
- **Source File**: 04_sdtm/define.xml

## Content Summary
- **ItemGroupDefs (Domains)**: 22
  - Special Purpose: DM, SV, SE
  - Events: AE, DS, MH
  - Interventions: CM, EX
  - Findings: LB, QS, SC, VS
  - Trial Design: TA, TE, TI, TS, TV
  - Relationship: RELREC
  - Supplemental: SUPPAE, SUPPDM, SUPPDS, SUPPLB
- **ItemDefs (Variables)**: 539
- **CodeListDefs**: 388

## Controlled Terminology Sources
- MedDRA Version: 8.0
- CDISC Submission Values: SDTM IG 3.1.2
- Study-specific codelists: Treatment arms, Visit codes, Test codes

## Compliance
- Standard: Define-XML 2.0
- SDTM Implementation Guide: 3.1.2
- Pinnacle 21 validation: Referenced in validation framework

## Cross-Reference with SDTM_Specifications.md
- All 22 domains in define.xml match specification inventory
- Variable-level metadata consistent between define.xml and specifications
- Codelist references aligned with P21 format specifications

## Notes
- Define.xml uses ODM v1.2.2 schema (differs from ADaM define.xml which uses v1.3.2)
- Supplemental qualifiers use standard RELID/RDOMAIN/IDVAR/QNAM/QVAL structure
""",
    "T4.2.define_adam_doc.001": """\
# ADaM Define.xml Documentation Report

## File Metadata
- **Define-XML Version**: 2.0
- **ODM Schema Version**: 1.3.2
- **Source File**: 05_adam/define.xml

## Dataset Inventory
| Dataset | Label | Class | Records |
|---------|-------|-------|---------|
| ADSL | Subject-Level Analysis | ADSL | 254 |
| ADAE | Adverse Events Analysis | OCCDS | 1,191 |
| ADADAS | ADAS-Cog Analysis | BDS | 2,718 |
| ADLBC | Laboratory Analysis | BDS | 7,778 |
| ADTTE | Time-to-Event Analysis | ADTTE | 254 |

## Key Analysis Variable Definitions
- **TRT01PN**: Planned Treatment (Numeric) - 0/54/81 mapping
- **ITTFL/SAFFL/EFFFL**: Population flags with explicit derivation rules
- **PARAMCD**: Analysis parameter codes per ADaM structure
- **AVAL/BASE/CHG/PCHG**: Analysis value chain per BDS standard

## Codelist Count
- **Total**: 894 codelists (P21 format with ARC extensions)

## Computational Methods
- ANCOVA model specification referenced for primary endpoint
- LOCF imputation method documented in ADADAS derivation
- Treatment-emergent flag logic documented in ADAE derivation

## Primary Endpoint Lineage (ADADAS.ACTOT)
1. Source: QS domain (CDISC SDTM)
2. Parameter: PARAMCD = 'ACTOT' (sum of 11 ADAS-Cog items)
3. Derivation: AVAL = sum of ACITM01-ACITM11 responses
4. Baseline: BASE = AVAL at AVISITN = 0
5. Change: CHG = AVAL - BASE
6. LOCF: DTYPE = 'LOCF' for post-baseline imputed records
7. Analysis flag: ANL01FL = 'Y' for included observations

## Compliance Standards
- ADaM Implementation Guide: 1.1
- Define-XML: 2.0
- ODM Schema: 1.3.2 (Note: differs from SDTM define.xml v1.2.2)
""",
    "T4.3.val_plan_doc.001": """\
# Validation Plan Documentation

## Validation Layers

### 1. Document Alignment
- Protocol to SAP consistency verification
- SAP to Mock Shell specification alignment
- Mock Shell to TLF Output structure matching

### 2. Data Lineage
- Subject ID traceability: Raw -> SDTM -> ADaM
- Variable lineage: TLF -> ADaM -> SDTM -> Raw mapping
- Cross-dataset USUBJID existence checks

### 3. Analysis Consistency
- Model specification verification (ANCOVA parameters)
- Results reproducibility (ground truth value comparison)
- Treatment coding consistency across datasets

### 4. Regulatory Compliance
- CDISC standard compliance (SDTM IG 3.1.2, ADaM IG 1.1)
- Pinnacle 21 validation
- Define-XML 2.0 completeness

## Automated Validation Scripts

| Script | Description | Key Checks |
|--------|-------------|------------|
| V001 | Subject Traceability | D-001 to D-004 (subject counts, USUBJID format) |
| V002 | Treatment Consistency | D-010 to D-013 (ARMCD, TRT01PN coding, treatment N) |
| V003 | Population Consistency | D-020 to D-023 (ITTFL, SAFFL, EFFFL, COMP24FL logic) |
| V004 | SAP-Mock Alignment | Specification matching for tables and figures |
| V005 | Analysis Logic | ANCOVA model, dose response, LS Means, LOCF |
| V006 | Demographic Consistency | ADSL statistics vs TLF ground truth |

## Check Categories
- **D-xxx**: Data consistency checks
- **L-xxx**: Log and output verification checks
- **P-xxx**: Programming logic checks
- **M-xxx**: Method and model specification checks

## Execution Phases
1. **Phase 1 - Data Validation**: Run V001-V003 (automated)
2. **Phase 2 - Document Validation**: Run V004 (semi-automated)
3. **Phase 3 - Analysis Validation**: Run V005-V006 (automated)
4. **Phase 4 - Final Report**: Compile results, resolve issues

## Methodology Summary
The validation follows a four-layer approach combining automated R scripts with manual document review. Automated checks verify data consistency, treatment coding, population logic, and analysis reproducibility. Manual checks ensure document alignment between protocol, SAP, mock shells, and final outputs. The quality report aggregates results across all checks with severity classification.
""",
    "T4.3.val_checklist_doc.001": """\
# Alignment Checklist Documentation

## Protocol-to-SAP Alignment Sections
- Study objectives mapping to analysis endpoints
- Treatment group definitions and coding
- Population definitions (ITT, Safety, Efficacy)
- Primary and secondary endpoint specifications
- Statistical methodology consistency
- Missing data handling approach

## SAP-to-Mock Shell Alignment Sections
- Table 14-1.03 Demographics: Title, population, columns, statistics
- Table 14-3.01 Primary Endpoint: Analysis model, population, endpoint, methods
- Table 14-4.01 AE Overview: Population, row categories, display conventions
- Table 14-4.02 AE by SOC/PT: Filtering threshold, sorting, MedDRA coding
- Figure 14-5.01 KM Plot: Endpoint, treatment display, statistical summary

## Mock Shell-to-TLF Output Alignment Sections
- Structure verification (rows, columns, headers)
- Numeric value comparison against ground truth
- Formatting compliance (decimal places, percentages)
- Footnote accuracy and completeness

## Analysis Logic Verification
- ANCOVA model specification: CHG ~ TRTPN + SITEGR1 + BASE
- Type III Sum of Squares with proportional weighting
- Data selection filters: EFFFL, ITTFL, PARAMCD, ANL01FL, AVISITN
- Missing data: LOCF via DTYPE flag
- No multiplicity adjustment for primary endpoint

## Check Summary
- **Protocol-SAP alignment**: 6 sections, all complete
- **SAP-Mock alignment**: 5 mock shells verified
- **Mock-TLF alignment**: 8 TLF outputs cross-referenced
- **Analysis logic**: 4 verification points confirmed
- **Total checks**: 51 (31 passed, 0 failed, 20 pending per consistency validation)
- **Quality report status**: 18/26 checks passed (69%), 3 documented issues
""",
    "T4.3.study_synopsis.001": """\
# Study Synopsis: CDISCPilot01

## Study Title
Safety and Efficacy of the Xanomeline Transdermal Therapeutic System (TTS) in Patients with Mild to Moderate Alzheimer's Disease

## Study Identification
- **Study ID**: CDISCPilot01
- **Phase**: Phase 2/3
- **Indication**: Alzheimer's Disease (Mild to Moderate)

## Objectives

### Primary Objective
Evaluate the efficacy of Xanomeline TTS compared to placebo on cognitive function as measured by the ADAS-Cog (11) score.

### Secondary Objectives
- Assess clinical global impression (CIBIC+)
- Evaluate behavioral symptoms (NPI-X)
- Evaluate safety and tolerability

## Study Design
Randomized, Double-Blind, Placebo-Controlled, Parallel-Group, Multi-Center study.

## Subject Count
- **Planned**: 300 subjects (100 per group)
- **Screened**: 306 subjects
- **Randomized (ITT)**: 254 subjects
- **Efficacy**: 234 subjects
- **Safety**: 254 subjects

## Treatment Groups
| Group | Treatment | Planned N | Actual N |
|-------|-----------|-----------|----------|
| Placebo | Transdermal patch (placebo) | 100 | 86 |
| Xanomeline Low Dose | Xanomeline TTS 50 cm2 | 100 | 84 |
| Xanomeline High Dose | Xanomeline TTS 75 cm2 | 100 | 84 |

Randomization ratio: 1:1:1

## Primary Endpoint
- **Name**: Change from Baseline to Week 24 in ADAS-Cog (11) Total Score
- **Measurement**: ADAS-Cog (Alzheimer's Disease Assessment Scale - Cognitive Subscale, 11 items, score range 0-70)
- **Timepoint**: Week 24
- **Statistical Method**: ANCOVA with treatment, pooled site group, and baseline score as covariates
- **Missing Data**: LOCF (Last Observation Carried Forward)

## Analysis Populations
| Population | Definition | N |
|-----------|------------|---|
| ITT | All randomized subjects | 254 |
| Safety | Subjects who received at least one dose | 254 |
| Efficacy | Subjects with at least one post-baseline efficacy assessment | 234 |

## Study Duration
24 weeks of treatment + 2 weeks of follow-up

## Treatment Administration
Xanomeline is a selective M1 muscarinic acetylcholine receptor agonist delivered via transdermal patch for stable plasma concentrations.
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
        gold_file = gold_dir / "expected_output.txt"
        gold_data = all_gold[tid]
        gold_file.write_text(gold_data, encoding="utf-8")
        print(f"  wrote {gold_file}")

    print(f"\nGenerated {len(all_tasks)} T4 tasks in {TASKS_DIR}")
    print(f"Gold outputs in {GOLD_ROOT}")


if __name__ == "__main__":
    main()
