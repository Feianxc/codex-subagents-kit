# Open-source Sync Report — 2026-04-14 Skill Upgrade

## Purpose

把当前最终版 `codex-subagents-kit` skill 内容同步回你之前已经开源的仓库，同时保持仓库原有的公开发布结构、摘要报告策略和历史索引。

## Sync source and target

- Source iteration copy:
  - `E:\工作区\10_Projects_项目\AI与自动化\CODEX团队功能优化\codex-subagents-kit-iteration-20260413\skill\codex-subagents-kit\`
- Verified deployed copy:
  - `C:\Users\feian\.codex\skills\codex-subagents-kit\`
- Target public repo:
  - `E:\工作区\工作区分类\AI_Agents\codex-subagents-kit\skills\codex-subagents-kit\`

在同步前已确认：

- 当前迭代目录中的 skill
- 本机 Codex 全局已部署的 skill

两者内容一致，可视作同一个“最终版”来源。

## What changed in the public repo

### Newly added to the public skill

- `evals/forward-regression.cases.json`
- `references/official-patterns-2026.md`
- `references/research-swarm-pattern.md`
- `references/scoring-rubric.md`
- `scripts/run_codex_skill_regression.py`

### Refreshed from the final iteration

- `SKILL.md`
- `agents/openai.yaml`
- `assets/project-agents/*.toml`
- `evals/evals.trigger.json`
- `references/artifact-contract.md`
- `references/codex-runtime-notes.md`
- `references/decision-matrix.md`
- `references/multi-agent-hardening.md`
- `references/project-agents.md`
- `references/selection-guide.md`
- `references/topology-catalog.md`
- `scripts/check_codex_swarm_run.py`
- `scripts/init_codex_swarm_run.py`
- `scripts/probe_codex_swarm_runtime.py`
- `tests/smoke.json`

## Upgrade highlights

这次同步后的公开版 skill，重点提升在于：

1. 从“Subagents 工作台”进一步收敛为“多智能体 / 子智能体编排工作台”
2. 明确强调 `single-controller first`
3. 明确强调 `ownership-first`
4. 把 `research-swarm` 和 `official-patterns bridge` 纳入公开版
5. 把 `artifact-contract` 升级到 `v2`
6. 把 runtime probe 与 run checker 升级为更强调证据与闭环的版本
7. 把 forward regression cases 和 scoring rubric 一并公开

## What was intentionally not synced

为了保持公开仓库干净、可审计、适合开源：

- 没有提交 `.workspace/`
- 没有提交本机 `runs/`
- 没有提交 `__pycache__/`
- 没有提交 `.pyc`
- 没有把本机绝对路径痕迹的大体量运行产物直接带进仓库

## Local validation after sync

已执行的本地校验：

1. `quick_validate_skill.py --skill-dir skills/codex-subagents-kit`
2. `validate_release_repo.py --repo-root .`

结果：

- `quick_validate_skill.py` → `STATUS=ok`
- `validate_release_repo.py` → `STATUS=ok`

## Evidence posture

这份报告证明的是：

- 公开仓库已经成功同步到 2026-04 的最终版 skill 内容
- 仓库结构仍满足原有公开版校验要求

这份报告**不等价于**新的公开 live eval 结论。  
如果后续要对外宣称“新的公开发布版已通过新一轮完整回归 / 新一轮 live eval”，仍建议再补一套独立的公开评测报告。
