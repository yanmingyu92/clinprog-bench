#!/usr/bin/env python3
"""Execute gold-standard SAS/R programs against Pilot01 data.

Generates .xpt output files for T1 code-generation tasks, hashes all
outputs, and updates gold/manifest.json.

Usage:
    # Dry run — show what would be executed
    python scripts/execute_gold.py --dry-run

    # Execute R gold scripts only (SAS requires manual operator run)
    python scripts/execute_gold.py --r-only

    # Execute all (SAS must be on PATH or specified via --sas-path)
    python scripts/execute_gold.py --sas-path "/c/Program Files/SASHome/SASFoundation/9.4/sas.exe"
"""

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR = REPO_ROOT / "gold"
TASKS_DIR = REPO_ROOT / "tasks"

# Pilot01 substrate paths (relative to bench-program parent)
PILOT01_ROOT = (
    REPO_ROOT.parent / "track1-pilot01" / "external" / "eSubmission-Benchmark"
)

# Path mappings: placeholder -> actual Pilot01 path
# Output directory for executed gold scripts
OUTPUT_DIR = REPO_ROOT / "gold" / "_exec_output"

PATH_MAP = {
    # Raw data
    "path/to/raw/data": str(PILOT01_ROOT / "03_raw_data"),
    # SDTM datasets (inputs)
    "path/to/sdtm/output": str(PILOT01_ROOT / "04_sdtm" / "datasets"),
    "path/to/sdtm/ae.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "ae.xpt"),
    "path/to/sdtm/dm.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "dm.xpt"),
    "path/to/sdtm/ds.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "ds.xpt"),
    "path/to/sdtm/ex.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "ex.xpt"),
    "path/to/sdtm/lb.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "lb.xpt"),
    "path/to/sdtm/mh.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "mh.xpt"),
    "path/to/sdtm/qs.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "qs.xpt"),
    "path/to/sdtm/sc.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "sc.xpt"),
    "path/to/sdtm/suppdm.xpt": str(
        PILOT01_ROOT / "04_sdtm" / "datasets" / "suppdm.xpt"
    ),
    "path/to/sdtm/vs.xpt": str(PILOT01_ROOT / "04_sdtm" / "datasets" / "vs.xpt"),
    # ADaM datasets (inputs for downstream tasks)
    "path/to/adam/output": str(PILOT01_ROOT / "05_adam" / "datasets"),
    "path/to/adam/adsl.xpt": str(PILOT01_ROOT / "05_adam" / "datasets" / "adsl.xpt"),
    "path/to/adam/adae.xpt": str(PILOT01_ROOT / "05_adam" / "datasets" / "adae.xpt"),
    "path/to/adam/adtte.xpt": str(PILOT01_ROOT / "05_adam" / "datasets" / "adtte.xpt"),
    # Metadata
    "path/to/adam_spec.xlsx": str(
        PILOT01_ROOT / "05_adam" / "ADaM_Specifications.xlsx"
    ),
    # Outputs (resolve to gold execution output directory)
    "path/to/output/adsl.xpt": str(OUTPUT_DIR / "adsl.xpt"),
    "path/to/output/adae.xpt": str(OUTPUT_DIR / "adae.xpt"),
    "path/to/output/adadas.xpt": str(OUTPUT_DIR / "adadas.xpt"),
    "path/to/output/tlf-demographic.rtf": str(OUTPUT_DIR / "tlf-demographic.rtf"),
    "path/to/output/tlf-ae-soc-pt.rtf": str(OUTPUT_DIR / "tlf-ae-soc-pt.rtf"),
    "path/to/output/tlf-kmplot.pdf": str(OUTPUT_DIR / "tlf-kmplot.pdf"),
    "path/to/output": str(OUTPUT_DIR),
}


def resolve_paths(content: str) -> str:
    """Replace placeholder paths with actual Pilot01 paths."""
    for placeholder, actual in PATH_MAP.items():
        content = content.replace(placeholder, actual.replace("\\", "/"))
    return content


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def collect_t1_tasks() -> list[dict]:
    """Collect all T1 code-generation task definitions."""
    tasks = []
    t1_dir = TASKS_DIR / "T1_codegen"
    for f in sorted(t1_dir.glob("*.json")):
        with open(f) as fh:
            task = json.load(fh)
            tasks.append(task)
    return tasks


def prepare_script(task: dict) -> tuple[Path, str] | None:
    """Prepare a gold script for execution by resolving paths.

    Returns (script_path, engine) or None if no executable gold found.
    """
    gold_path = REPO_ROOT / task["expected_outputs"]["gold_path"]

    for ext, engine in [(".sas", "SAS"), (".R", "R"), (".py", "Python")]:
        gold_file = gold_path / f"expected_output{ext}"
        if gold_file.exists():
            content = gold_file.read_text(encoding="utf-8")
            resolved = resolve_paths(content)

            # Ensure output directory exists for generated files
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            tmp = REPO_ROOT / "temp" / f"exec_{task['task_id']}{ext}"
            tmp.parent.mkdir(parents=True, exist_ok=True)
            tmp.write_text(resolved, encoding="utf-8")
            return tmp, engine

    return None


def execute_r(script_path: Path, task_id: str) -> dict:
    """Execute an R script and return result info."""
    print(f"  Executing R: {script_path.name}")
    try:
        result = subprocess.run(
            ["Rscript", str(script_path)],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=script_path.parent,
            encoding="utf-8",
            errors="replace",
        )
        return {
            "task_id": task_id,
            "engine": "R",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "task_id": task_id,
            "engine": "R",
            "returncode": -1,
            "success": False,
            "error": "timeout",
        }
    except FileNotFoundError:
        return {
            "task_id": task_id,
            "engine": "R",
            "returncode": -1,
            "success": False,
            "error": "Rscript not found",
        }


def execute_sas(script_path: Path, task_id: str, sas_path: str) -> dict:
    """Execute a SAS script and return result info."""
    print(f"  Executing SAS: {script_path.name}")
    try:
        result = subprocess.run(
            [
                sas_path,
                "-sysin",
                str(script_path),
                "-nosplash",
                "-noovp",
                "-log",
                str(script_path.with_suffix(".log")),
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )
        return {
            "task_id": task_id,
            "engine": "SAS",
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:] if result.stdout else "",
            "stderr": result.stderr[-2000:] if result.stderr else "",
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired:
        return {
            "task_id": task_id,
            "engine": "SAS",
            "returncode": -1,
            "success": False,
            "error": "timeout",
        }
    except FileNotFoundError:
        return {
            "task_id": task_id,
            "engine": "SAS",
            "returncode": -1,
            "success": False,
            "error": f"SAS not found at {sas_path}",
        }


def update_manifest():
    """Regenerate gold/manifest.json with hashes of all gold files."""
    manifest = {}
    for path in sorted(GOLD_DIR.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            rel = str(path.relative_to(GOLD_DIR)).replace(os.sep, "/")
            manifest[rel] = sha256_file(path)

    manifest_data = {
        "description": "SHA-256 hashes of all gold-standard outputs",
        "generated": "2026-04-26",
        "count": len(manifest),
        "files": manifest,
    }
    manifest_path = GOLD_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest_data, indent=2))
    print(f"\nUpdated manifest: {len(manifest)} files")


def main():
    parser = argparse.ArgumentParser(
        description="Execute gold-standard programs against Pilot01 data"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be executed without running",
    )
    parser.add_argument("--r-only", action="store_true", help="Execute R scripts only")
    parser.add_argument(
        "--sas-path", default="sas", help="Path to SAS executable (default: 'sas')"
    )
    parser.add_argument(
        "--clean", action="store_true", help="Remove temp files after execution"
    )
    args = parser.parse_args()

    tasks = collect_t1_tasks()
    print(f"Found {len(tasks)} T1 code-generation tasks\n")

    results = []
    sas_count = 0
    r_count = 0

    for task in tasks:
        task_id = task["task_id"]
        kind = task["expected_outputs"]["kind"]
        print(f"[{task_id}] kind={kind}")

        prepared = prepare_script(task)
        if prepared is None:
            print("  No executable gold script found")
            continue

        script_path, engine = prepared

        if args.dry_run:
            print(f"  DRY RUN: would execute {engine}: {script_path}")
            continue

        if engine == "R":
            if args.r_only or kind == "r_program":
                result = execute_r(script_path, task_id)
                results.append(result)
                r_count += 1
            else:
                print("  Skipped (use --r-only or run without flags)")
                continue
        elif engine == "SAS":
            if not args.r_only:
                result = execute_sas(script_path, task_id, args.sas_path)
                results.append(result)
                sas_count += 1
            else:
                print("  Skipped (R-only mode)")
                continue
        else:
            print(f"  Unsupported engine: {engine}")
            continue

        status = "PASS" if result["success"] else "FAIL"
        print(f"  -> {status}")
        if not result["success"] and result.get("stderr"):
            stderr_clean = (
                result["stderr"][:500].encode("ascii", errors="replace").decode()
            )
            print(f"     stderr: {stderr_clean}")

    # Summary
    if results:
        print(f"\n{'=' * 60}")
        passed = sum(r["success"] for r in results)
        print(f"Execution Summary: {passed}/{len(results)} succeeded")
        print(f"  SAS: {sas_count} tasks")
        print(f"  R:   {r_count} tasks")
        for r in results:
            status = "PASS" if r["success"] else "FAIL"
            print(f"  [{status}] {r['task_id']} ({r['engine']})")

    # Update manifest
    if not args.dry_run:
        update_manifest()

    # Clean temp files
    if args.clean:
        temp_dir = REPO_ROOT / "temp"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
            print("Cleaned temp files")

    # Return non-zero if any failed
    if results and not all(r["success"] for r in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
