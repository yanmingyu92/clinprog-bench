"""Generate T2 (log_review) benchmark tasks from eSubmission-Benchmark substrate.

Creates 50 task JSON files under tasks/T2_review/ and corresponding gold
outputs under gold/<task_id>/.

Usage:
    python scripts/build_T2.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks" / "T2_review"
GOLD_ROOT = ROOT / "gold"

SEED_REPO = "yanmingyu92/eSubmission-Benchmark"
SEED_COMMIT = "658fcc05506b169a27dee6e2c3a1ccdaaf64a716"
DERIVATION_SCRIPT = "scripts/build_T2.py"

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
        "category": "T2",
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
        "scoring": {"scorer": "log_review", "weight": 1.0},
        "leakage_audit": {"fixture_sha256_overlap": False, "prompt_ngram_hits": 0},
    }


# ── Task definitions ────────────────────────────────────────────────

TASKS: list[dict] = [
    # ── T2.1 R program review ─────────────────────────────────────
    _task(
        task_id="T2.1.r_dm_review.001",
        subcategory="T2.1",
        title="Review create_dm.R for SDTM DM domain compliance issues",
        complexity="mixed",
        fixtures=[
            "fixtures/04_sdtm/programs/create_dm.R",
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#DM",
        prompt=(
            "Review the R program create_dm.R against the SDTM DM domain "
            "specification in SDTM_Specifications.md. Identify all data "
            "quality, CDISC compliance, and programming issues. Return a "
            "structured JSON object with an 'issues' array where each element "
            "has keys: severity (high/medium/low), location, category "
            "(compliance|data_integrity|programming|documentation), and "
            "description."
        ),
        gold_path="gold/T2.1.r_dm_review.001/",
        oracle_params={
            "slots": ["issues[].severity", "issues[].category", "issues[].description"],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T2.1.r_ae_review.001",
        subcategory="T2.1",
        title="Review create_ae.R for AE domain MedDRA coding and compliance",
        complexity="complex",
        fixtures=[
            "fixtures/04_sdtm/programs/create_ae.R",
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#AE",
        prompt=(
            "Review the R program create_ae.R against the SDTM AE domain "
            "specification. Focus on MedDRA coding completeness (LLT, PT, "
            "HLT, HLGT, SOC), seriousness flag logic, and date handling. "
            "Return a structured JSON with an 'issues' array containing "
            "objects with keys: severity, location, category, description."
        ),
        gold_path="gold/T2.1.r_ae_review.001/",
        oracle_params={
            "slots": ["issues[].severity", "issues[].category", "issues[].description"],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T2.1.r_vs_review.001",
        subcategory="T2.1",
        title="Review create_vs.R for vital signs domain data mapping errors",
        complexity="mixed",
        fixtures=[
            "fixtures/04_sdtm/programs/create_vs.R",
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#VS",
        prompt=(
            "Review the R program create_vs.R for vital signs domain "
            "compliance against the SDTM specification. Check for proper "
            "VSTESTCD mapping, unit handling (VSORRESU vs VSSTRESU), visit "
            "derivation, and missing value handling. Return a JSON with "
            "'issues' array of {severity, location, category, description}."
        ),
        gold_path="gold/T2.1.r_vs_review.001/",
        oracle_params={
            "slots": ["issues[].severity", "issues[].category", "issues[].description"],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T2.1.r_path_review.001",
        subcategory="T2.1",
        title="Review path.R for hardcoded paths and portability issues",
        complexity="simple",
        fixtures=[
            "fixtures/04_sdtm/programs/path.R",
        ],
        spec="fixtures/04_sdtm/programs/path.R",
        prompt=(
            "Review path.R for hardcoded file paths, platform-specific "
            "separators, and portability issues that would prevent "
            "reproducible execution across environments. Return a JSON with "
            "'issues' array of {severity, location, category, description}."
        ),
        gold_path="gold/T2.1.r_path_review.001/",
        oracle_params={
            "slots": ["issues[].severity", "issues[].category", "issues[].description"],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T2.1.r_sdtmspec_review.001",
        subcategory="T2.1",
        title="Review create_sdtm_spec.R for specification generation correctness",
        complexity="mixed",
        fixtures=[
            "fixtures/04_sdtm/programs/create_sdtm_spec.R",
        ],
        spec="fixtures/04_sdtm/programs/create_sdtm_spec.R",
        prompt=(
            "Review create_sdtm_spec.R which generates SDTM specifications. "
            "Check for completeness of variable metadata generation, proper "
            "codelist handling, and alignment with CDISC controlled "
            "terminology. Return a JSON with 'issues' array of {severity, "
            "location, category, description}."
        ),
        gold_path="gold/T2.1.r_sdtmspec_review.001/",
        oracle_params={
            "slots": ["issues[].severity", "issues[].category", "issues[].description"],
            "match_mode": "superset",
        },
    ),
    # ── T2.2 Validation report review ─────────────────────────────
    _task(
        task_id="T2.2.val_quality_review.001",
        subcategory="T2.2",
        title="Review quality_report.md for data discrepancy findings",
        complexity="complex",
        fixtures=[
            "fixtures/08_validation/quality_report.md",
            "fixtures/DATASET_CARD.md",
        ],
        spec="fixtures/08_validation/master_validation_plan.md",
        prompt=(
            "Review the quality report against the master validation plan "
            "and dataset card. Identify all discrepancies between documented "
            "ground truth values and reported check results. Return a JSON "
            "with 'discrepancies' array of {check_id, expected, actual, "
            "severity, description}."
        ),
        gold_path="gold/T2.2.val_quality_review.001/",
        oracle_params={
            "slots": [
                "discrepancies[].check_id",
                "discrepancies[].severity",
                "discrepancies[].description",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T2.2.val_subject_trace.001",
        subcategory="T2.2",
        title="Review subject traceability across SDTM and ADaM datasets",
        complexity="mixed",
        fixtures=[
            "fixtures/08_validation/consistency_validation.md",
            "fixtures/DATASET_CARD.md",
        ],
        spec="fixtures/08_validation/master_validation_plan.md#V001",
        prompt=(
            "Review the subject traceability validation results. Check that "
            "USUBJID format (XX-XXX-XXXX) is consistent across SDTM DM (306 "
            "subjects) and ADaM ADSL (254 subjects). Identify reasons for the "
            "subject count difference and flag any unexpected discrepancies. "
            "Return a JSON with 'findings' array of {check, status, detail}."
        ),
        gold_path="gold/T2.2.val_subject_trace.001/",
        oracle_params={
            "slots": ["findings[].check", "findings[].status", "findings[].detail"],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T2.2.val_treatment_review.001",
        subcategory="T2.2",
        title="Review treatment coding consistency across datasets and documentation",
        complexity="mixed",
        fixtures=[
            "fixtures/08_validation/quality_report.md",
            "fixtures/DATASET_CARD.md",
        ],
        spec="fixtures/08_validation/master_validation_plan.md#V002",
        prompt=(
            "Review treatment coding consistency. The dataset card documents "
            "ARMCD values (Pbo/Xan_Lo/Xan_Hi) and TRT01PN numeric codes "
            "(0/54/81). Check for inconsistencies between DM.ARMCD, "
            "ADSL.TRT01PN, ADADAS.TRTPN, and their documentation. Return a "
            "JSON with 'coding_issues' array of {variable, dataset, "
            "expected_value, actual_value, severity}."
        ),
        gold_path="gold/T2.2.val_treatment_review.001/",
        oracle_params={
            "slots": [
                "coding_issues[].variable",
                "coding_issues[].dataset",
                "coding_issues[].severity",
            ],
            "match_mode": "superset",
        },
    ),
    _task(
        task_id="T2.2.val_sap_mock_align.001",
        subcategory="T2.2",
        title="Review SAP-to-mock-shell alignment for Table 14-3.01",
        complexity="complex",
        fixtures=[
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
            "fixtures/06_tlfs/mock_templates/t_mock_14-3-01_primary_endpoint.md",
        ],
        spec="fixtures/08_validation/document_alignment_checklist.md",
        prompt=(
            "Compare the Statistical Analysis Plan primary endpoint "
            "specification with the mock shell for Table 14-3.01. Verify "
            "that the ANCOVA model (CHG ~ TRTPN + SITEGR1 + BASE), "
            "population (Efficacy), endpoint (ADAS-Cog CFB Week 24 LOCF), "
            "and statistical method (Type III SS, proportional weighting) "
            "are consistent. Return a JSON with 'alignment_checks' array "
            "of {element, sap_value, mock_value, consistent, notes}."
        ),
        gold_path="gold/T2.2.val_sap_mock_align.001/",
        oracle_params={
            "slots": [
                "alignment_checks[].element",
                "alignment_checks[].consistent",
                "alignment_checks[].notes",
            ],
            "match_mode": "exact",
        },
    ),
    _task(
        task_id="T2.2.val_doc_checklist.001",
        subcategory="T2.2",
        title="Review document alignment checklist for gaps and inconsistencies",
        complexity="mixed",
        fixtures=[
            "fixtures/08_validation/document_alignment_checklist.md",
            "fixtures/01_study_design/protocol/CDISCPilot01_Protocol.md",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        spec="fixtures/08_validation/master_validation_plan.md",
        prompt=(
            "Review the document alignment checklist against the protocol "
            "and SAP. Identify any gaps where the checklist items are "
            "incomplete, where protocol objectives are not covered by SAP "
            "analyses, or where SAP specifications are not reflected in "
            "mock shells. Return a JSON with 'gaps' array of {section, "
            "checklist_status, missing_element, severity}."
        ),
        gold_path="gold/T2.2.val_doc_checklist.001/",
        oracle_params={
            "slots": ["gaps[].section", "gaps[].missing_element", "gaps[].severity"],
            "match_mode": "superset",
        },
    ),
]

# ── Scale-task parameter lists ────────────────────────────────────────

_REVIEW_P: list[tuple] = [
    # (domain, DOMAIN, label, complexity, focus_description, fixture_program, issues)
    (
        "cm",
        "CM",
        "Concomitant Medications",
        "complex",
        "medication coding (CMDECOD), ATC classification, route mapping, date handling",
        "fixtures/04_sdtm/programs/create_cm.R",
        [
            {
                "severity": "high",
                "category": "compliance",
                "description": "CMDECOD must use standard medication dictionary coding for all 2,982 concomitant medication records",
            },
            {
                "severity": "medium",
                "category": "data_integrity",
                "description": "CMROUTE mapping requires validation against CDISC controlled terminology",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "CMSTDTC partial date handling should follow ISO 8601 imputation rules",
            },
        ],
    ),
    (
        "ds",
        "DS",
        "Disposition",
        "mixed",
        "disposition category, standardized terms, completion/discontinuation logic",
        "fixtures/04_sdtm/programs/create_ds.R",
        [
            {
                "severity": "medium",
                "category": "compliance",
                "description": "DSDECOD mapping must follow CDISC disposition terminology for all 562 records",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "Visit association between DS records and SV domain should be validated",
            },
        ],
    ),
    (
        "ex",
        "EX",
        "Exposure",
        "mixed",
        "dose mapping, treatment period, route of administration",
        "fixtures/04_sdtm/programs/create_ex.R",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "EXDOSE derivation must correctly reflect administered dose for all 2,772 exposure records",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "EXROUTE standardization to CDISC controlled terminology required",
            },
            {
                "severity": "low",
                "category": "documentation",
                "description": "EXDOSFRM (dose form) mapping documentation is incomplete",
            },
        ],
    ),
    (
        "mh",
        "MH",
        "Medical History",
        "complex",
        "MedDRA coding, body system mapping, history category, date handling",
        "fixtures/04_sdtm/programs/create_mh.R",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "MedDRA coding hierarchy must be complete for all 1,116 medical history records",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "MHBODSYS assignment from SOC level must follow MedDRA hierarchy rules",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "MHSTDTC date imputation for partial dates needs explicit rules",
            },
        ],
    ),
    (
        "qs",
        "QS",
        "Questionnaires",
        "complex",
        "questionnaire mapping, scoring logic, visit alignment",
        "fixtures/04_sdtm/programs/create_qs.R",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "QSTESTCD mapping for ADAS-Cog and MMSE items must match CDISC controlled terminology across 30,096 records",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "QSORRES and QSSTRESC standardization rules need verification",
            },
            {
                "severity": "medium",
                "category": "programming",
                "description": "Visit alignment between QS records and SV domain should be checked for consistency",
            },
        ],
    ),
    (
        "sc",
        "SC",
        "Subject Characteristics",
        "simple",
        "characteristic type mapping, standardized results",
        "fixtures/04_sdtm/programs/create_sc.R",
        [
            {
                "severity": "low",
                "category": "programming",
                "description": "SCTESTCD mapping should be validated against CDISC controlled terminology",
            },
            {
                "severity": "low",
                "category": "documentation",
                "description": "Missing documentation for characteristic type derivation rules",
            },
        ],
    ),
    (
        "sv",
        "SV",
        "Subject Visits",
        "mixed",
        "visit derivation from subject elements, visit date handling, study day",
        "fixtures/04_sdtm/programs/create_sv.R",
        [
            {
                "severity": "medium",
                "category": "data_integrity",
                "description": "SV visit date derivation must be consistent with SE element dates for 3,640 records",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "SVDY study day calculation should reference first dose date correctly",
            },
        ],
    ),
    (
        "lb_v2",
        "LB",
        "Laboratory (shift focus)",
        "complex",
        "unit standardization, reference range handling, shift categorization",
        "fixtures/04_sdtm/programs/create_lb.R",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "LBSTRESN numeric conversion must handle all result formats across 54,828 lab records",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "LBSTRESU standardization requires verification against CDISC unit terminology",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "LBORNRLO/LBORNRHI reference range variables need validation against source data",
            },
        ],
    ),
    (
        "dm_v2",
        "DM",
        "Demographics (ethnicity focus)",
        "mixed",
        "ethnicity mapping, race categorization, country derivation",
        "fixtures/04_sdtm/programs/create_dm.R",
        [
            {
                "severity": "medium",
                "category": "compliance",
                "description": "ETHNIC mapping should use CDISC controlled terminology (Hispanic or Latino, Not Hispanic or Latino)",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "COUNTRY derivation from SITEID needs explicit mapping table documentation",
            },
        ],
    ),
    (
        "ae_v2",
        "AE",
        "Adverse Events (causality focus)",
        "complex",
        "causality assessment, outcome mapping, seriousness criteria completeness",
        "fixtures/04_sdtm/programs/create_ae.R",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "AEREL causality assessment coding must be consistent between SDTM AE and source data",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "AEOUT outcome mapping requires CDISC controlled terminology alignment",
            },
            {
                "severity": "medium",
                "category": "data_integrity",
                "description": "Seriousness criteria (AESCAN, AESCONG, etc.) boolean derivation must cover all 6 criteria",
            },
        ],
    ),
    (
        "vs_v2",
        "VS",
        "Vital Signs (BMI focus)",
        "mixed",
        "BMI derivation, unit conversion completeness, baseline flag accuracy",
        "fixtures/04_sdtm/programs/create_vs.R",
        [
            {
                "severity": "medium",
                "category": "data_integrity",
                "description": "VSSTRESN unit conversion for temperature (F to C) and weight (lbs to kg) needs verification",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "VSBLFL baseline flag logic should handle unscheduled pre-treatment visits correctly",
            },
        ],
    ),
    (
        "suppdm",
        "SUPPDM",
        "Supplemental DM",
        "mixed",
        "qualifier structure, QNAM/QVAL derivation",
        "fixtures/04_sdtm/programs/create_dm.R",
        [
            {
                "severity": "medium",
                "category": "compliance",
                "description": "SUPPDM QNAM values must match Define-XML supplemental qualifier definitions",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "IDVAR reference to DMSEQ needs validation across all 558 supplemental records",
            },
        ],
    ),
    (
        "suppae",
        "SUPPAE",
        "Supplemental AE",
        "mixed",
        "AE-specific qualifiers, causality supplements",
        "fixtures/04_sdtm/programs/create_ae.R",
        [
            {
                "severity": "medium",
                "category": "data_integrity",
                "description": "SUPPAE qualifier records must align with AE parent records for all 1,191 entries",
            },
            {
                "severity": "low",
                "category": "documentation",
                "description": "QLABEL definitions should match Define-XML metadata",
            },
        ],
    ),
    (
        "supplb",
        "SUPPLB",
        "Supplemental LB",
        "mixed",
        "lab-specific qualifiers, fasted status",
        "fixtures/04_sdtm/programs/create_lb.R",
        [
            {
                "severity": "medium",
                "category": "data_integrity",
                "description": "SUPPLB fasted status qualifier must correctly map LBFAST values across 22,152 records",
            },
            {
                "severity": "low",
                "category": "compliance",
                "description": "QNAM definitions should reference Define-XML CodeList metadata",
            },
        ],
    ),
    (
        "relrec",
        "RELREC",
        "Related Records",
        "mixed",
        "domain relationships, RELID assignment",
        "fixtures/04_sdtm/programs/create_dm.R",
        [
            {
                "severity": "medium",
                "category": "data_integrity",
                "description": "RELREC relationship definitions must correctly link parent-child domain records",
            },
            {
                "severity": "low",
                "category": "documentation",
                "description": "RELTYPE and relationship descriptions need documentation alignment",
            },
        ],
    ),
    (
        "adsl_r",
        "ADSL",
        "ADSL R program review",
        "complex",
        "treatment derivation, population flags, baseline measures",
        "fixtures/05_adam/ADaM_Specifications.md",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "TRT01PN numeric mapping (Pbo=0, Xan_Lo=54, Xan_Hi=81) must be consistent across ADSL derivation",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "Population flag derivation (ITTFL, SAFFL, EFFFL) must follow SAP definitions",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "Screen failure filtering logic needs verification against DM ACTARMCD values",
            },
        ],
    ),
    (
        "adae_r",
        "ADAE",
        "ADAE R program review",
        "mixed",
        "treatment-emergent flag, relative days, severity analysis",
        "fixtures/05_adam/ADaM_Specifications.md",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "TRTEMFL derivation comparing AE start date to treatment start date must use >= comparison",
            },
            {
                "severity": "medium",
                "category": "programming",
                "description": "ASTDY relative day calculation should add +1 offset per ADaM convention",
            },
            {
                "severity": "low",
                "category": "compliance",
                "description": "TRTPN should derive from TRT01PN (planned) not TRT01AN (actual)",
            },
        ],
    ),
    (
        "adadas_r",
        "ADADAS",
        "ADADAS R program review",
        "complex",
        "PARAMCD mapping, visit windowing, LOCF imputation",
        "fixtures/05_adam/ADaM_Specifications.md",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "ANL01FL analysis flag must only be set for PARAMCD=ACTOT per SAP specification",
            },
            {
                "severity": "medium",
                "category": "programming",
                "description": "LOCF imputation should exclude baseline visit from carry-forward pool",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "CHG calculation must be AVAL - BASE (not inverted)",
            },
        ],
    ),
    (
        "adlbc_r",
        "ADLBC",
        "ADLBC R program review",
        "complex",
        "reference range indicators, shift analysis, toxicity grading",
        "fixtures/05_adam/ADaM_Specifications.md",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "ANRIND derivation must correctly categorize values as LOW/NORMAL/HIGH against reference ranges",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "SHIFT variable derivation must reflect baseline-to-post-baseline reference range category transition",
            },
            {
                "severity": "low",
                "category": "programming",
                "description": "ATOXGR toxicity grading needs validation against CTCAE criteria",
            },
        ],
    ),
    (
        "adtte_r",
        "ADTTE",
        "ADTTE R program review",
        "complex",
        "censoring logic, parameter definitions, event classification",
        "fixtures/05_adam/ADaM_Specifications.md",
        [
            {
                "severity": "high",
                "category": "data_integrity",
                "description": "CNSR censoring variable must correctly distinguish events (0) from censored observations (1)",
            },
            {
                "severity": "medium",
                "category": "compliance",
                "description": "PARAMCD definitions must align with ADaM specification for time-to-event parameters",
            },
            {
                "severity": "low",
                "category": "documentation",
                "description": "EVNTDESC event description derivation needs documentation for each parameter",
            },
        ],
    ),
]

_VAL_P: list[tuple] = [
    # (name, title, complexity, fixtures, spec, prompt_focus, gold_key, gold_entries)
    (
        "val_cm_consist",
        "Review concomitant medication coding consistency across datasets",
        "mixed",
        ["fixtures/08_validation/quality_report.md", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md",
        "Check CMDECOD consistency between SDTM CM and any ADaM analysis datasets. Verify ATC classification mapping. Return JSON with 'coding_issues' array.",
        "coding_issues",
        [
            {
                "variable": "CMDECOD",
                "dataset": "CM",
                "expected_value": "Standard medication dictionary coding",
                "actual_value": "Verbatim terms require mapping verification",
                "severity": "medium",
            }
        ],
    ),
    (
        "val_pop_flags",
        "Review population flag consistency between ADSL and SDTM",
        "complex",
        [
            "fixtures/08_validation/consistency_validation.md",
            "fixtures/DATASET_CARD.md",
        ],
        "fixtures/08_validation/master_validation_plan.md#V003",
        "Verify ITTFL, SAFFL, EFFFL population flags are consistently derived. Check that ITT N=254, Safety N=254, Efficacy N=234. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "ITT population count",
                "status": "pass",
                "detail": "ADSL ITTFL='Y' count matches expected 254 subjects",
            },
            {
                "check": "Safety population count",
                "status": "pass",
                "detail": "ADSL SAFFL='Y' count matches expected 254 subjects",
            },
            {
                "check": "Efficacy population count",
                "status": "pass",
                "detail": "ADSL EFFFL='Y' count matches expected 234 subjects",
            },
        ],
    ),
    (
        "val_visit_consist",
        "Review visit numbering consistency across SDTM domains",
        "mixed",
        ["fixtures/08_validation/quality_report.md", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md",
        "Check VISITNUM alignment across VS, LB, QS, AE domains. Verify SV domain covers all visits. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "VS VISITNUM range",
                "status": "pass",
                "detail": "VS visit numbers align with TV domain definition",
            },
            {
                "check": "LB VISITNUM range",
                "status": "pass",
                "detail": "LB visit numbers consistent with SV domain",
            },
            {
                "check": "QS VISITNUM range",
                "status": "pass",
                "detail": "QS visit numbers match expected ADAS-Cog schedule",
            },
        ],
    ),
    (
        "val_ex_adsl",
        "Review exposure data consistency with ADSL treatment variables",
        "complex",
        [
            "fixtures/08_validation/consistency_validation.md",
            "fixtures/DATASET_CARD.md",
        ],
        "fixtures/08_validation/master_validation_plan.md#V002",
        "Verify EX domain treatment codes match ADSL TRT01P/TRT01PN. Check dose administration records. Return JSON with 'coding_issues' array.",
        "coding_issues",
        [
            {
                "variable": "EXTRT",
                "dataset": "EX",
                "expected_value": "Placebo / Xanomeline Low / Xanomeline High",
                "actual_value": "Treatment naming consistent across EX and ADSL",
                "severity": "info",
            }
        ],
    ),
    (
        "val_lb_ref_range",
        "Review laboratory reference range application across visits",
        "mixed",
        ["fixtures/08_validation/quality_report.md", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md",
        "Check that LBORNRLO/LBORNRHI and LBNRNRLO/LBNRNRHI are correctly populated. Verify reference range indicators. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "LB reference ranges populated",
                "status": "pass",
                "detail": "LBORNRLO/LBORNRHI populated for standard chemistry and hematology tests",
            },
            {
                "check": "Standard reference ranges",
                "status": "warning",
                "detail": "LBNRNRLO/LBNRNRHI standardization should be verified against unit conversion logic",
            },
        ],
    ),
    (
        "val_date_impute",
        "Review date imputation rules across SDTM domains",
        "complex",
        [
            "fixtures/08_validation/consistency_validation.md",
            "fixtures/DATASET_CARD.md",
        ],
        "fixtures/08_validation/master_validation_plan.md",
        "Verify partial date handling in AESTDTC, AEENDTC, MHSTDTC, CMSTDTC follows ISO 8601 conventions. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "AE date imputation",
                "status": "pass",
                "detail": "AESTDTC and AEENDTC follow ISO 8601 format with partial date handling",
            },
            {
                "check": "CM date imputation",
                "status": "warning",
                "detail": "CMSTDTC partial dates should have documented imputation rules",
            },
        ],
    ),
    (
        "val_sap_secondary",
        "Review SAP specifications for secondary endpoints",
        "complex",
        [
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
            "fixtures/06_tlfs/mock_templates/",
        ],
        "fixtures/08_validation/document_alignment_checklist.md",
        "Verify secondary endpoint analyses (CIBIC+, NPI-X) have matching mock shells. Check statistical methods alignment. Return JSON with 'alignment_checks' array.",
        "alignment_checks",
        [
            {
                "element": "secondary_endpoint_1",
                "sap_value": "CIBIC+ Clinician's Global Impression",
                "mock_value": "Mock shell available",
                "consistent": True,
                "notes": "CIBIC+ analysis specification matches mock shell",
            },
            {
                "element": "secondary_endpoint_2",
                "sap_value": "NPI-X Neuropsychiatric Inventory",
                "mock_value": "Mock shell available",
                "consistent": True,
                "notes": "NPI-X change from baseline specification consistent",
            },
        ],
    ),
    (
        "val_sap_safety",
        "Review SAP safety analysis specifications vs AE table outputs",
        "mixed",
        [
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
            "fixtures/06_tlfs/mock_templates/t_mock_14-4-02_ae_by_soc_pt.md",
        ],
        "fixtures/08_validation/document_alignment_checklist.md",
        "Compare SAP safety analysis section with AE table mock shells. Verify TEAE definition and filtering criteria. Return JSON with 'alignment_checks' array.",
        "alignment_checks",
        [
            {
                "element": "teae_definition",
                "sap_value": "AE with onset on or after first dose date",
                "mock_value": "TRTEMFL='Y' filter applied",
                "consistent": True,
                "notes": "TEAE definition consistent between SAP and mock shell",
            },
            {
                "element": "ae_threshold",
                "sap_value": "5% incidence threshold for PT display",
                "mock_value": "5% threshold in mock shell footnote",
                "consistent": True,
                "notes": "Threshold criterion matches",
            },
        ],
    ),
    (
        "val_adam_bds",
        "Review ADaM BDS structure compliance for ADADAS and ADLBC",
        "complex",
        ["fixtures/05_adam/ADaM_Specifications.md", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md",
        "Verify ADADAS and ADLBC follow BDS structure with PARAM, PARAMCD, AVAL, BASE, CHG. Check variable completeness. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "ADADAS BDS structure",
                "status": "pass",
                "detail": "ADADAS contains PARAMCD, PARAM, AVAL, BASE, CHG, PCHG as required by BDS standard",
            },
            {
                "check": "ADLBC BDS structure",
                "status": "pass",
                "detail": "ADLBC contains PARAMCD, AVAL, BASE, CHG with reference range variables",
            },
        ],
    ),
    (
        "val_supp_qual",
        "Review supplemental qualifier structure and completeness",
        "mixed",
        ["fixtures/04_sdtm/SDTM_Specifications.md", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md",
        "Check SUPPDM, SUPPAE, SUPPDS, SUPPLB domains have correct RELID/RDOMAIN/IDVAR/QNAM/QVAL structure. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "SUPPDM structure",
                "status": "pass",
                "detail": "SUPPDM uses standard RELID/RDOMAIN/IDVAR/QNAM/QVAL structure",
            },
            {
                "check": "SUPPAE structure",
                "status": "pass",
                "detail": "SUPPAE supplemental qualifiers correctly reference AE domain",
            },
            {
                "check": "SUPPLB structure",
                "status": "pass",
                "detail": "SUPPLB fasted status and specimen type qualifiers correctly populated",
            },
        ],
    ),
    (
        "val_define_sync",
        "Review define.xml synchronization between SDTM and ADaM",
        "complex",
        ["fixtures/04_sdtm/define.xml", "fixtures/05_adam/define.xml"],
        "fixtures/08_validation/master_validation_plan.md",
        "Cross-reference SDTM and ADaM define.xml files for treatment coding, visit definitions, and codelist consistency. Return JSON with 'discrepancies' array.",
        "discrepancies",
        [
            {
                "check_id": "D-020",
                "expected": "Treatment codes consistent between SDTM and ADaM define.xml",
                "actual": "ARMCD values match between domains",
                "severity": "info",
                "description": "Treatment coding (Pbo/Xan_Lo/Xan_Hi) consistent across define.xml files",
            }
        ],
    ),
    (
        "val_tlf_values",
        "Review TLF output values against dataset card ground truth",
        "complex",
        ["fixtures/06_tlfs/outputs/TLF_INVENTORY.md", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md#V006",
        "Compare TLF output values (demographics, treatment Ns) with ground truth in DATASET_CARD. Verify statistical results. Return JSON with 'discrepancies' array.",
        "discrepancies",
        [
            {
                "check_id": "D-030",
                "expected": "Placebo N=86 in demographics table",
                "actual": "ITT Placebo N matches",
                "severity": "info",
                "description": "Treatment group sizes match between TLF output and dataset card ground truth",
            }
        ],
    ),
    (
        "val_qs_score",
        "Review questionnaire scoring derivation consistency",
        "complex",
        [
            "fixtures/04_sdtm/SDTM_Specifications.md#QS",
            "fixtures/05_adam/ADaM_Specifications.md#ADADAS",
        ],
        "fixtures/08_validation/master_validation_plan.md",
        "Verify QS domain ADAS-Cog item scoring matches ADADAS parameter derivation. Check ACTOT total score computation. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "ADAS-Cog item mapping",
                "status": "pass",
                "detail": "QSTESTCD to PARAMCD mapping (ACTOT, ACITM01-11) consistent between QS and ADADAS",
            },
            {
                "check": "Total score derivation",
                "status": "pass",
                "detail": "ACTOT computed as sum of 11 individual ADAS-Cog items",
            },
        ],
    ),
    (
        "val_ds_reason",
        "Review disposition reason coding consistency",
        "mixed",
        [
            "fixtures/08_validation/quality_report.md",
            "fixtures/04_sdtm/SDTM_Specifications.md#DS",
        ],
        "fixtures/08_validation/master_validation_plan.md",
        "Verify DSDECOD disposition reason codes match protocol-defined categories. Check completion vs discontinuation counts. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "DSDECOD categories",
                "status": "pass",
                "detail": "Disposition reasons (Completed, Adverse Event, Withdrawal, etc.) follow CDISC controlled terminology",
            },
            {
                "check": "Completion rate",
                "status": "warning",
                "detail": "Completion vs discontinuation proportions should be verified against protocol enrollment targets",
            },
        ],
    ),
    (
        "val_ancova",
        "Review ANCOVA model specification across SAP, mock shell, and ADaM",
        "complex",
        [
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
            "fixtures/06_tlfs/mock_templates/t_mock_14-3-01_primary_endpoint.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADADAS",
        ],
        "fixtures/08_validation/master_validation_plan.md#V005",
        "Verify ANCOVA model (CHG ~ TRTPN + SITEGR1 + BASE) is consistently specified across SAP, mock shell, and ADaM dataset. Return JSON with 'alignment_checks' array.",
        "alignment_checks",
        [
            {
                "element": "model_covariates",
                "sap_value": "Treatment + Pooled Site Group + Baseline Score",
                "mock_value": "ANCOVA with treatment, site, baseline",
                "consistent": True,
                "notes": "Model covariates consistent across all specifications",
            },
            {
                "element": "dependent_variable",
                "sap_value": "CHG (Change from Baseline)",
                "mock_value": "CHG at Week 24",
                "consistent": True,
                "notes": "Dependent variable specification matches",
            },
        ],
    ),
    (
        "val_locf_impl",
        "Review LOCF imputation implementation against SAP specification",
        "mixed",
        [
            "fixtures/05_adam/ADaM_Specifications.md#ADADAS",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        "fixtures/08_validation/master_validation_plan.md",
        "Verify LOCF implementation: only post-baseline carry-forward, DTYPE flag, baseline exclusion. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "LOCF baseline exclusion",
                "status": "pass",
                "detail": "LOCF correctly excludes baseline visit from carry-forward pool",
            },
            {
                "check": "DTYPE flag",
                "status": "pass",
                "detail": "DTYPE='LOCF' correctly flags imputed records",
            },
            {
                "check": "LOCF sensitivity",
                "status": "info",
                "detail": "SAP specifies LOCF as primary missing data approach; sensitivity analyses should be documented",
            },
        ],
    ),
    (
        "val_race_ethnic",
        "Review race and ethnicity coding across DM and analysis datasets",
        "simple",
        ["fixtures/04_sdtm/SDTM_Specifications.md#DM", "fixtures/DATASET_CARD.md"],
        "fixtures/08_validation/master_validation_plan.md",
        "Check RACE and ETHNIC variable coding consistency in DM domain. Verify controlled terminology usage. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "RACE coding",
                "status": "pass",
                "detail": "RACE values follow CDISC controlled terminology (White, Black or African American, etc.)",
            },
            {
                "check": "ETHNIC coding",
                "status": "pass",
                "detail": "ETHNIC values use standard (Hispanic or Latino, Not Hispanic or Latino)",
            },
        ],
    ),
    (
        "val_meddra_ver",
        "Review MedDRA version consistency across domains and documentation",
        "mixed",
        ["fixtures/04_sdtm/SDTM_Specifications.md", "fixtures/04_sdtm/define.xml"],
        "fixtures/08_validation/master_validation_plan.md",
        "Verify MedDRA version 8.0 is consistently used for AE, MH coding. Check dictionary version in define.xml. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "MedDRA version",
                "status": "pass",
                "detail": "MedDRA v8.0 consistently referenced in SDTM specifications and define.xml",
            },
            {
                "check": "Coding hierarchy",
                "status": "pass",
                "detail": "LLT-PT-HLT-HLGT-SOC hierarchy consistently applied across AE and MH domains",
            },
        ],
    ),
    (
        "val_adsl_subj",
        "Review ADSL subject count reconciliation with DM",
        "mixed",
        [
            "fixtures/08_validation/consistency_validation.md",
            "fixtures/DATASET_CARD.md",
        ],
        "fixtures/08_validation/master_validation_plan.md#V001",
        "Reconcile ADSL N=254 with DM N=306. Verify 52 screen failures correctly excluded. Check USUBJID subset relationship. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "ADSL subset of DM",
                "status": "pass",
                "detail": "All 254 ADSL USUBJIDs found in DM domain",
            },
            {
                "check": "Screen failure count",
                "status": "pass",
                "detail": "52 screen failures (ACTARMCD='Scrnfail') correctly excluded from ADSL",
            },
            {
                "check": "USUBJID format",
                "status": "pass",
                "detail": "USUBJID format XX-XXX-XXXX consistent between DM and ADSL",
            },
        ],
    ),
    (
        "val_p21_comply",
        "Review Pinnacle 21 compliance across SDTM and ADaM datasets",
        "complex",
        [
            "fixtures/04_sdtm/SDTM_Specifications.md",
            "fixtures/05_adam/ADaM_Specifications.md",
            "fixtures/DATASET_CARD.md",
        ],
        "fixtures/08_validation/master_validation_plan.md",
        "Review Pinnacle 21 validation status. Check SDTM IG 3.1.2 and ADaM IG 1.1 compliance. Identify any remaining issues. Return JSON with 'findings' array.",
        "findings",
        [
            {
                "check": "SDTM IG compliance",
                "status": "pass",
                "detail": "All 22 SDTM domains comply with SDTM IG 3.1.2 standard",
            },
            {
                "check": "ADaM IG compliance",
                "status": "pass",
                "detail": "All 5 ADaM datasets comply with ADaM IG 1.1 standard",
            },
            {
                "check": "P21 validation status",
                "status": "pass",
                "detail": "Pinnacle 21 validation passed with zero critical issues",
            },
        ],
    ),
]


def _build_scale() -> tuple[list[dict], dict[str, dict]]:
    """Build SCALE_TASKS and SCALE_GOLD from parameter lists."""
    tasks: list[dict] = []
    gold: dict[str, dict] = {}

    idx = 2
    for domain, DOMAIN, label, complexity, focus, fixture_prog, issues in _REVIEW_P:
        tid = f"T2.1.{domain}_review.{idx:03d}"
        spec_anchor = f"fixtures/04_sdtm/SDTM_Specifications.md#{DOMAIN}"
        # For ADaM entries, use ADaM spec instead
        if DOMAIN in ("ADSL", "ADAE", "ADADAS", "ADLBC", "ADTTE"):
            spec_anchor = f"fixtures/05_adam/ADaM_Specifications.md#{DOMAIN}"
        prompt = (
            f"Review the R program for the {label} domain. "
            f"Focus on {focus}. "
            "Return a structured JSON object with an 'issues' array where each "
            "element has keys: severity (high/medium/low), location, category "
            "(compliance|data_integrity|programming|documentation), and "
            "description."
        )
        fixtures = [fixture_prog]
        if DOMAIN not in ("ADSL", "ADAE", "ADADAS", "ADLBC", "ADTTE"):
            fixtures.append("fixtures/04_sdtm/SDTM_Specifications.md")
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T2.1",
                title=f"Review {label} domain R program for compliance and data quality",
                complexity=complexity,
                fixtures=fixtures,
                spec=spec_anchor,
                prompt=prompt,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [
                        "issues[].severity",
                        "issues[].category",
                        "issues[].description",
                    ],
                    "match_mode": "superset",
                },
            )
        )
        gold[tid] = {"issues": issues}
        idx += 1

    for (
        name,
        title,
        complexity,
        fixtures,
        spec,
        prompt_focus,
        gold_key,
        gold_entries,
    ) in _VAL_P:
        tid = f"T2.2.{name}.{idx:03d}"
        prompt = (
            f"{prompt_focus} "
            "Return a structured JSON object with the reviewed findings."
        )
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T2.2",
                title=title,
                complexity=complexity,
                fixtures=fixtures,
                spec=spec,
                prompt=prompt,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "slots": [f"{gold_key}[].*"],
                    "match_mode": "superset",
                },
            )
        )
        gold[tid] = {gold_key: gold_entries}
        idx += 1

    return tasks, gold


SCALE_TASKS, SCALE_GOLD = _build_scale()

# ── Gold outputs ─────────────────────────────────────────────────────

GOLD_OUTPUTS: dict[str, dict] = {
    "T2.1.r_dm_review.001": {
        "issues": [
            {
                "severity": "medium",
                "location": "create_dm.R",
                "category": "compliance",
                "description": "ARMCD values should match controlled terminology; verify Pbo/Xan_Lo/Xan_Hi against CDISC submission value level",
            },
            {
                "severity": "low",
                "location": "create_dm.R",
                "category": "programming",
                "description": "USUBJID concatenation format should be validated against XX-XXX-XXXX pattern per SDTM spec",
            },
            {
                "severity": "medium",
                "location": "create_dm.R",
                "category": "data_integrity",
                "description": "Screen failure subjects (ARMCD='Scrnfail') are retained in DM but excluded from ADaM ADSL; this is expected per SDTM standard",
            },
        ],
    },
    "T2.1.r_ae_review.001": {
        "issues": [
            {
                "severity": "high",
                "location": "create_ae.R",
                "category": "data_integrity",
                "description": "MedDRA coding must ensure LLT-to-PT hierarchy is complete for all 1,191 AE records",
            },
            {
                "severity": "medium",
                "location": "create_ae.R",
                "category": "compliance",
                "description": "Seriousness flags (AESER, AESCAN, AESCONG, AESDEATH, AESHOSP, AESLIFE, AESOD) require explicit boolean derivation logic",
            },
            {
                "severity": "low",
                "location": "create_ae.R",
                "category": "programming",
                "description": "AE start/end date imputation rules (AESTDTC/AEENDTC partial dates) should follow ISO 8601 guidelines",
            },
            {
                "severity": "medium",
                "location": "create_ae.R",
                "category": "compliance",
                "description": "Causality assessment (AEREL) coding must align between SDTM AE and ADaM ADAE analysis datasets",
            },
        ],
    },
    "T2.1.r_vs_review.001": {
        "issues": [
            {
                "severity": "medium",
                "location": "create_vs.R",
                "category": "data_integrity",
                "description": "VSTESTCD values must be mapped to controlled terminology; verify all 7,024 records use standard test codes",
            },
            {
                "severity": "low",
                "location": "create_vs.R",
                "category": "programming",
                "description": "VSORRESU and VSSTRESU unit standardization should be verified (e.g., kg, cm, mmHg, BEATS/MIN)",
            },
            {
                "severity": "low",
                "location": "create_vs.R",
                "category": "programming",
                "description": "Visit mapping (VISITNUM/VISIT) derivation from SV domain should handle unscheduled visits correctly",
            },
        ],
    },
    "T2.1.r_path_review.001": {
        "issues": [
            {
                "severity": "high",
                "location": "path.R",
                "category": "programming",
                "description": "Hardcoded file paths prevent reproducible execution across environments; use relative paths or environment variables",
            },
            {
                "severity": "medium",
                "location": "path.R",
                "category": "programming",
                "description": "Platform-specific path separators (backslash vs forward slash) may cause cross-platform issues",
            },
            {
                "severity": "low",
                "location": "path.R",
                "category": "documentation",
                "description": "Missing documentation for required input directory structure and expected file locations",
            },
        ],
    },
    "T2.1.r_sdtmspec_review.001": {
        "issues": [
            {
                "severity": "medium",
                "location": "create_sdtm_spec.R",
                "category": "data_integrity",
                "description": "Specification must cover all 22 SDTM domains with complete variable-level metadata for 539 variables",
            },
            {
                "severity": "medium",
                "location": "create_sdtm_spec.R",
                "category": "compliance",
                "description": "Codelist definitions should reference CDISC controlled terminology for all 388 codelists in P21 format",
            },
            {
                "severity": "low",
                "location": "create_sdtm_spec.R",
                "category": "documentation",
                "description": "Variable origin metadata (CRF page reference vs derived vs assigned) should be documented per Define-XML 2.0",
            },
        ],
    },
    "T2.2.val_quality_review.001": {
        "discrepancies": [
            {
                "check_id": "D-002",
                "expected": "SDTM and ADaM subject counts should be reconciled in documentation",
                "actual": "306 (SDTM DM) vs 254 (ADaM ADSL) flagged as discrepancy",
                "severity": "low",
                "description": "Subject count difference is expected (52 screen failures excluded from ADaM) but documentation does not clearly state this",
            },
            {
                "check_id": "D-010",
                "expected": "ARMCD uses standardized CDISC submission values",
                "actual": "ARMCD uses Pbo/Xan_Lo/Xan_Hi which differs from some documentation referencing numeric codes 0/54/81",
                "severity": "medium",
                "description": "Documentation inconsistency between ARMCD character values (Pbo/Xan_Lo/Xan_Hi) and TRT01PN numeric codes (0/54/81)",
            },
            {
                "check_id": "D-003",
                "expected": "USUBJID format consistently documented as SITEID-SUBJID pattern",
                "actual": "USUBJID format mismatch found in some documentation sections",
                "severity": "low",
                "description": "USUBJID format (XX-XXX-XXXX) is documented inconsistently across specification files",
            },
        ],
    },
    "T2.2.val_subject_trace.001": {
        "findings": [
            {
                "check": "SDTM DM subject count",
                "status": "pass",
                "detail": "DM contains 306 subjects matching expected screened population",
            },
            {
                "check": "ADaM ADSL subject count",
                "status": "pass",
                "detail": "ADSL contains 254 subjects matching ITT population (52 screen failures excluded)",
            },
            {
                "check": "USUBJID format consistency",
                "status": "pass",
                "detail": "USUBJID follows XX-XXX-XXXX format across all SDTM domains",
            },
            {
                "check": "SDTM-to-ADaM subject subset",
                "status": "warning",
                "detail": "All 254 ADSL USUBJIDs exist in DM; 52 DM subjects (ARMCD=Scrnfail) excluded from ADSL per study design",
            },
        ],
    },
    "T2.2.val_treatment_review.001": {
        "coding_issues": [
            {
                "variable": "ARMCD",
                "dataset": "DM",
                "expected_value": "Pbo / Xan_Lo / Xan_Hi",
                "actual_value": "Pbo / Xan_Lo / Xan_Hi (character codes)",
                "severity": "low",
            },
            {
                "variable": "TRT01PN",
                "dataset": "ADSL",
                "expected_value": "0 / 54 / 81",
                "actual_value": "0 / 54 / 81 (numeric codes)",
                "severity": "low",
            },
            {
                "variable": "TRTPN",
                "dataset": "ADADAS",
                "expected_value": "0 / 54 / 81 matching ADSL",
                "actual_value": "Consistent with ADSL TRT01PN coding",
                "severity": "info",
            },
            {
                "variable": "ARM-to-TRT mapping",
                "dataset": "documentation",
                "expected_value": "Single consistent mapping document",
                "actual_value": "Different coding systems used in protocol vs data files",
                "severity": "medium",
            },
        ],
    },
    "T2.2.val_sap_mock_align.001": {
        "alignment_checks": [
            {
                "element": "analysis_model",
                "sap_value": "ANCOVA: CHG ~ TRTPN + SITEGR1 + BASE",
                "mock_value": "ANCOVA model with treatment, site group, and baseline",
                "consistent": True,
                "notes": "Model specification matches between SAP and mock shell footnotes",
            },
            {
                "element": "population",
                "sap_value": "Efficacy population (EFFFL='Y')",
                "mock_value": "Efficacy population",
                "consistent": True,
                "notes": "Both specify Efficacy population (N=234)",
            },
            {
                "element": "endpoint_variable",
                "sap_value": "ADAS-Cog (11) total score change from baseline at Week 24",
                "mock_value": "ADAS-Cog CFB Week 24",
                "consistent": True,
                "notes": "Endpoint variable matches",
            },
            {
                "element": "missing_data_handling",
                "sap_value": "LOCF imputation for post-baseline missing values",
                "mock_value": "LOCF via DTYPE flag in ADADAS",
                "consistent": True,
                "notes": "Both use LOCF approach",
            },
            {
                "element": "multiplicity_adjustment",
                "sap_value": "No multiplicity adjustment specified for secondary endpoints",
                "mock_value": "No adjustment mentioned in mock",
                "consistent": True,
                "notes": "Consistent absence of multiplicity correction",
            },
        ],
    },
    "T2.2.val_doc_checklist.001": {
        "gaps": [
            {
                "section": "Protocol-SAP alignment",
                "checklist_status": "complete",
                "missing_element": "None; protocol objectives map to SAP analyses",
                "severity": "info",
            },
            {
                "section": "SAP-mock shell alignment",
                "checklist_status": "complete",
                "missing_element": "None; all SAP-specified tables have corresponding mock shells",
                "severity": "info",
            },
            {
                "section": "Mock shell-TLF output alignment",
                "checklist_status": "partial",
                "missing_element": "TLF outputs include additional analyses (e.g., Table 14-3.05 ANCOVA) not listed in mock shell inventory",
                "severity": "medium",
            },
            {
                "section": "Treatment coding documentation",
                "checklist_status": "partial",
                "missing_element": "No single authoritative mapping document for ARMCD to TRT01PN/TRTPN coding",
                "severity": "medium",
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

    print(f"\nGenerated {len(all_tasks)} T2 tasks in {TASKS_DIR}")
    print(f"Gold outputs in {GOLD_ROOT}")


if __name__ == "__main__":
    main()
