# Codex Runtime Notes

Snapshot date: 2026-04-13

These notes are local evidence for this workstation, not a universal guarantee for every Codex build.

## Observed Local Facts

- `codex --version` returns `codex-cli 0.120.0`.
- `codex features list` shows `multi_agent` as `stable` and enabled (`true`).
- `~/.codex/config.toml` currently sets `[features].multi_agent = true`.
- 当前 `~/.codex/config.toml` 还设置了：
  - `model = "gpt-5.4"`
  - `model_reasoning_effort = "xhigh"`
  - `web_search = "live"`
- `collaboration_modes` 仍标记为 `removed`。
- `codex --help` and `codex exec --help` expose `codex exec`, but do not expose a Claude Code style `TeamCreate / TaskCreate` CLI.
- `~/.codex/agents/` 当前存在，但本次探查未观察到已定义的项目级角色文件。
- Some bridged Codex runtimes may expose native agent tools directly in-session, but that is session evidence, not a generic CLI guarantee.
- 2026-04-13 的 runtime probe 记录到当前 session 暴露了：
  - `spawn_agent`
  - `wait_agent`
  - `send_input`

## Practical Interpretation

Treat Codex on this machine as:

- product-level support for Subagents / multi-agent related flows is present
- controller-style orchestration is strong
- file-based planning and audit are stable
- `codex exec` child runs are usable
- direct native child-agent tooling still requires live session evidence
- `AGENTS.md` + `.codex/agents/` + `skills.config` are still the honest default for reusable project-level setup
- current local config is capable of live web research plus high-reasoning controller sessions

## Recommended Default

Use the four-gate model:

1. Product Gate: confirm version/features/config support
2. Session Gate: confirm live native tool evidence
3. Policy Gate: confirm this run should actually spawn
4. Task Gate: confirm the task is spawn-worthy

If Product Gate passes but Session Gate does not, prefer `config-guided-codex-subagents`.
If only a stable degraded path is needed, use `artifact-orchestrated-swarm`.
If the task is still small after gating, prefer `single-controller`.
If the task is research-heavy, combine the chosen runtime mode with a `research-swarm` overlay and a shared findings ledger.
