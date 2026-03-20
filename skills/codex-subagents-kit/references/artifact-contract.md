# Artifact Contract

## Required run artifacts

- `preflight.md`
- `agent-blueprints.md`
- `execution-plan.md`
- `task-registry.md`
- `protocol-audit.md`
- `team-report.md`
- `scorecard.md`

## Registry minimum columns

- `Task ID`
- `Owner`
- `Status`
- `Blocked By`
- `Input Path`
- `Output Path`
- `Acceptance`
- `Spawn Reason`

## Protocol audit minimum fields

- chosen mode
- four-gate result
- native / config-guided / artifact evidence
- child `codex exec` usage
- deviations and downgrades
- closure state

## Scorecard dimensions

- Codex alignment
- Context efficiency
- Mode-selection accuracy
- Spawn quality
- Validation / acceptance
- Audit honesty

## Completion rule

Do not call the run complete until:

1. registry is updated
2. expected outputs exist
3. acceptance is checked
4. protocol-audit reflects deviations
5. scorecard is updated
