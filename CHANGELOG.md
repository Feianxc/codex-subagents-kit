# Changelog

All notable changes to this repository will be documented in this file.

This project follows a lightweight, human-maintained changelog style:

- keep entries concise
- prefer evidence-backed summaries
- do not over-claim runtime behavior

## [0.2.0] - 2026-04-14

### Added

- add `references/official-patterns-2026.md`
- add `references/research-swarm-pattern.md`
- add `references/scoring-rubric.md`
- add `evals/forward-regression.cases.json`
- add `scripts/run_codex_skill_regression.py`
- add open-source sync report for the 2026-04 skill upgrade

### Changed

- upgrade `skills/codex-subagents-kit/SKILL.md` toward `single-controller first`, `ownership-first`, `research-swarm`, and stronger stop/fallback guidance
- upgrade `references/artifact-contract.md` to `v2`
- upgrade runtime probe and run checker to emphasize session evidence, config-guided evidence, and closure integrity
- refresh project-agent templates, trigger fixtures, smoke prompt, and supporting references
- refresh README and repository history notes so the public repo matches the currently deployed skill more closely

### Notes

- this release reflects a **public-repo sync of the current final skill**
- it does **not** by itself claim a brand-new public live-eval campaign

## [0.1.0] - 2026-03-20

### Added

- initial public release of `codex-subagents-kit`
- publish Codex-native skill, baseline variant, fixtures, prompts, scripts, and curated reports
- document discoverability limits, routing collisions, and representative local history artifacts
