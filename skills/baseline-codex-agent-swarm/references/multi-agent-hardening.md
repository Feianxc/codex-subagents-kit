# Multi-Agent Hardening

## Core Rules

1. Keep prompts narrow.
2. Keep outputs file-based.
3. Keep ownership explicit.
4. Keep acceptance testable.
5. Keep claims honest.

## Child Run Prompt Contract

Every child prompt should contain:

- `task_id`
- objective
- allowed scope
- forbidden scope
- input path
- output path
- acceptance
- stop condition

Example skeleton:

```text
Task ID: RSRCH-01
Objective: Compare two existing files and summarize the differences.
Allowed scope: Read-only analysis of the listed files.
Forbidden scope: Do not edit source files. Do not widen scope.
Input path: docs/a.md, docs/b.md
Output path: .workspace/codex-swarm/runs/<run_id>/outputs/rsrch-01.md
Acceptance: Output contains a concise diff summary and 3 concrete recommendations.
Stop condition: Finish after writing the output file.
```

## File Boundary Rules

- Do not spawn two child runs that edit the same hot file at the same time.
- Prefer analysis-first child runs and controller-owned merge steps.
- When edits are unavoidable, partition files or time-slice the runs.

## Honesty Rules

- `native-multi-agent` means the runtime truly provides native multi-agent behavior.
- `artifact-orchestrated-swarm` means the controller is orchestrating child `codex exec` runs.
- A feature flag alone is not proof of runtime capability.
- A planned child run is not a completed child run.

## Completion Rules

Do not call the run complete until:

1. registry statuses are updated
2. outputs are present
3. acceptance was checked
4. audit notes reflect deviations
