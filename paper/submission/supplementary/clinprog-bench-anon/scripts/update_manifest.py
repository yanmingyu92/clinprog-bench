"""Update gold/manifest.json with SHA-256 hashes of all gold outputs.

Scans gold/ directory for expected_output.* files, computes SHA-256,
and writes a fresh manifest.json.

Usage:
    python scripts/update_manifest.py
"""

from __future__ import annotations

import hashlib
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GOLD_DIR = ROOT / "gold"
MANIFEST_PATH = GOLD_DIR / "manifest.json"


def _sha256_hex(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def update_manifest() -> int:
    """Rebuild manifest.json from all gold output files. Returns file count."""
    files: dict[str, str] = {}

    for gold_file in sorted(GOLD_DIR.rglob("expected_output.*")):
        rel = gold_file.relative_to(GOLD_DIR)
        key = str(rel).replace("\\", "/")
        files[key] = _sha256_hex(gold_file)

    manifest = {
        "description": "SHA-256 hashes of all gold-standard outputs",
        "generated": str(date.today()),
        "count": len(files),
        "files": dict(sorted(files.items())),
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    return len(files)


def main() -> None:
    """Run the manifest update."""
    print("Updating gold/manifest.json...")
    count = update_manifest()
    print(f"  Hashed {count} gold files into manifest")


if __name__ == "__main__":
    main()
