# Chat Records and Iteration Index

这个文档用来回答两个问题：

1. 这个 skill 当时主要在哪些目录里被持续迭代？
2. 对应的“聊天式记录 / prompt-response 证据”现在还能在本机哪里找到？

## 原始本机项目位置

主要源项目目录：

```text
E:\工作区\10_Projects_项目\AI与自动化\CODEX团队功能优化
```

## 已定位到的高价值迭代痕迹

### 1) 早期实验阶段：`skill-lab`

用途：baseline 与 optimized 版对照实验。

重点目录：

- `skill-lab/runs/20260320-live-eval-01`
- `skill-lab/runs/20260320-live-eval-05`
- `skill-lab/reports/score-report-live-eval-05.md`
- `skill-lab/reports/global-skill-cutover-20260320.md`

说明：

- 这里能看到 `codex-agent-swarm-baseline` 与 `codex-agent-swarm-optimized` 的早期比较
- 这是从“实验版 swarm 命名”收敛到“Codex Subagents Kit”之前的重要阶段

### 2) 发布收敛阶段：`skill-lab+`

用途：公开发布版命名、验证、README 与开源仓库补全。

重点目录：

- `skill-lab+/skills/codex-subagents-kit/`
- `skill-lab+/reports/final-release-validation-20260320.md`
- `skill-lab+/reports/score-report-release-eval-04-final-candidate.md`
- `skill-lab+/reports/discoverability-report-release-02-post-cutover.md`
- `skill-lab+/runs/20260320-release-eval-04-final-candidate/`
- `skill-lab+/runs/20260321-natural-trigger-probe-01/`

说明：

- 这里能看到正式命名从 `codex-agent-swarm-optimized` 收敛到 `codex-subagents-kit`
- `prompt.md` / `response.md` / `events.jsonl` 是最接近“聊天记录”的第一手材料

### 3) 子 agent 行为烟测：`.workspace/subagent-model-smoke`

用途：验证子 agent / skill 介入前后，模型行为和输出结构的变化。

重点文件：

- `.workspace/subagent-model-smoke/before.jsonl`
- `.workspace/subagent-model-smoke/with-skill.jsonl`
- `.workspace/subagent-model-smoke/after-global-policy.jsonl`
- `.workspace/subagent-model-smoke/after-global-policy-team-zh.jsonl`

说明：

- 这些是结构化的线程事件日志
- 能看到 `spawn_agent` / `wait` / `close_agent` 等工具级调用痕迹
- `with-skill.jsonl` 明确显示了 `codex-subagents-kit` 被使用后的回复结构

### 4) 路由冲突证据：自然语言探针

关键证据：

- `skill-lab+/runs/20260321-natural-trigger-probe-01/prompt.md`
- `skill-lab+/runs/20260321-natural-trigger-probe-01/response.md`

结论：

- 自然语言“请帮我创建一个AGENT团队来处理这个任务”没有命中 `codex-subagents-kit`
- 实际命中了 `agent-team-planner`
- 这就是为什么仓库明确建议使用 `Use $codex-subagents-kit`

## 本开源整理仓库中已复制的代表性原始片段

为方便公开展示和回溯，下面这些小体量原始片段已经复制到：

```text
docs/history/raw/
```

包含：

- `20260320-live-eval-01-optimized-topology-prompt.md`
- `20260320-live-eval-05-optimized-topology-response.md`
- `20260320-release-eval-04-final-candidate-topology-prompt.md`
- `20260320-release-eval-04-final-candidate-topology-response.md`
- `20260321-natural-trigger-probe-prompt.md`
- `20260321-natural-trigger-probe-response.md`

## 2026-04-09 开源整理同步说明

在本次开源整理中，又额外发现当前本机安装版 skill 比 2026-03-20 发布仓库版更新了两处内容：

- `skills/codex-subagents-kit/SKILL.md`
- `skills/codex-subagents-kit/references/selection-guide.md`

因此这个开源整理目录在保留 2026-03-20 发布证据的同时，叠加同步了当前本机安装版的这两份较新文件，用于让公开仓库更贴近你现在实际在用的版本。

## 2026-04-14 二次升级同步说明

在本次升级同步中，公开仓库进一步对齐到了你当前迭代目录 / 本机安装版的最终版 skill。

本次高价值来源目录：

- `codex-subagents-kit-iteration-20260413/skill/codex-subagents-kit/`
- `C:\Users\feian\.codex\skills\codex-subagents-kit\`

这次不再只是同步零散单文件，而是把公开仓库中的 `skills/codex-subagents-kit/` 整体更新到新版能力面，重点包括：

- `SKILL.md`：强化 `single-controller first`、`ownership-first`、`research-swarm`、停止条件与边界表达
- `references/artifact-contract.md`：升级为 `v2`
- `references/official-patterns-2026.md`
- `references/research-swarm-pattern.md`
- `references/scoring-rubric.md`
- `scripts/probe_codex_swarm_runtime.py`
- `scripts/check_codex_swarm_run.py`
- `scripts/run_codex_skill_regression.py`
- `evals/forward-regression.cases.json`

这意味着公开仓库现在已经不只是 2026-03-20 的发布快照，而是叠加了 2026-04 的“实现层闭环”升级版本。

同时保留的原则：

- 仍然不把本机大体量 `runs/` 原始产物直接提交到公开仓库
- 仍然把公开仓库定位为“技能本体 + 摘要报告 + 历史索引”
- 若未来需要新的公开发布结论，仍建议基于新的独立 eval / regression 产物再补正式报告
