"""CLI entry point for ClinProg-Bench."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from clinprog_bench.schema import validate_tasks_dir

console = Console()


def _cmd_validate(tasks_dir: Path) -> None:
    """Validate all task JSON files in *tasks_dir*."""
    if not tasks_dir.is_dir():
        console.print(f"[bold red]Not a directory: {tasks_dir}[/bold red]")
        sys.exit(1)

    try:
        tasks = validate_tasks_dir(tasks_dir)
    except Exception as exc:
        console.print(f"[bold red]Validation error:[/bold red] {exc}")
        sys.exit(1)

    console.print(
        f"[bold green]Validation passed:[/bold green] {len(tasks)} task(s) validated"
    )


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="clinprog-bench",
        description="ClinProg-Bench: clinical programming benchmark toolkit",
    )
    subparsers = parser.add_subparsers(dest="command")

    validate_p = subparsers.add_parser(
        "validate", help="Validate task JSON files against the schema"
    )
    validate_p.add_argument(
        "tasks_dir",
        type=Path,
        help="Path to the tasks/ directory",
    )

    args = parser.parse_args()

    if args.command == "validate":
        _cmd_validate(args.tasks_dir)
    else:
        parser.print_help()
        sys.exit(1)


__all__ = ["main"]
