"""Build anonymized supplementary package for NeurIPS submission."""
import shutil, pathlib, re

root = pathlib.Path(r"C:\Users\yanmi\Downloads\ClinAgent-main\ClinAgent-main\bench-program\clinprog-bench")
stage = root / "paper" / "submission" / "supplementary" / "clinprog-bench-anon"

# Clean staging area
if stage.exists():
    shutil.rmtree(stage)
stage.mkdir(parents=True)

# Dirs to include
include_dirs = ["src", "tasks", "gold", "fixtures", "scripts", "tests", "docs", "review_package"]
for d in include_dirs:
    src = root / d
    if src.exists():
        shutil.copytree(src, stage / d, dirs_exist_ok=True)

# Files to include
include_files = [
    "pyproject.toml", "README.md", "CITATION.cff", "DATA_CARD.md",
    "croissant.json", "LICENSE", "LICENSE-DATA",
]
for f in include_files:
    src = root / f
    if src.is_file():
        shutil.copy2(src, stage / f)

# CI workflow
github_dir = root / ".github"
if github_dir.exists():
    shutil.copytree(github_dir, stage / ".github", dirs_exist_ok=True)

# Anonymize text files
text_exts = {".md", ".py", ".json", ".toml", ".yml", ".yaml", ".cff", ".txt", ".cfg", ".R"}
count = 0
for p in stage.rglob("*"):
    if p.is_file() and p.suffix in text_exts:
        try:
            text = p.read_text(encoding="utf-8")
            original = text
            text = re.sub(r"anonymous", "anonymous", text, flags=re.IGNORECASE)
            text = re.sub(r"Anonymous Author", "Anonymous Author", text)
            text = re.sub(r"0000-0000-0000-0000", "0000-0000-0000-0000", text)
            if text != original:
                p.write_text(text, encoding="utf-8")
                count += 1
        except (UnicodeDecodeError, PermissionError):
            pass

file_count = sum(1 for _ in stage.rglob("*") if _.is_file())
print(f"Staged {file_count} files, anonymized {count} files")

# Create ZIP
zip_path = root / "paper" / "submission" / "supplementary" / "clinprog-bench-supplementary"
shutil.make_archive(str(zip_path), "zip", stage.parent, stage.name)
zip_size = pathlib.Path(str(zip_path) + ".zip").stat().st_size / (1024 * 1024)
print(f"ZIP: clinprog-bench-supplementary.zip ({zip_size:.1f} MB)")
