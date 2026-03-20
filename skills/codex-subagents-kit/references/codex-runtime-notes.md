# Codex Runtime Notes

Snapshot date: 2026-03-20

These notes are local evidence for this workstation, not a universal guarantee for every Codex build.

## Observed Local Facts

- `codex --version` returns `codex-cli 0.116.0`.
- `codex features list` shows `multi_agent` as `stable` and enabled (`true`).
- `~/.codex/config.toml` currently sets `[features].multi_agent = true`.
- `collaboration_modes` is marked `removed`.
- `codex --help` and `codex exec --help` expose `codex exec`, but do not expose a Claude Code style `TeamCreate / TaskCreate` CLI.
- `~/.codex/agents/` does not currently exist on this workstation.
- Some bridged Codex runtimes may expose native agent tools directly in-session, but that is session evidence, not a generic CLI guarantee.

## Practical Interpretation

Treat Codex on this machine as:

- product-level support for Subagents / multi-agent related flows is present
- controller-style orchestration is strong
- file-based planning and audit are stable
- `codex exec` child runs are usable
- direct native child-agent tooling still requires live session evidence

## Recommended Default

Use the four-gate model:

1. Product Gate: confirm version/features/config support
2. Session Gate: confirm live native tool evidence
3. Policy Gate: confirm this run should actually spawn
4. Task Gate: confirm the task is spawn-worthy

If Product Gate passes but Session Gate does not, prefer `config-guided-codex-subagents`.
If only a stable degraded path is needed, use `artifact-orchestrated-swarm`.
