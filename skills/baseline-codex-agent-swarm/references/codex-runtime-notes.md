# Codex Runtime Notes

Snapshot date: 2026-03-11

These notes are local evidence for this workstation, not a universal guarantee for every Codex build.

## Observed Local Facts

- `codex features list` shows `multi_agent` as `experimental`.
- The current local value is `true`.
- `~/.codex/config.toml` currently sets `[features].multi_agent = true`.
- `collaboration_modes` is marked `removed`.
- The local `config.toml` is thin and mainly sets provider/model.
- The public CLI help surfaces `codex exec`, but does not describe a Claude Code style `TeamCreate` / `TaskCreate` runtime.
- Some bridged Codex runtimes may expose native agent tools directly in-session, but that is runtime evidence, not a generic CLI guarantee.

## Practical Interpretation

Treat Codex on this machine as:

- capable of native multi-agent when both the feature flag and fresh runtime tool evidence are present
- strong at controller-style orchestration
- stable for file-based planning and audit
- usable for child `codex exec` subprocesses
- not proven to expose a stable native team runtime from CLI help alone

## Recommended Default

Prefer `native-multi-agent` only when you have both:

1. `codex features list` showing `multi_agent = true`
2. fresh current-session evidence that native agent tools are really exposed

If either proof is missing, default to `artifact-orchestrated-swarm`.

## Minimum Capability Probe

1. Run `codex features list`.
2. Record whether `multi_agent` is enabled.
3. Record whether the current runtime actually exposes native child-agent tools, for example `spawn_agent`, `send_input`, `wait`, `close_agent`.
4. If both proofs exist, prefer `native-multi-agent`.
5. If proof is absent or ambiguous, stay in `artifact-orchestrated-swarm`.
