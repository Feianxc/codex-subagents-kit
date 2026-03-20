#!/usr/bin/env python3
"""Check a Codex swarm run for required artifacts and registry hygiene."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_FILES = (
    "preflight.md",
    "agent-blueprints.md",
    "execution-plan.md",
    "task-registry.md",
    "protocol-audit.md",
    "team-report.md",
    "scorecard.md",
)

REQUIRED_SUBDIRS = ("prompts", "outputs", "logs", "manifests")
REQUIRED_REGISTRY_COLUMNS = (
    "Task ID",
    "Owner",
    "Status",
    "Blocked By",
    "Input Path",
    "Output Path",
    "Acceptance",
    "Spawn Reason",
)


def extract_markdown_table(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    for idx, line in enumerate(lines):
        if "|" not in line:
            continue
        if idx + 1 >= len(lines):
            continue
        separator = lines[idx + 1]
        if "|" not in separator or "-" not in separator:
            continue
        header = [cell.strip() for cell in line.strip().strip("|").split("|")]
        rows = []
        for row_line in lines[idx + 2 :]:
            if not row_line.strip():
                break
            if "|" not in row_line:
                break
            cells = [cell.strip() for cell in row_line.strip().strip("|").split("|")]
            if len(cells) != len(header):
                continue
            if set(cells) == {"---"}:
                continue
            rows.append(dict(zip(header, cells)))
        return header, rows
    return [], []


def main() -> int:
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    parser = argparse.ArgumentParser(description="Check a Codex swarm run directory.")
    parser.add_argument("--run-root", required=True, help="Path to the run root.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of text.")
    args = parser.parse_args()

    run_root = Path(args.run_root).resolve()
    missing_files = [name for name in REQUIRED_FILES if not (run_root / name).exists()]
    missing_subdirs = [name for name in REQUIRED_SUBDIRS if not (run_root / name).is_dir()]

    header = []
    rows = []
    registry_path = run_root / "task-registry.md"
    if registry_path.exists():
        header, rows = extract_markdown_table(registry_path)

    missing_columns = [name for name in REQUIRED_REGISTRY_COLUMNS if name not in header]
    pending_rows = [
        row["Task ID"]
        for row in rows
        if row.get("Status", "").strip().lower() in {"pending", "blocked", "todo", "in_progress"}
    ]
    missing_acceptance = [
        row["Task ID"] for row in rows if not row.get("Acceptance", "").strip()
    ]
    missing_spawn_reason = [
        row["Task ID"] for row in rows if not row.get("Spawn Reason", "").strip()
    ]

    failures = []
    warnings = []

    if not run_root.exists():
        failures.append("run_root_missing")
    if missing_files:
        failures.append("missing_required_files")
    if missing_subdirs:
        failures.append("missing_required_subdirectories")
    if registry_path.exists() and missing_columns:
        failures.append("task_registry_missing_columns")

    if registry_path.exists() and not rows:
        warnings.append("task_registry_has_no_rows")
    if pending_rows:
        warnings.append("task_registry_has_open_tasks")
    if missing_acceptance:
        warnings.append("task_registry_missing_acceptance")
    if missing_spawn_reason:
        warnings.append("task_registry_missing_spawn_reason")

    verdict = "PASS"
    exit_code = 0
    if failures:
        verdict = "FAIL"
        exit_code = 1
    elif warnings:
        verdict = "WARN"

    result = {
        "run_root": str(run_root),
        "verdict": verdict,
        "failures": failures,
        "warnings": warnings,
        "missing_files": missing_files,
        "missing_subdirs": missing_subdirs,
        "task_count": len(rows),
        "pending_tasks": pending_rows,
        "missing_columns": missing_columns,
        "missing_acceptance": missing_acceptance,
        "missing_spawn_reason": missing_spawn_reason,
    }

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print(f"VERDICT={verdict}")
        print(f"RUN_ROOT={run_root}")
        print(f"TASK_COUNT={len(rows)}")
        if missing_files:
            print("MISSING_FILES=" + ",".join(missing_files))
        if missing_subdirs:
            print("MISSING_SUBDIRS=" + ",".join(missing_subdirs))
        if missing_columns:
            print("MISSING_COLUMNS=" + ",".join(missing_columns))
        if pending_rows:
            print("PENDING_TASKS=" + ",".join(pending_rows))
        if missing_acceptance:
            print("MISSING_ACCEPTANCE=" + ",".join(missing_acceptance))
        if missing_spawn_reason:
            print("MISSING_SPAWN_REASON=" + ",".join(missing_spawn_reason))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
