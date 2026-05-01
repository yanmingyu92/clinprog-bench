"""Generate T5 (debug) benchmark tasks from eSubmission-Benchmark substrate.

Creates 50 task JSON files under tasks/T5_debug/ and corresponding gold
patch outputs under gold/<task_id>/.

Each task provides a buggy SAS or R program with known defects. The agent
must identify and fix all bugs. Gold output is a unified diff patch.

Usage:
    python scripts/build_T5.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks" / "T5_debug"
GOLD_ROOT = ROOT / "gold"

SEED_REPO = "anonymous/eSubmission-Benchmark"
SEED_COMMIT = "658fcc05506b169a27dee6e2c3a1ccdaaf64a716"
DERIVATION_SCRIPT = "scripts/build_T5.py"

# ── Shared building blocks ──────────────────────────────────────────


def _provenance() -> dict:
    return {
        "seed_repo": SEED_REPO,
        "seed_commit": SEED_COMMIT,
        "derivation_script": DERIVATION_SCRIPT,
        "human_authors": ["R02"],
        "human_reviewers": ["R01"],
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
        "category": "T5",
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
            "kind": "patch",
            "gold_path": gold_path,
            "oracle": {"type": "patch_apply", "params": oracle_params},
        },
        "scoring": {"scorer": "debug", "weight": 1.0},
        "leakage_audit": {"fixture_sha256_overlap": False, "prompt_ngram_hits": 0},
    }


def _patch_gold_t(
    domain: str,
    bug_descs: list[str],
    fix_descs: list[str],
    fix_locs: list[str],
    *,
    ext: str = ".sas",
) -> str:
    """Generate a unified diff patch string for gold output."""
    stem = domain.lower()
    lines = [f"--- a/{stem}_prog{ext}", f"+++ b/{stem}_prog{ext}"]
    for i, (bug, fix) in enumerate(zip(bug_descs, fix_descs, strict=False), 1):
        lines.append("@@ -1,5 +1,5 @@")
        lines.append(f"-Bug {i}: {bug}")
        lines.append(f"+Fix {i}: {fix}")
    lines.append("")
    lines.append("Summary of fixes:")
    for i, (fix, loc) in enumerate(zip(fix_descs, fix_locs, strict=False), 1):
        lines.append(f"{i}. {fix} ({loc})")
    return "\n".join(lines)


# ── Task definitions ────────────────────────────────────────────────

TASKS: list[dict] = [
    # ── T5.1 SDTM program bugs ────────────────────────────────────
    _task(
        task_id="T5.1.sdtm_dm_debug.001",
        subcategory="T5.1",
        title="Debug SDTM DM domain program: USUBJID derivation and ARM mapping errors",
        complexity="mixed",
        fixtures=[
            "fixtures/04_sdtm/programs/create_dm.R",
            "fixtures/04_sdtm/SDTM_Specifications.md#DM",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#DM",
        prompt=(
            "The following SAS program is intended to create the SDTM DM "
            "domain but contains 3 bugs: (1) USUBJID is constructed using "
            "SUBJID-SITEID order instead of STUDYID-SITEID-SUBJID, (2) "
            "ARMCD mapping for Xanomeline Low Dose uses incorrect code "
            "'Xan_lo' (lowercase L) instead of 'Xan_Lo', (3) the AGE "
            "calculation uses BRTHDTC directly without converting to a SAS "
            "date value. Fix all bugs and return the corrected program."
        ),
        gold_path="gold/T5.1.sdtm_dm_debug.001/",
        oracle_params={
            "bug_count": 3,
            "fix_locations": ["USUBJID_derivation", "ARMCD_mapping", "AGE_calculation"],
        },
    ),
    _task(
        task_id="T5.1.sdtm_ae_debug.001",
        subcategory="T5.1",
        title="Debug SDTM AE program: seriousness flag logic and MedDRA hierarchy errors",
        complexity="complex",
        fixtures=[
            "fixtures/04_sdtm/programs/create_ae.R",
            "fixtures/04_sdtm/SDTM_Specifications.md#AE",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#AE",
        prompt=(
            "The following SAS program creates the SDTM AE domain but has "
            "4 bugs: (1) The seriousness flag AESER is set based on only "
            "AESHOSP and AESDEATH but omits AESCAN, AESCONG, AESLIFE, and "
            "AESOD criteria, (2) AESEQ is not retained and reset per "
            "observation instead of incrementing within each USUBJID, "
            "(3) The MedDRA hierarchy assigns AEBODSYS from HLT instead of "
            "SOC, causing incorrect body system mapping, (4) AESTDTC date "
            "conversion uses is8601dt. (datetime) instead of is8601da. "
            "(date-only). Fix all bugs."
        ),
        gold_path="gold/T5.1.sdtm_ae_debug.001/",
        oracle_params={
            "bug_count": 4,
            "fix_locations": [
                "AESER_logic",
                "AESEQ_retain",
                "AEBODSYS_mapping",
                "AESTDTC_format",
            ],
        },
    ),
    _task(
        task_id="T5.1.sdtm_vs_debug.001",
        subcategory="T5.1",
        title="Debug SDTM VS domain program: baseline flag and unit conversion errors",
        complexity="mixed",
        fixtures=[
            "fixtures/04_sdtm/programs/create_vs.R",
            "fixtures/04_sdtm/SDTM_Specifications.md#VS",
        ],
        spec="fixtures/04_sdtm/SDTM_Specifications.md#VS",
        prompt=(
            "The following SAS program creates the SDTM VS domain but has "
            "3 bugs: (1) VSBLFL (baseline flag) is set to 'Y' when "
            "VISITDY > 0 (post-baseline) instead of VISITDY <= 0 "
            "(pre-baseline), (2) Temperature unit conversion from "
            "Fahrenheit to Celsius uses (F - 32) / 1.2 instead of the "
            "correct formula (F - 32) * 5/9, (3) VSTESTCD for Diastolic "
            "Blood Pressure is mapped as 'DBP' instead of 'DIABP' per "
            "CDISC controlled terminology. Fix all bugs."
        ),
        gold_path="gold/T5.1.sdtm_vs_debug.001/",
        oracle_params={
            "bug_count": 3,
            "fix_locations": [
                "VSBLFL_condition",
                "TEMP_conversion",
                "VSTESTCD_mapping",
            ],
        },
    ),
    # ── T5.2 ADaM program bugs ────────────────────────────────────
    _task(
        task_id="T5.2.adam_adsl_debug.001",
        subcategory="T5.2",
        title="Debug ADSL derivation: population flag logic and treatment coding errors",
        complexity="complex",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md#ADSL",
            "fixtures/04_sdtm/SDTM_Specifications.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADSL",
        prompt=(
            "The following R program creates ADSL but has 4 bugs: "
            "(1) SAFFL (safety flag) is incorrectly derived by checking "
            "for any EX record (including dose=0) instead of EXDOSE > 0, "
            "(2) EFFFL (efficacy flag) checks VISITNUM >= 0 instead of "
            "VISITNUM > 0, incorrectly including baseline visit as "
            "post-baseline, (3) TRT01PN mapping uses 54 for Xan_Hi and 81 "
            "for Xan_Lo (values are swapped), (4) Screen failures "
            "(ACTARMCD='Scrnfail') are not filtered out, resulting in 306 "
            "records instead of the expected 254. Fix all bugs."
        ),
        gold_path="gold/T5.2.adam_adsl_debug.001/",
        oracle_params={
            "bug_count": 4,
            "fix_locations": [
                "SAFFL_dose_check",
                "EFFFL_visit_check",
                "TRT01PN_swap",
                "screen_failure_filter",
            ],
        },
    ),
    _task(
        task_id="T5.2.adam_adae_debug.001",
        subcategory="T5.2",
        title="Debug ADAE derivation: treatment-emergent flag and relative day errors",
        complexity="mixed",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md#ADAE",
            "fixtures/04_sdtm/SDTM_Specifications.md#AE",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADAE",
        prompt=(
            "The following R program creates ADAE but has 3 bugs: "
            "(1) TRTEMFL (treatment-emergent flag) uses ASTDT > TRTSDT "
            "(strictly greater than) instead of ASTDT >= TRTSDT, "
            "incorrectly excluding AEs that start on the same day as first "
            "dose, (2) ASTDY (relative start day) calculation uses "
            "ASTDT - TRTSDT without adding 1, resulting in day 0 instead "
            "of day 1 for events on the first dose date, (3) Treatment "
            "variables TRTPN and TRTAN are swapped: TRTPN (planned numeric) "
            "is assigned from TRT01AN (actual) and TRTAN (actual numeric) "
            "is assigned from TRT01PN (planned). Fix all bugs."
        ),
        gold_path="gold/T5.2.adam_adae_debug.001/",
        oracle_params={
            "bug_count": 3,
            "fix_locations": ["TRTEMFL_comparison", "ASTDY_offset", "TRTPN_TRTAN_swap"],
        },
    ),
    _task(
        task_id="T5.2.adam_adadas_debug.001",
        subcategory="T5.2",
        title="Debug ADADAS LOCF imputation and visit windowing errors",
        complexity="complex",
        fixtures=[
            "fixtures/05_adam/ADaM_Specifications.md#ADADAS",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        spec="fixtures/05_adam/ADaM_Specifications.md#ADADAS",
        prompt=(
            "The following R program creates ADADAS but has 4 bugs: "
            "(1) LOCF imputation carries forward the baseline value "
            "(VISITNUM==0) to post-baseline visits, but should only carry "
            "forward post-baseline observations, (2) Visit window for "
            "Week 24 has AWHI=252 instead of 336, cutting off late-visit "
            "records that should be windowed to Week 24, (3) ANL01FL "
            "(analysis flag) is set for all PARAMCD values but should only "
            "be set for PARAMCD='ACTOT' per the SAP, (4) CHG calculation "
            "is BASE - AVAL (inverted) instead of AVAL - BASE. Fix all "
            "bugs."
        ),
        gold_path="gold/T5.2.adam_adadas_debug.001/",
        oracle_params={
            "bug_count": 4,
            "fix_locations": [
                "LOCF_baseline_exclusion",
                "AWHI_Week24",
                "ANL01FL_PARAMCD",
                "CHG_direction",
            ],
        },
    ),
    # ── T5.3 TLF program bugs ─────────────────────────────────────
    _task(
        task_id="T5.3.tlf_demo_debug.001",
        subcategory="T5.3",
        title="Debug demographics table: wrong population filter and statistic errors",
        complexity="mixed",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-1-03_demographic.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADSL",
        ],
        spec="fixtures/06_tlfs/mock_templates/t_mock_14-1-03_demographic.md",
        prompt=(
            "The following R program generates Table 14-1.03 but has "
            "3 bugs: (1) Population filter uses SAFFL=='Y' (Safety) "
            "instead of ITTFL=='Y' (ITT) per mock shell, (2) The mean/SD "
            "format uses formatC with format='e' (scientific notation) "
            "instead of format='f' (fixed decimal), (3) The Total column "
            "is missing because add_overall_col was omitted from the table "
            "layout. Fix all bugs."
        ),
        gold_path="gold/T5.3.tlf_demo_debug.001/",
        oracle_params={
            "bug_count": 3,
            "fix_locations": ["population_filter", "format_string", "overall_column"],
        },
    ),
    _task(
        task_id="T5.3.tlf_ae_debug.001",
        subcategory="T5.3",
        title="Debug AE table: sorting and percentage denominator errors",
        complexity="complex",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-4-02_ae_by_soc_pt.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADAE",
        ],
        spec="fixtures/06_tlfs/mock_templates/t_mock_14-4-02_ae_by_soc_pt.md",
        prompt=(
            "The following R program generates Table 14-4.02 but has "
            "3 bugs: (1) Percentage denominator uses total Safety "
            "population N=254 for all treatment groups instead of the "
            "treatment-specific N, causing incorrect percentages, "
            "(2) The 5% incidence threshold filters based on SOC-level "
            "percentage instead of PT-level, removing entire SOCs "
            "incorrectly, (3) TRTEMFL filter is missing, so pre-treatment "
            "AEs are included in the counts. Fix all bugs."
        ),
        gold_path="gold/T5.3.tlf_ae_debug.001/",
        oracle_params={
            "bug_count": 3,
            "fix_locations": [
                "denominator_per_group",
                "threshold_level",
                "TRTEMFL_filter",
            ],
        },
    ),
    _task(
        task_id="T5.3.tlf_km_debug.001",
        subcategory="T5.3",
        title="Debug KM plot: censoring variable inversion and missing confidence bands",
        complexity="mixed",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/f_mock_14-5-01_km_plot.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADTTE",
        ],
        spec="fixtures/06_tlfs/mock_templates/f_mock_14-5-01_km_plot.md",
        prompt=(
            "The following R program generates the KM plot but has "
            "3 bugs: (1) The event indicator is derived as CNSR directly "
            "instead of 1-CNSR, inverting events and censored "
            "observations in the Surv() call, (2) conf.int=TRUE is set on "
            "ggsurvplot but the survfit call is missing conf.int parameter "
            "so no confidence bands are computed, (3) Risk table uses "
            "risk.table.col='grey' instead of 'strata', losing treatment "
            "group coloring. Fix all bugs."
        ),
        gold_path="gold/T5.3.tlf_km_debug.001/",
        oracle_params={
            "bug_count": 3,
            "fix_locations": ["event_indicator", "confint_survfit", "risk_table_color"],
        },
    ),
    _task(
        task_id="T5.3.tlf_primary_debug.001",
        subcategory="T5.3",
        title="Debug primary endpoint table: ANCOVA model specification and LOCF filter errors",
        complexity="complex",
        fixtures=[
            "fixtures/06_tlfs/mock_templates/t_mock_14-3-01_primary_endpoint.md",
            "fixtures/05_adam/ADaM_Specifications.md#ADADAS",
            "fixtures/01_study_design/sap/CDISCPilot01_SAP.md",
        ],
        spec="fixtures/06_tlfs/mock_templates/t_mock_14-3-01_primary_endpoint.md",
        prompt=(
            "The following R program generates Table 14-3.01 for the "
            "primary efficacy endpoint but has 4 bugs: (1) ANCOVA model "
            "uses lm(CHG ~ TRTPN + SITEGR1) missing the BASE covariate "
            "per SAP specification (should be CHG ~ TRTPN + SITEGR1 + "
            "BASE), (2) The analysis incorrectly filters to only DTYPE='LOCF' "
            "records instead of including all non-LOCF records plus LOCF "
            "where the original is missing, (3) TRTPN is used in the model "
            "as a numeric (continuous) variable instead of as a factor "
            "(categorical), resulting in a trend test instead of treatment "
            "group comparisons, (4) The population filter uses ITTFL=='Y' "
            "instead of EFFFL=='Y' per the SAP and mock shell. Fix all "
            "bugs."
        ),
        gold_path="gold/T5.3.tlf_primary_debug.001/",
        oracle_params={
            "bug_count": 4,
            "fix_locations": [
                "ancova_base_covariate",
                "locf_filter_logic",
                "TRTPN_factor",
                "population_filter",
            ],
        },
    ),
]

# ── Scale-task parameter lists ───────────────────────────────────────

_SDTM_P: list[tuple] = [
    (
        "cm",
        "CM",
        "Concomitant Medications",
        "complex",
        3,
        [
            "CMDECOD is populated from raw verbatim term (CMTRT) instead of standard medication dictionary",
            "CMROUTE uses non-standard route codes (e.g., 'oral') instead of CDISC controlled terminology ('ORAL')",
            "CMSTDTC date conversion uses datetime format (is8601dt.) instead of date-only format (is8601da.)",
        ],
        [
            "CMDECOD mapped from standard medication dictionary coding, not raw verbatim term",
            "CMROUTE uses CDISC controlled terminology with uppercase standard codes",
            "CMSTDTC uses date-only ISO 8601 format (is8601da.)",
        ],
        ["medication_coding", "route_terminology", "date_format"],
        "The following SAS program creates the SDTM CM domain but has 3 bugs: (1) CMDECOD is populated from the raw verbatim term (CMTRT) instead of standard medication dictionary coding, (2) CMROUTE uses non-standard lowercase route codes (e.g., 'oral') instead of CDISC controlled terminology ('ORAL'), (3) CMSTDTC date conversion uses is8601dt. (datetime) instead of is8601da. (date-only). Fix all bugs.",
    ),
    (
        "ds",
        "DS",
        "Disposition",
        "mixed",
        3,
        [
            "DSDECOD for completed subjects uses 'COMPLETED' but should use 'COMPLETED' per CDISC (already correct), but DISCONFL derivation checks DSDECOD != 'Completed' (case-sensitive) when DSDECOD is uppercase",
            "DSCAT is hardcoded as 'DISPOSITION' instead of 'DISPOSITION TRIAL' per SDTM specification",
            "DSSEQ is not retained and resets per observation instead of incrementing within USUBJID",
        ],
        [
            "DISCONFL comparison uses correct case matching for DSDECOD values",
            "DSCAT set to 'DISPOSITION TRIAL' per SDTM specification",
            "DSSEQ properly retained and incremented per USUBJID",
        ],
        ["disposition_case", "dscat_value", "dsseq_retain"],
        "The following SAS program creates the SDTM DS domain but has 3 bugs: (1) DISCONFL derivation uses case-sensitive comparison that doesn't match actual DSDECOD values, (2) DSCAT is hardcoded as 'DISPOSITION' instead of 'DISPOSITION TRIAL' per SDTM specification, (3) DSSEQ is not retained and resets per observation. Fix all bugs.",
    ),
    (
        "ex",
        "EX",
        "Exposure",
        "mixed",
        3,
        [
            "EXDOSE for Placebo subjects is set to 0 but EXDOSU is left blank instead of being set to 'mg' for consistency",
            "EXSTDTC derivation uses input(BRTHDTC, yymmdd10.) (birth date) instead of input(EXSTDT_RAW, yymmdd10.)",
            "EXSEQ numbering is global across all subjects instead of per USUBJID",
        ],
        [
            "EXDOSU populated with appropriate unit even for Placebo (0 mg)",
            "EXSTDTC derived from correct start date variable (EXSTDT_RAW, not BRTHDTC)",
            "EXSEQ numbering reset per USUBJID with proper retain",
        ],
        ["exdosu_placebo", "exstdtc_variable", "exseq_per_subject"],
        "The following SAS program creates the SDTM EX domain but has 3 bugs: (1) EXDOSU for Placebo subjects is left blank, (2) EXSTDTC uses birth date variable instead of exposure start date, (3) EXSEQ numbers globally instead of per subject. Fix all bugs.",
    ),
    (
        "mh",
        "MH",
        "Medical History",
        "complex",
        4,
        [
            "MHBODSYS is mapped from HLT instead of SOC level, causing incorrect body system classification",
            "MHSEQ not retained, resets per observation instead of incrementing within USUBJID",
            "MHSTDTC partial date handling truncates 2-digit year dates (e.g., '54' becomes '0054')",
            "MHCAT is hardcoded as 'MEDICAL HISTORY' but should use the QSCAT value from source data",
        ],
        [
            "MHBODSYS mapped from SOC (System Organ Class) not HLT",
            "MHSEQ properly retained and incremented per USUBJID",
            "MHSTDTC handles partial dates correctly preserving 4-digit years",
            "MHCAT derived from source category variable",
        ],
        ["mhbodsys_mapping", "mhseq_retain", "mhstdtc_partial", "mhcat_source"],
        "The following SAS program creates the SDTM MH domain but has 4 bugs: (1) MHBODSYS is mapped from HLT instead of SOC, (2) MHSEQ is not retained per subject, (3) MHSTDTC partial dates are truncated incorrectly, (4) MHCAT is hardcoded. Fix all bugs.",
    ),
    (
        "qs",
        "QS",
        "Questionnaires",
        "complex",
        4,
        [
            "QSSTRESC for numeric items is stored as character without standardizing to numeric format (QSSTRESN is missing)",
            "QSTESTCD for ADAS-Cog Word Recall is mapped as 'WR' instead of 'ACITM01' per CDISC convention",
            "QSSEQ uses _N_ for sequential numbering instead of retained counter per USUBJID",
            "QSORRES and QSSTRESC are swapped: QSORRES gets the standardized value and QSSTRESC gets the original",
        ],
        [
            "QSSTRESN populated with numeric conversion of QSSTRESC for numeric items",
            "QSTESTCD for ADAS-Cog items uses ACITM01-ACITM11 coding convention",
            "QSSEQ properly retained and incremented per USUBJID",
            "QSORRES gets original result, QSSTRESC gets standardized result",
        ],
        ["qsstresn_numeric", "qstestcd_mapping", "qsseq_retain", "qsorres_swap"],
        "The following SAS program creates the SDTM QS domain but has 4 bugs: (1) QSSTRESN is not populated for numeric items, (2) QSTESTCD for ADAS-Cog items uses non-standard codes, (3) QSSEQ uses _N_ instead of retained counter, (4) QSORRES and QSSTRESC are swapped. Fix all bugs.",
    ),
    (
        "sc",
        "SC",
        "Subject Characteristics",
        "simple",
        2,
        [
            "SCSTRESC for numeric characteristics is left blank (only SCORRES populated)",
            "SCSEQ starts at 0 instead of 1 for first record per USUBJID",
        ],
        [
            "SCSTRESC populated from standardized conversion of original result",
            "SCSEQ starts at 1 for first record per USUBJID",
        ],
        ["scstresc_missing", "scseq_offset"],
        "The following SAS program creates the SDTM SC domain but has 2 bugs: (1) SCSTRESC is left blank for numeric characteristics, (2) SCSEQ starts at 0 instead of 1. Fix all bugs.",
    ),
    (
        "sv",
        "SV",
        "Subject Visits",
        "mixed",
        3,
        [
            "SVDY calculation uses SVSTDTC minus RFSTDTC without converting to SAS dates first, producing incorrect day values",
            "VISITNUM is derived from VISIT name alphabetically instead of numeric visit ordering",
            "SVSEQ is not retained and resets per observation",
        ],
        [
            "SVDY computed as integer difference between SAS date values",
            "VISITNUM derived from numeric visit ordering, not alphabetical",
            "SVSEQ properly retained and incremented per USUBJID",
        ],
        ["svdy_date_conversion", "visitnum_ordering", "svseq_retain"],
        "The following SAS program creates the SDTM SV domain but has 3 bugs: (1) SVDY calculation doesn't convert to SAS dates, (2) VISITNUM is derived alphabetically, (3) SVSEQ is not retained. Fix all bugs.",
    ),
    (
        "dm_v2",
        "DM",
        "Demographics (race focus)",
        "mixed",
        3,
        [
            "RACE is mapped from raw using abbreviated codes ('W', 'B') instead of full CDISC terms ('WHITE', 'BLACK OR AFRICAN AMERICAN')",
            "ETHNIC derivation uses raw 'H'/'NH' codes instead of CDISC standard 'Hispanic or Latino'/'Not Hispanic or Latino'",
            "COUNTRY is hardcoded as 'USA' instead of being derived from SITEID lookup table",
        ],
        [
            "RACE mapped to full CDISC controlled terminology values",
            "ETHNIC mapped to CDISC standard values",
            "COUNTRY derived from SITEID via lookup table",
        ],
        ["race_mapping", "ethnic_mapping", "country_derivation"],
        "The following SAS program creates the SDTM DM domain but has 3 bugs: (1) RACE uses abbreviated codes, (2) ETHNIC uses abbreviated codes, (3) COUNTRY is hardcoded. Fix all bugs.",
    ),
    (
        "ae_v2",
        "AE",
        "Adverse Events (outcome focus)",
        "mixed",
        3,
        [
            "AEOUT mapping uses 'RECOVERED' for partial recovery instead of 'RECOVERING/RESOLVING' per CDISC",
            "AESEQ counter is reset for each BY group (by USUBJID AESTDTC) instead of just by USUBJID",
            "AEACN (action taken) for 'Dose Reduced' is mapped as 'DR' instead of 'DOSE REDUCED'",
        ],
        [
            "AEOUT mapped to correct CDISC terminology for partial outcomes",
            "AESEQ retained and incremented per USUBJID only",
            "AEACN mapped to full CDISC controlled terminology",
        ],
        ["aeout_mapping", "aeseq_by_group", "aeacn_terminology"],
        "The following SAS program creates the SDTM AE domain but has 3 bugs: (1) AEOUT uses incorrect CDISC terms, (2) AESEQ resets for each visit within subject, (3) AEACN uses abbreviated codes. Fix all bugs.",
    ),
    (
        "lb_v2",
        "LB",
        "Laboratory (unit focus)",
        "complex",
        4,
        [
            "LBSTRESU uses original units (LBORRESU) instead of standardized units for all tests",
            "LBSTRESN conversion for temperature uses (F-32)/1.8 instead of (F-32)*5/9",
            "LBSEQ numbering starts at 0 instead of 1 for first record per USUBJID",
            "LBORNRLO/LBORNRHI reference ranges are swapped (lower in upper field)",
        ],
        [
            "LBSTRESU uses standardized SI units for all tests",
            "LBSTRESN temperature conversion uses correct formula (F-32)*5/9",
            "LBSEQ starts at 1 for first record per USUBJID",
            "LBORNRLO/LBORNRHI correctly assigned (lower to lower, upper to upper)",
        ],
        [
            "lbstresu_standardization",
            "temp_conversion",
            "lbseq_offset",
            "ref_range_swap",
        ],
        "The following SAS program creates the SDTM LB domain but has 4 bugs: (1) LBSTRESU uses original units, (2) temperature conversion uses wrong formula, (3) LBSEQ starts at 0, (4) reference range limits are swapped. Fix all bugs.",
    ),
    (
        "vs_v2",
        "VS",
        "Vital Signs (computation focus)",
        "mixed",
        3,
        [
            "BMI computation uses WEIGHTBL/(HEIGHTBL/100) instead of WEIGHTBL/(HEIGHTBL/100)**2",
            "VSBLFL baseline flag logic uses VISITNUM < 0 instead of VISITNUM <= 0, excluding the screening visit",
            "VSTESTCD for Pulse is mapped as 'HR' instead of 'PULSE' per CDISC controlled terminology",
        ],
        [
            "BMI computed as WEIGHTBL/(HEIGHTBL/100)**2",
            "VSBLFL set for VISITNUM <= 0 (includes screening visit)",
            "Pulse test code uses CDISC standard 'PULSE'",
        ],
        ["bmi_formula", "vsblfl_condition", "pulse_testcd"],
        "The following SAS program creates the SDTM VS domain but has 3 bugs: (1) BMI formula is incorrect, (2) VSBLFL excludes screening visit, (3) Pulse VSTESTCD is non-standard. Fix all bugs.",
    ),
    (
        "suppdm",
        "SUPPDM",
        "Supplemental DM",
        "mixed",
        3,
        [
            "IDVAR is set to 'USUBJID' but should be 'DMSEQ' per SDTM supplemental qualifier standard",
            "QNAM values use lowercase ('ethnic_grp') instead of uppercase ('ETHNIC_GRP')",
            "QVAL for binary qualifiers uses 'Yes'/'No' instead of 'Y'/'N'",
        ],
        [
            "IDVAR set to 'DMSEQ' per SDTM supplemental qualifier standard",
            "QNAM values use uppercase naming convention",
            "QVAL for binary qualifiers uses 'Y'/'N'",
        ],
        ["idvar_value", "qnam_case", "qval_format"],
        "The following SAS program creates the SUPPDM domain but has 3 bugs: (1) IDVAR references wrong variable, (2) QNAM uses lowercase, (3) QVAL binary values use wrong format. Fix all bugs.",
    ),
    (
        "suppae",
        "SUPPAE",
        "Supplemental AE",
        "mixed",
        3,
        [
            "RDOMAIN is set to 'DM' instead of 'AE' for supplemental AE qualifiers",
            "IDVARVAL references SUBJID instead of AESEQ for linking to parent AE records",
            "QLABEL is not populated, leaving qualifier labels missing",
        ],
        [
            "RDOMAIN set to 'AE' for supplemental AE qualifiers",
            "IDVARVAL references AESEQ for parent record linkage",
            "QLABEL populated with descriptive label per Define-XML",
        ],
        ["rdomain_value", "idvarval_reference", "qlabel_missing"],
        "The following SAS program creates the SUPPAE domain but has 3 bugs: (1) RDOMAIN is incorrect, (2) IDVARVAL references wrong variable, (3) QLABEL is not populated. Fix all bugs.",
    ),
    (
        "supplb",
        "SUPPLB",
        "Supplemental LB",
        "mixed",
        3,
        [
            "SUPPLB RELID is not unique across domains, causing potential merge conflicts with SUPPDM/SUPPAE",
            "QNAM for fasted status uses 'FAST' instead of 'LBFAST' per Define-XML specification",
            "RDOMAIN is hardcoded as 'LB' in data step but QNAM prefix check uses 'DM'",
        ],
        [
            "RELID uniquely assigned across all supplemental qualifier domains",
            "QNAM for fasted status uses 'LBFAST' per Define-XML specification",
            "RDOMAIN and QNAM prefix check both use 'LB' consistently",
        ],
        ["relid_uniqueness", "qnam_fasted", "rdomain_prefix"],
        "The following SAS program creates the SUPPLB domain but has 3 bugs: (1) RELID is not unique across domains, (2) QNAM uses wrong name for fasted status, (3) RDOMAIN prefix check is inconsistent. Fix all bugs.",
    ),
]

_ADAM_P: list[tuple] = [
    (
        "adlbc",
        "ADLBC",
        "Laboratory Analysis",
        "complex",
        4,
        [
            "ANRIND derivation uses AVAL < LBNRNRHI (strict less than) instead of AVAL <= LBNRNRHI for 'LOW' classification",
            "BASE is taken from first visit (VISITNUM==1) instead of baseline visit (VISITNUM==0)",
            "SHIFT variable is derived as ANRIND concatenated with BNRIND instead of as a structured transition pair",
            "PARAMCD for Sodium is mapped as 'NA' instead of 'SODIUM' per CDISC controlled terminology",
        ],
        [
            "ANRIND uses <= for lower bound comparison",
            "BASE taken from baseline visit (VISITNUM==0)",
            "SHIFT derived as structured baseline-to-post-baseline category transition",
            "Sodium PARAMCD mapped as 'SODIUM'",
        ],
        ["anrind_comparison", "base_visit", "shift_structure", "sodium_paramcd"],
        "The following R program creates ADLBC but has 4 bugs: (1) ANRIND uses wrong comparison operator, (2) BASE is from wrong visit, (3) SHIFT is incorrectly structured, (4) Sodium PARAMCD is wrong. Fix all bugs.",
    ),
    (
        "adtte",
        "ADTTE",
        "Time-to-Event Analysis",
        "mixed",
        3,
        [
            "CNSR is used directly in Surv() call instead of 1-CNSR, inverting events and censored observations",
            "ADT (analysis date) is derived from AE start date instead of event-specific date per PARAMCD",
            "PARAMCD is hardcoded as 'TTDE' for all records instead of being derived from source data",
        ],
        [
            "Surv() uses 1-CNSR for event indicator",
            "ADT derived from correct event-specific date per PARAMCD",
            "PARAMCD derived from source data mapping",
        ],
        ["cnsr_inversion", "adt_source", "paramcd_derivation"],
        "The following R program creates ADTTE but has 3 bugs: (1) CNSR is used directly instead of 1-CNSR, (2) ADT uses wrong date source, (3) PARAMCD is hardcoded. Fix all bugs.",
    ),
    (
        "adsl_v2",
        "ADSL",
        "Subject-Level (SAFFL focus)",
        "mixed",
        3,
        [
            "SAFFL derivation checks for any EX record (including EXDOSE=0) instead of EXDOSE > 0",
            "TRT01PN for Xan_Lo is set to 81 and Xan_Hi to 54 (values are swapped)",
            "COMP24FL is derived from DSDECOD=='COMPLETED' without also checking VISIT=='WEEK 24'",
        ],
        [
            "SAFFL requires EXDOSE > 0",
            "TRT01PN corrected: Xan_Lo=54, Xan_Hi=81",
            "COMP24FL checks both DSDECOD and VISIT for Week 24 completion",
        ],
        ["saffl_dose_check", "trt01pn_swap", "comp24fl_visit"],
        "The following R program creates ADSL but has 3 bugs: (1) SAFFL includes zero-dose records, (2) TRT01PN values are swapped, (3) COMP24FL doesn't check visit. Fix all bugs.",
    ),
    (
        "adae_v2",
        "ADAE",
        "Adverse Events (ASTDY focus)",
        "mixed",
        3,
        [
            "ASTDY calculation is ASTDT - TRTSDT without the +1 offset, giving day 0 instead of day 1 for first dose day events",
            "TRTEMFL uses ASTDT > TRTSDT (strictly greater) instead of >=, excluding same-day events",
            "TRTPN is assigned from TRT01AN (actual) instead of TRT01PN (planned)",
        ],
        [
            "ASTDY adds +1 offset",
            "TRTEMFL uses >= for inclusive comparison",
            "TRTPN from TRT01PN (planned numeric treatment)",
        ],
        ["astdy_offset", "trtemfl_comparison", "trtpn_source"],
        "The following R program creates ADAE but has 3 bugs: (1) ASTDY missing +1 offset, (2) TRTEMFL excludes same-day events, (3) TRTPN from wrong source. Fix all bugs.",
    ),
    (
        "adadas_v2",
        "ADADAS",
        "ADAS-Cog (CHG focus)",
        "mixed",
        3,
        [
            "CHG is computed as BASE - AVAL (inverted) instead of AVAL - BASE",
            "ANL01FL is set for all PARAMCD values instead of only PARAMCD=='ACTOT' per SAP",
            "PCHG computation divides by AVAL instead of BASE for percent change",
        ],
        [
            "CHG = AVAL - BASE (correct direction)",
            "ANL01FL only set for PARAMCD=='ACTOT'",
            "PCHG = (CHG/BASE) * 100",
        ],
        ["chg_direction", "anl01fl_paramcd", "pchg_denominator"],
        "The following R program creates ADADAS but has 3 bugs: (1) CHG is inverted, (2) ANL01FL is set for all parameters, (3) PCHG divides by wrong variable. Fix all bugs.",
    ),
    (
        "adlbc_v2",
        "ADLBC",
        "Lab (BASE focus)",
        "mixed",
        3,
        [
            "BASE is populated from the first non-missing post-baseline visit instead of the baseline visit (AVISITN==0)",
            "CHG for post-baseline visits uses AVAL minus last observation instead of AVAL minus BASE",
            "ATOXGR toxicity grading uses absolute value thresholds instead of CTCAE grade definitions",
        ],
        [
            "BASE from baseline visit (AVISITN==0)",
            "CHG = AVAL - BASE consistently",
            "ATOXGR derived per CTCAE grade definitions",
        ],
        ["base_visit_source", "chg_baseline", "atoxgr_grading"],
        "The following R program creates ADLBC but has 3 bugs: (1) BASE from wrong visit, (2) CHG uses last observation, (3) ATOXGR uses wrong grading. Fix all bugs.",
    ),
    (
        "adtte_v2",
        "ADTTE",
        "Time-to-Event (AVAL focus)",
        "mixed",
        3,
        [
            "AVAL is derived as TRTEDT - TRTSDT (treatment duration) instead of event date - treatment start date",
            "CNSR=1 is assigned for events (should be 0) and CNSR=0 for censored (should be 1)",
            "TRTP is taken from ADSL TRT01A (actual) instead of TRT01P (planned)",
        ],
        [
            "AVAL = event_date - treatment_start_date",
            "CNSR: 0=event, 1=censored (correct assignment)",
            "TRTP from TRT01P (planned treatment)",
        ],
        ["aval_derivation", "cnsr_assignment", "trtp_source"],
        "The following R program creates ADTTE but has 3 bugs: (1) AVAL uses wrong dates, (2) CNSR values are inverted, (3) TRTP from wrong source. Fix all bugs.",
    ),
    (
        "adsl_v3",
        "ADSL",
        "Subject-Level (EOSSTT focus)",
        "simple",
        2,
        [
            "EOSSTT is set to 'Completed' for all subjects regardless of actual disposition status",
            "TRTDURD calculation is TRTEDT - TRTSDT without the +1, giving one day short of actual duration",
        ],
        [
            "EOSSTT derived from DSDECOD: 'Completed' or 'Discontinued'",
            "TRTDURD = as.integer(TRTEDT - TRTSDT) + 1L",
        ],
        ["eosstt_derivation", "trtdurd_offset"],
        "The following R program creates ADSL but has 2 bugs: (1) EOSSTT is set to 'Completed' for all subjects, (2) TRTDURD is missing +1 offset. Fix all bugs.",
    ),
    (
        "adae_v3",
        "ADAE",
        "Adverse Events (ASEV focus)",
        "mixed",
        3,
        [
            "ASEV (analysis severity) takes the first severity value instead of maximum severity across records for the same AE",
            "AENDY calculation is AENDT - TRTSDT without +1, giving day 0 for events ending on first dose day",
            "TRTEMFL filter for TEAE analysis uses TRTEMFL=='N' instead of TRTEMFL=='Y'",
        ],
        [
            "ASEV derived as maximum severity per AE",
            "AENDY = as.integer(AENDT - TRTSDT) + 1L",
            "TRTEMFL filter uses 'Y' for treatment-emergent",
        ],
        ["asev_max_severity", "aendy_offset", "trtemfl_filter"],
        "The following R program creates ADAE but has 3 bugs: (1) ASEV takes first instead of max severity, (2) AENDY missing +1 offset, (3) TRTEMFL filter is inverted. Fix all bugs.",
    ),
    (
        "adadas_v3",
        "ADADAS",
        "ADAS-Cog (LOCF focus)",
        "complex",
        4,
        [
            "LOCF carries forward baseline value (VISITNUM==0) to post-baseline visits instead of only post-baseline observations",
            "AWHI for Week 24 is set to 252 instead of 336, cutting off late-visit records",
            "AWLO for Week 8 is set to 30 instead of 29, excluding day-29 observations",
            "Visit windowing assigns AVISIT based on AWTARGET == VISTPT instead of AWLO <= ADY <= AWHI range",
        ],
        [
            "LOCF excludes baseline from carry-forward pool",
            "AWHI for Week 24 = 336",
            "AWLO for Week 8 = 29",
            "Visit windowing uses AWLO/AWHI range check",
        ],
        ["locf_baseline", "awhi_week24", "awlo_week8", "visit_window_range"],
        "The following R program creates ADADAS but has 4 bugs: (1) LOCF includes baseline, (2) Week 24 AWHI is wrong, (3) Week 8 AWLO is wrong, (4) Visit windowing uses wrong logic. Fix all bugs.",
    ),
    (
        "adlbc_v3",
        "ADLBC",
        "Lab (ANRIND focus)",
        "mixed",
        3,
        [
            "ANRIND 'NORMAL' threshold uses AVAL > LBNRNRLO & AVAL < LBNRNRHI (exclusive) instead of >= and <= (inclusive)",
            "BNRIND (baseline reference range indicator) is not derived, leaving the shift variable without a baseline reference",
            "SHIFT variable concatenates 'L2N' style strings but should use structured 'LOW_TO_NORMAL' format",
        ],
        [
            "ANRIND uses inclusive comparisons (>= and <=) for NORMAL range",
            "BNRIND derived from baseline visit ANRIND logic",
            "SHIFT uses structured transition format",
        ],
        ["anrind_comparison", "bnrind_missing", "shift_format"],
        "The following R program creates ADLBC but has 3 bugs: (1) ANRIND uses exclusive comparison, (2) BNRIND is not derived, (3) SHIFT uses wrong format. Fix all bugs.",
    ),
    (
        "adtte_v3",
        "ADTTE",
        "Time-to-Event (subgroup focus)",
        "complex",
        4,
        [
            "Subgroup variable SUBGP is derived from SITEID using first 2 characters instead of SITEGR1 (pooled site group)",
            "Stratified log-rank test uses unstratified survdiff() without strata() argument",
            "Median time-to-event calculation uses mean() instead of quantile(survfit, probs=0.5)",
            "Treatment variable in survfit() uses numeric TRT01PN instead of factor, treating treatment as continuous",
        ],
        [
            "SUBGP derived from SITEGR1 (pooled site group)",
            "Log-rank uses strata() for stratified comparison",
            "Median uses quantile(survfit, probs=0.5)",
            "Treatment variable converted to factor for categorical comparison",
        ],
        ["subgp_source", "logrank_strata", "median_calculation", "trt_factor"],
        "The following R program creates ADTTE with subgroup analysis but has 4 bugs: (1) SUBGP from wrong variable, (2) log-rank not stratified, (3) median uses mean(), (4) treatment not factor. Fix all bugs.",
    ),
    (
        "adadas_v4",
        "ADADAS",
        "ADAS-Cog (visit focus)",
        "mixed",
        3,
        [
            "AVISIT is derived from VISIT name directly without mapping to standardized analysis visit names",
            "AWTARGET for Week 16 is set to 112 but AWLO is 84 (should be 85), overlapping with Week 8 window",
            "DTYPE flag for LOCF records is set to 'LOCF' for all records including non-imputed ones",
        ],
        [
            "AVISIT mapped to standardized analysis visit names per specification",
            "AWLO for Week 16 = 85 (no overlap with Week 8)",
            "DTYPE='LOCF' only for imputed records",
        ],
        ["avisit_mapping", "awlo_week16", "dtype_flag"],
        "The following R program creates ADADAS but has 3 bugs: (1) AVISIT not standardized, (2) Week 16 AWLO overlaps Week 8, (3) DTYPE set for all records. Fix all bugs.",
    ),
    (
        "adsl_v4",
        "ADSL",
        "Subject-Level (age grouping)",
        "simple",
        2,
        [
            "AGEGR1 is derived as cut(AGE, c(0,40,65,100)) but should use c(0,40,65,Inf) to include ages above 100",
            "SEX variable is used as numeric 1/2 instead of character 'M'/'F' for label derivation",
        ],
        [
            "AGEGR1 uses c(0,40,65,Inf) to cover all ages",
            "SEX kept as character 'M'/'F' for label mapping",
        ],
        ["agegr1_bounds", "sex_type"],
        "The following R program creates ADSL but has 2 bugs: (1) AGEGR1 upper bound excludes ages above 100, (2) SEX is numeric instead of character. Fix all bugs.",
    ),
]

_TLF_P: list[tuple] = [
    (
        "ae_overview",
        "14-4.01",
        "AE Overview Table",
        "mixed",
        3,
        [
            "Population filter uses ITTFL=='Y' (ITT) instead of SAFFL=='Y' (Safety) per mock shell",
            "TEAE count uses all AE records instead of filtering by TRTEMFL=='Y'",
            "Event count column sums all AE records per group instead of counting unique subjects with events",
        ],
        [
            "Population filter changed to SAFFL=='Y' (Safety)",
            "TEAE count filters by TRTEMFL=='Y'",
            "Event count uses distinct USUBJID count per group",
        ],
        ["population_filter", "teae_filter", "event_count_method"],
        "The following R program generates Table 14-4.01 AE Overview but has 3 bugs: (1) Wrong population filter, (2) TEAE count missing TRTEMFL filter, (3) Event count not distinct. Fix all bugs.",
    ),
    (
        "disposition",
        "14-2.01",
        "Disposition Table",
        "mixed",
        3,
        [
            "Disposition table uses SAFFL=='Y' (Safety) instead of ITTFL=='Y' (ITT) population filter",
            "Completion percentage denominator uses total N=254 instead of treatment-group-specific N",
            "Discontinuation reason ordering is alphabetical instead of by frequency (descending) per mock shell",
        ],
        [
            "Population filter changed to ITTFL=='Y' (ITT)",
            "Percentage denominator uses treatment-group-specific N",
            "Reason ordering by frequency descending",
        ],
        ["population_filter", "denominator", "sort_order"],
        "The following R program generates Table 14-2.01 Disposition but has 3 bugs: (1) Wrong population, (2) Wrong denominator, (3) Wrong sort order. Fix all bugs.",
    ),
    (
        "cfb",
        "14-3.02",
        "Change from Baseline Over Time",
        "mixed",
        3,
        [
            "Standard error uses sd(x)/sqrt(length(x)) without na.rm=TRUE, producing NA for visits with missing data",
            "Visit filtering uses AVISITN %in% c(0,8,16,24) but includes baseline (AVISITN==0) in change values",
            "Confidence interval uses z*SE instead of t*SE (qt(0.975, df=n-1)*SE)",
        ],
        [
            "Standard error includes na.rm=TRUE",
            "Baseline visit excluded from change-from-baseline display rows",
            "CI uses t-distribution critical value",
        ],
        ["se_na_rm", "visit_filter", "ci_distribution"],
        "The following R program generates Table 14-3.02 CFB Over Time but has 3 bugs: (1) SE fails with missing data, (2) Baseline included in CFB rows, (3) CI uses wrong distribution. Fix all bugs.",
    ),
    (
        "lab_summary",
        "14-6.01",
        "Laboratory Summary Table",
        "complex",
        4,
        [
            "Lab parameters are not grouped by test category (Chemistry, Hematology, Urinalysis) per mock shell",
            "Mean values use median() instead of mean() for central tendency",
            "Reference range flag counts use total lab records instead of unique subjects",
            "Shift from baseline display uses CHG values instead of ANRIND/BNRIND category transitions",
        ],
        [
            "Lab parameters grouped by test category",
            "Central tendency uses mean()",
            "Reference range counts use distinct subjects",
            "Shift display uses ANRIND/BNRIND categories",
        ],
        ["parameter_grouping", "stat_function", "count_method", "shift_variable"],
        "The following R program generates Table 14-6.01 Lab Summary but has 4 bugs: (1) No category grouping, (2) Wrong stat function, (3) Wrong count method, (4) Wrong shift variable. Fix all bugs.",
    ),
    (
        "responder",
        "14-3.03",
        "Responder Analysis Table",
        "complex",
        4,
        [
            "Responder definition uses AVAL > BASE (improvement in any direction) instead of specified threshold (e.g., >=4 point improvement)",
            "CMH test uses chisq.test() instead of mantelhaen.test() for stratified analysis",
            "Response rates are calculated as n/total_N (overall) instead of n/group_N (treatment-specific)",
            "Missing values in response variable are counted as non-responders instead of being excluded",
        ],
        [
            "Responder uses specified improvement threshold",
            "CMH test uses mantelhaen.test() for stratified analysis",
            "Response rates use group-specific denominators",
            "Missing values excluded from responder analysis",
        ],
        ["responder_definition", "cmh_test", "rate_denominator", "missing_handling"],
        "The following R program generates Table 14-3.03 Responder Analysis but has 4 bugs: (1) Wrong responder definition, (2) Wrong statistical test, (3) Wrong denominator, (4) Missing not excluded. Fix all bugs.",
    ),
    (
        "shift_table",
        "14-6.02",
        "Lab Shift Table",
        "complex",
        3,
        [
            "Shift table uses CHG categories (positive/negative/zero) instead of ANRIND/BNRIND reference range transitions (LOW/NORMAL/HIGH)",
            "Post-baseline visit selection uses first post-baseline visit instead of worst-case (maximum severity) visit",
            "Percentage calculation for shift cells uses column total instead of row total as denominator",
        ],
        [
            "Shift uses ANRIND/BNRIND reference range categories",
            "Post-baseline selection uses worst-case visit",
            "Percentages use row total as denominator",
        ],
        ["shift_categories", "visit_selection", "percentage_denominator"],
        "The following R program generates Table 14-6.02 Lab Shift but has 3 bugs: (1) Wrong shift categories, (2) Wrong visit selection, (3) Wrong percentage denominator. Fix all bugs.",
    ),
    (
        "conmed",
        "14-2.02",
        "Concomitant Medications Table",
        "complex",
        4,
        [
            "Medications are sorted alphabetically instead of by ATC class and frequency",
            "Percentage denominator uses total Safety N instead of treatment-group-specific N",
            "Route of administration filter is missing, including topical medications in oral medication counts",
            "ATC class names use abbreviated codes ('J01') instead of full names ('ANTIINFECTIVES FOR SYSTEMIC USE')",
        ],
        [
            "Medications sorted by ATC class then frequency",
            "Percentage denominator uses treatment-group-specific N",
            "Route filter applied to select relevant administration routes",
            "ATC class names use full descriptive names",
        ],
        ["sort_logic", "denominator", "route_filter", "atc_display"],
        "The following R program generates Table 14-2.02 Concomitant Medications but has 4 bugs: (1) Wrong sort, (2) Wrong denominator, (3) Missing route filter, (4) Abbreviated ATC codes. Fix all bugs.",
    ),
    (
        "exposure",
        "14-2.03",
        "Exposure Compliance Table",
        "mixed",
        3,
        [
            "Treatment duration uses max(EXENDTC) - min(EXSTDTC) without +1 offset, giving one day short",
            "Compliance percentage uses planned doses instead of actual doses for the ratio",
            "Dose intensity calculation divides by treatment period in weeks instead of days",
        ],
        [
            "Treatment duration includes +1 offset",
            "Compliance uses actual vs planned doses",
            "Dose intensity uses consistent time unit (days)",
        ],
        ["duration_offset", "compliance_doses", "intensity_units"],
        "The following R program generates Table 14-2.03 Exposure but has 3 bugs: (1) Duration missing +1, (2) Compliance uses wrong doses, (3) Intensity uses wrong time unit. Fix all bugs.",
    ),
    (
        "medhist",
        "14-1.04",
        "Medical History Table",
        "mixed",
        3,
        [
            "Medical history table uses Safety population instead of ITT population",
            "SOC/PT sorting is alphabetical instead of by SOC frequency (descending) per mock shell",
            "Pre-existing condition flag filter is missing, including post-baseline conditions",
        ],
        [
            "Population filter uses ITT (ITTFL=='Y')",
            "SOC/PT sorted by frequency descending",
            "Pre-existing condition filter applied",
        ],
        ["population_filter", "sort_order", "condition_filter"],
        "The following R program generates Table 14-1.04 Medical History but has 3 bugs: (1) Wrong population, (2) Wrong sort, (3) Missing condition filter. Fix all bugs.",
    ),
    (
        "primary_v2",
        "14-3.01",
        "Primary Endpoint (dose response)",
        "complex",
        4,
        [
            "Dose-response trend test uses linear regression on TRT01PN as numeric instead of contrast-based Cochran-Armitage test",
            "LS means are computed from raw group means instead of from the ANCOVA model fitted values",
            "Pairwise p-values are not adjusted for multiplicity (should use Dunnett's method for 2 comparisons)",
            "TRTPN is used as numeric in the model instead of as a factor (categorical)",
        ],
        [
            "Dose-response uses contrast-based trend test",
            "LS means from ANCOVA model",
            "Pairwise p-values adjusted using Dunnett's method",
            "TRTPN as factor in model",
        ],
        ["trend_test", "ls_means", "multiplicity", "trtpn_factor"],
        "The following R program generates Table 14-3.01 Primary Endpoint but has 4 bugs: (1) Wrong trend test, (2) Wrong LS means, (3) No multiplicity adjustment, (4) TRTPN as numeric. Fix all bugs.",
    ),
    (
        "ae_severity_v2",
        "14-4.04",
        "AE by Severity Table",
        "mixed",
        3,
        [
            "Severity levels are ordered alphabetically ('MILD', 'MODERATE', 'SEVERE') instead of by clinical severity",
            "Subject counts for each severity level count multiple events per subject instead of unique subjects",
            "Total row sums severity-level counts instead of counting distinct subjects with any AE",
        ],
        [
            "Severity ordered by clinical severity level",
            "Counts use distinct subjects per severity",
            "Total uses distinct subjects with any AE",
        ],
        ["severity_order", "count_method", "total_method"],
        "The following R program generates Table 14-4.04 AE by Severity but has 3 bugs: (1) Wrong severity order, (2) Duplicate subject counting, (3) Total sums instead of distinct. Fix all bugs.",
    ),
    (
        "forest",
        "14-5.02",
        "Forest Plot (Subgroup)",
        "complex",
        4,
        [
            "Subgroup labels use variable names ('SEX', 'AGEGR1') instead of descriptive labels ('Sex', 'Age Group')",
            "Forest plot x-axis uses linear scale instead of log scale for odds ratios",
            "Confidence intervals are computed using normal approximation instead of exact (Clopper-Pearson) method",
            "Interaction p-value uses anova() on lm models instead of coxph or logistic regression interaction test",
        ],
        [
            "Subgroup labels use descriptive text",
            "Forest plot x-axis uses log scale",
            "CI uses exact method (Clopper-Pearson)",
            "Interaction p-value from appropriate model",
        ],
        ["subgroup_labels", "x_scale", "ci_method", "interaction_test"],
        "The following R program generates Figure 14-5.02 Forest Plot but has 4 bugs: (1) Raw variable names as labels, (2) Linear scale for OR, (3) Wrong CI method, (4) Wrong interaction test. Fix all bugs.",
    ),
]


# ── Scale-task builder ────────────────────────────────────────────────


def _build_scale() -> tuple[list[dict], dict[str, str]]:
    """Build 40 scale tasks and their gold outputs from parameter lists."""
    tasks: list[dict] = []
    gold: dict[str, str] = {}

    # T5.1 SDTM scale tasks
    sdtm_idx = 2
    for (
        domain,
        domain_upper,
        label,
        complexity,
        bug_count,
        bug_descs,
        fix_descs,
        fix_locs,
        prompt_detail,
    ) in _SDTM_P:
        tid = f"T5.1.sdtm_{domain}_debug.{sdtm_idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T5.1",
                title=f"Debug SDTM {domain_upper} domain program: {label} errors",
                complexity=complexity,
                fixtures=[
                    f"fixtures/04_sdtm/programs/create_{domain}.R",
                    f"fixtures/04_sdtm/SDTM_Specifications.md#{domain_upper}",
                ],
                spec=f"fixtures/04_sdtm/SDTM_Specifications.md#{domain_upper}",
                prompt=prompt_detail,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "bug_count": bug_count,
                    "fix_locations": fix_locs,
                },
            )
        )
        gold[tid] = _patch_gold_t(
            domain_upper, bug_descs, fix_descs, fix_locs, ext=".sas"
        )
        sdtm_idx += 1

    # T5.2 ADaM scale tasks
    adam_idx = 2
    for (
        name,
        name_upper,
        label,
        complexity,
        bug_count,
        bug_descs,
        fix_descs,
        fix_locs,
        prompt_detail,
    ) in _ADAM_P:
        tid = f"T5.2.adam_{name}_debug.{adam_idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T5.2",
                title=f"Debug {name_upper} derivation: {label} errors",
                complexity=complexity,
                fixtures=[
                    f"fixtures/05_adam/ADaM_Specifications.md#{name_upper}",
                    "fixtures/04_sdtm/SDTM_Specifications.md",
                ],
                spec=f"fixtures/05_adam/ADaM_Specifications.md#{name_upper}",
                prompt=prompt_detail,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "bug_count": bug_count,
                    "fix_locations": fix_locs,
                },
            )
        )
        gold[tid] = _patch_gold_t(name_upper, bug_descs, fix_descs, fix_locs, ext=".R")
        adam_idx += 1

    # T5.3 TLF scale tasks
    tlf_idx = 2
    for (
        name,
        table_num,
        label,
        complexity,
        bug_count,
        bug_descs,
        fix_descs,
        fix_locs,
        prompt_detail,
    ) in _TLF_P:
        tid = f"T5.3.tlf_{name}_debug.{tlf_idx:03d}"
        tasks.append(
            _task(
                task_id=tid,
                subcategory="T5.3",
                title=f"Debug {label}: Table/Figure {table_num} errors",
                complexity=complexity,
                fixtures=[
                    f"fixtures/06_tlfs/mock_templates/t_mock_{table_num.replace('-', '_').replace('.', '_')}.md",
                    "fixtures/05_adam/ADaM_Specifications.md",
                ],
                spec=f"fixtures/06_tlfs/mock_templates/t_mock_{table_num.replace('-', '_').replace('.', '_')}.md",
                prompt=prompt_detail,
                gold_path=f"gold/{tid}/",
                oracle_params={
                    "bug_count": bug_count,
                    "fix_locations": fix_locs,
                },
            )
        )
        gold[tid] = _patch_gold_t(name, bug_descs, fix_descs, fix_locs, ext=".R")
        tlf_idx += 1

    return tasks, gold


SCALE_TASKS, SCALE_GOLD = _build_scale()

# ── Gold outputs (unified diff patches) ──────────────────────────────

GOLD_OUTPUTS: dict[str, str] = {
    "T5.1.sdtm_dm_debug.001": """--- a/sdtm_dm.sas
+++ b/sdtm_dm.sas
@@ -1,5 +1,5 @@
-Bug 1: USUBJID = cats(SUBJID, "-", SITEID, "-", STUDYID);
+Fix 1: USUBJID = cats(STUDYID, "-", SITEID, "-", SUBJID);

-Bug 2: when ("Xan_lo") do; ARMCD = "Xan_lo";
+Fix 2: when ("Xan_Lo") do; ARMCD = "Xan_Lo";

-Bug 3: AGE = yrdif(BRTHDTC, RFICDTC, 'ACTUAL');
+Fix 3: AGE = int(yrdif(input(BRTHDTC, yymmdd10.), input(RFICDTC, yymmdd10.), 'ACTUAL'));

Summary of fixes:
1. USUBJID concatenation order corrected to STUDYID-SITEID-SUBJID
2. ARMCD for Xanomeline Low Dose uses 'Xan_Lo' (capital L)
3. AGE calculation converts BRTHDTC string to SAS date before yrdif
""",
    "T5.1.sdtm_ae_debug.001": """--- a/sdtm_ae.sas
+++ b/sdtm_ae.sas
@@ -1,5 +1,5 @@
-Bug 1: if AESHOSP_RAW = "Y" or AESDEATH_RAW = "Y" then AESER = "Y";
+Fix 1: if AESCAN_RAW = "Y" or AESCONG_RAW = "Y" or AESDEATH_RAW = "Y" or AESHOSP_RAW = "Y" or AESLIFE_RAW = "Y" or AESOD_RAW = "Y" then AESER = "Y";

-Bug 2: AESEQ = _N_;
+Fix 2: retain AESEQ; if first.USUBJID then AESEQ = 0; AESEQ = AESEQ + 1;

-Bug 3: AEBODSYS = strip(HLT_RAW);
+Fix 3: AEBODSYS = strip(SOC_RAW);

-Bug 4: AESTDTC = strip(put(AESTDT, is8601dt.));
+Fix 4: AESTDTC = strip(put(AESTDT, is8601da.));

Summary of fixes:
1. AESER seriousness flag now checks all 6 seriousness criteria
2. AESEQ properly retained and incremented per USUBJID
3. AEBODSYS mapped from SOC (System Organ Class) not HLT
4. AESTDTC uses date format (is8601da.) instead of datetime (is8601dt.)
""",
    "T5.1.sdtm_vs_debug.001": """--- a/sdtm_vs.sas
+++ b/sdtm_vs.sas
@@ -1,5 +1,5 @@
-Bug 1: if VISITDY > 0 then VSBLFL = "Y";
+Fix 1: if VISITDY <= 0 then VSBLFL = "Y";

-Bug 2: TEMP_C = (TEMP_F - 32) / 1.2;
+Fix 2: TEMP_C = (TEMP_F - 32) * 5 / 9;

-Bug 3: when ("Diastolic Blood Pressure") VSTESTCD = "DBP";
+Fix 3: when ("Diastolic Blood Pressure") VSTESTCD = "DIABP";

Summary of fixes:
1. VSBLFL baseline flag set for pre-baseline visits (VISITDY <= 0)
2. Temperature conversion uses correct formula (F-32)*5/9
3. Diastolic BP test code uses CDISC standard 'DIABP'
""",
    "T5.2.adam_adsl_debug.001": """--- a/adam_adsl.R
+++ b/adam_adsl.R
@@ -1,5 +1,5 @@
-Bug 1: ex_dosed <- ex %>% filter(!is.na(EXDOSE)) %>% distinct(USUBJID)
+Fix 1: ex_dosed <- ex %>% filter(!is.na(EXDOSE) & EXDOSE > 0) %>% distinct(USUBJID)

-Bug 2: qs_postbl <- qs %>% filter(QSCAT == "ADAS-COG" & VISITNUM >= 0) %>% distinct(USUBJID)
+Fix 2: qs_postbl <- qs %>% filter(QSCAT == "ADAS-COG" & VISITNUM > 0) %>% distinct(USUBJID)

-Bug 3: TRT01PN = case_when(ACTARMCD == "Xan_Lo" ~ 81L, ACTARMCD == "Xan_Hi" ~ 54L)
+Fix 3: TRT01PN = case_when(ACTARMCD == "Xan_Lo" ~ 54L, ACTARMCD == "Xan_Hi" ~ 81L)

-Bug 4: adsl <- dm %>% select(STUDYID, USUBJID, ...)
+Fix 4: adsl <- dm %>% filter(ACTARMCD != "Scrnfail") %>% select(STUDYID, USUBJID, ...)

Summary of fixes:
1. SAFFL requires EXDOSE > 0 (not just non-missing)
2. EFFFL requires post-baseline visit (VISITNUM > 0, not >= 0)
3. TRT01PN mapping corrected: Xan_Lo=54, Xan_Hi=81
4. Screen failures (ACTARMCD='Scrnfail') filtered out before ADSL derivation
""",
    "T5.2.adam_adae_debug.001": """--- a/adam_adae.R
+++ b/adam_adae.R
@@ -1,5 +1,5 @@
-Bug 1: TRTEMFL = if_else(ASTDT > TRTSDT, "Y", "N")
+Fix 1: TRTEMFL = if_else(ASTDT >= TRTSDT, "Y", "N")

-Bug 2: ASTDY = as.integer(ASTDT - TRTSDT)
+Fix 2: ASTDY = as.integer(ASTDT - TRTSDT) + 1L

-Bug 3: TRTPN = TRT01AN; TRTAN = TRT01PN
+Fix 3: TRTPN = TRT01PN; TRTAN = TRT01AN

Summary of fixes:
1. TRTEMFL uses >= for start date comparison (AE on first dose day is TEAE)
2. ASTDY adds +1 offset (first dose day = day 1, not day 0)
3. TRTPN (planned numeric) from TRT01PN, TRTAN (actual numeric) from TRT01AN
""",
    "T5.2.adam_adadas_debug.001": """--- a/adam_adadas.R
+++ b/adam_adadas.R
@@ -1,5 +1,5 @@
-Bug 1: adadas_locf <- adadas %>% filter(!is.na(AVAL)) %>% fill(...)
+Fix 1: adadas_locf <- adadas %>% filter(VISITNUM > 0 & !is.na(AVAL)) %>% fill(...)

-Bug 2: AWHI = case_when(VISITNUM == 24 ~ 252)
+Fix 2: AWHI = case_when(VISITNUM == 24 ~ 336)

-Bug 3: ANL01FL = if_else(!is.na(AVAL), "Y", "")
+Fix 3: ANL01FL = if_else(PARAMCD == "ACTOT" & !is.na(AVAL), "Y", "")

-Bug 4: CHG = BASE - AVAL
+Fix 4: CHG = AVAL - BASE

Summary of fixes:
1. LOCF excludes baseline (VISITNUM==0) from carry-forward pool
2. Week 24 visit window upper bound corrected from 252 to 336 days
3. ANL01FL only flagged for PARAMCD='ACTOT' per SAP
4. CHG direction corrected: AVAL - BASE (not BASE - AVAL)
""",
    "T5.3.tlf_demo_debug.001": """--- a/tlf_demographic.R
+++ b/tlf_demographic.R
@@ -1,5 +1,5 @@
-Bug 1: adsl <- read_xpt("adsl.xpt") %>% filter(SAFFL == "Y")
+Fix 1: adsl <- read_xpt("adsl.xpt") %>% filter(ITTFL == "Y")

-Bug 2: formatC(mean(x), digits=1, format="e")
+Fix 2: formatC(mean(x), digits=1, format="f")

-Bug 3: lyt <- basic_table(show_colcounts = TRUE) %>% split_cols_by("TRT01P")
+Fix 3: lyt <- basic_table(show_colcounts = TRUE) %>% split_cols_by("TRT01P") %>% add_overall_col("Total")

Summary of fixes:
1. Population filter changed from Safety (SAFFL) to ITT (ITTFL)
2. Statistic format changed from scientific notation ('e') to fixed ('f')
3. Added overall total column to table layout
""",
    "T5.3.tlf_ae_debug.001": """--- a/tlf_ae_soc_pt.R
+++ b/tlf_ae_soc_pt.R
@@ -1,5 +1,5 @@
-Bug 1: pct = n / 254 * 100  (hardcoded total N)
+Fix 1: pct = n / treatment_N * 100  (per-group denominator)

-Bug 2: filter_at(vars(starts_with("soc_pct")), any_vars(. >= 5))
+Fix 2: filter_at(vars(starts_with("pt_pct")), any_vars(. >= 5))

-Bug 3: set_where(TRUE)  (no TEAE filter)
+Fix 3: set_where(TRTEMFL == "Y")

Summary of fixes:
1. Percentage denominator uses treatment-group-specific N
2. 5% threshold applied at PT level, not SOC level
3. TRTEMFL filter added to include only treatment-emergent AEs
""",
    "T5.3.tlf_km_debug.001": """--- a/tlf_km_plot.R
+++ b/tlf_km_plot.R
@@ -1,5 +1,5 @@
-Bug 1: Surv(AVAL, CNSR) ~ TRT01P
+Fix 1: Surv(AVAL, 1 - CNSR) ~ TRT01P

-Bug 2: km_fit <- survfit(Surv(AVAL, event) ~ TRT01P, data = adtte_saf)
+Fix 2: km_fit <- survfit(Surv(AVAL, event) ~ TRT01P, data = adtte_saf, conf.int = 0.95)

-Bug 3: risk.table.col = "grey"
+Fix 3: risk.table.col = "strata"

Summary of fixes:
1. Event indicator corrected: 1-CNSR (CNSR=1 is censored, 0 is event)
2. survfit call includes conf.int=0.95 to compute confidence bands
3. Risk table colored by treatment group (strata) instead of uniform grey
""",
    "T5.3.tlf_primary_debug.001": """--- a/tlf_primary.R
+++ b/tlf_primary.R
@@ -1,5 +1,5 @@
-Bug 1: lm(CHG ~ TRTPN + SITEGR1, data = adadas_anl)
+Fix 1: lm(CHG ~ factor(TRTPN) + SITEGR1 + BASE, data = adadas_anl)

-Bug 2: filter(DTYPE == "LOCF")
+Fix 2: filter(is.na(DTYPE) | DTYPE == "LOCF")

-Bug 3: lm(CHG ~ TRTPN + SITEGR1 + BASE, ...)
+Fix 3: lm(CHG ~ factor(TRTPN) + SITEGR1 + BASE, ...)

-Bug 4: filter(ITTFL == "Y")
+Fix 4: filter(EFFFL == "Y")

Summary of fixes:
1. ANCOVA model includes BASE as covariate per SAP
2. LOCF filter includes original observations (DTYPE=NA) plus LOCF imputed
3. TRTPN converted to factor for categorical treatment comparison
4. Population filter changed from ITT (ITTFL) to Efficacy (EFFFL)
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
        gold_file = gold_dir / "expected_output.patch"
        gold_file.write_text(gold_data + "\n", encoding="utf-8")
        print(f"  wrote {gold_file}")

    print(f"\nGenerated {len(all_tasks)} T5 tasks in {TASKS_DIR}")
    print(f"Gold outputs in {GOLD_ROOT}")


if __name__ == "__main__":
    main()
