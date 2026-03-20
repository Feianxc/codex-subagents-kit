#!/usr/bin/env python3
"""Initialize a standard Codex swarm run directory."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ARTIFACTS = (
    "preflight.md",
    "agent-blueprints.md",
    "execution-plan.md",
    "task-registry.md",
    "protocol-audit.md",
    "team-report.md",
)

SUBDIRS = ("prompts", "outputs", "logs", "manifests")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def make_run_id(case_name: str) -> str:
    stamp = utc_now().strftime("%Y%m%d-%H%M%S")
    slug = "-".join(case_name.strip().lower().split())
    return f"{stamp}-{slug}"


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def build_preflight(run_id: str, run_root: Path, workspace_root: Path, case_name: str) -> str:
    return f"""# Preflight

- Run ID: `{run_id}`
- Run Root: `{run_root}`
- Workspace Root: `{workspace_root}`
- Case: `{case_name}`

## Final Goal

- [ ] Fill in the final outcome this run should achieve.

## Deliverables

- [ ] List the concrete files or outcomes required.

## Constraints

- [ ] Record file boundaries, safety limits, and time constraints.

## Success Criteria

- [ ] Define what counts as done.

## Spawn Candidates

| Task ID | Candidate | Why Spawn | Inputs | Outputs | Acceptance |
| --- | --- | --- | --- | --- | --- |

## Tasks Not Worth Spawning

| Task | Why Keep With Controller |
| --- | --- |
"""


def build_blueprints(run_id: str, run_root: Path) -> str:
    return f"""# Agent Blueprints

- Run ID: `{run_id}`
- Run Root: `{run_root}`

| Task ID | Role | Objective | Allowed Scope | Forbidden Scope | Input Path | Output Path | Acceptance |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""


def build_execution_plan(run_id: str, run_root: Path) -> str:
    return f"""# Execution Plan

- Run ID: `{run_id}`
- Run Root: `{run_root}`

## Chosen Mode

- Mode: `TBD`
- Feature flag evidence: `TBD`
- Native tool evidence: `TBD`
- Preferred mode when proven: `native-multi-agent`
- Fallback path: `artifact-orchestrated-swarm`

## Phases

1. Preflight and scope lock
2. Spawn gate and task registry
3. Child execution or controller execution
4. Merge and acceptance
5. Audit and final report

## Checkpoints

- [ ] Registry initialized
- [ ] Outputs assigned
- [ ] Acceptance rules written
- [ ] Audit updated
"""


def build_registry(run_id: str, run_root: Path) -> str:
    return f"""# Task Registry

- Run ID: `{run_id}`
- Run Root: `{run_root}`

| Task ID | Owner | Status | Blocked By | Input Path | Output Path | Acceptance | Spawn Reason |
| --- | --- | --- | --- | --- | --- | --- | --- |
"""


def build_protocol_audit(run_id: str, run_root: Path) -> str:
    return f"""# Protocol Audit

- Run ID: `{run_id}`
- Run Root: `{run_root}`

## Runtime Mode

- Claimed mode: `TBD`
- Feature flag state: `TBD`
- Native multi-agent used: `TBD`
- Native tool evidence: `TBD`
- Child `codex exec` used: `TBD`

## Evidence

- Capability probe:
- Native tool probe:
- Child run evidence:
- Deviation log:

## Final Assessment

- Registry closed: `TBD`
- Acceptance checked: `TBD`
- Remaining gaps:
"""


def build_team_report(run_id: str, run_root: Path) -> str:
    return f"""# Team Report

- Run ID: `{run_id}`
- Run Root: `{run_root}`

## Summary

- Mode:
- Goal:
- Result:

## Outputs

- List final artifacts and business outputs here.

## Open Risks

- List remaining risks or follow-ups here.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize a Codex swarm run directory.")
    parser.add_argument("--workspace-root", default=".", help="Workspace root that owns the run.")
    parser.add_argument("--case", required=True, help="Short case name used in the run id.")
    parser.add_argument("--run-id", help="Explicit run id. Default: timestamp + case slug.")
    args = parser.parse_args()

    workspace_root = Path(args.workspace_root).resolve()
    run_id = args.run_id or make_run_id(args.case)
    run_root = workspace_root / ".workspace" / "codex-swarm" / "runs" / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    for subdir in SUBDIRS:
        (run_root / subdir).mkdir(parents=True, exist_ok=True)

    write_if_missing(
        run_root / "preflight.md",
        build_preflight(run_id, run_root, workspace_root, args.case),
    )
    write_if_missing(run_root / "agent-blueprints.md", build_blueprints(run_id, run_root))
    write_if_missing(run_root / "execution-plan.md", build_execution_plan(run_id, run_root))
    write_if_missing(run_root / "task-registry.md", build_registry(run_id, run_root))
    write_if_missing(run_root / "protocol-audit.md", build_protocol_audit(run_id, run_root))
    write_if_missing(run_root / "team-report.md", build_team_report(run_id, run_root))

    manifest = {
        "run_id": run_id,
        "workspace_root": str(workspace_root),
        "run_root": str(run_root),
        "case_name": args.case,
        "created_at_utc": utc_now().isoformat(),
        "required_artifacts": list(ARTIFACTS),
        "subdirectories": list(SUBDIRS),
    }
    (run_root / "manifests" / "run.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(f"RUN_ID={run_id}")
    print(f"RUN_ROOT={run_root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
