# Codex Subagents Kit

Codex-native workflow, references, fixtures, and validation assets for building **honest multi-agent / subagent collaboration skills**.

> 一个面向 Codex 的开源 skill 工程仓库：聚焦 `Subagents`、`.codex/agents/`、`skills.config`、artifact-backed execution、四层门控与可验证的 audit / scorecard 闭环。

## 为什么做这个仓库

这个仓库的目标不是把 Codex 包装成“神秘的自动团队运行时”，而是提供一套 **符合当前可观察机制** 的工程化方法：

- 什么时候值得使用 subagents
- 什么时候应该退回到 controller + artifacts 路径
- 如何减少无效上下文消耗
- 如何让规划、执行、验证、审计留痕
- 如何把“能跑”提升为“可验证、可复现、可开源”

## 核心能力

- **四层门控（Four Gates）**
  - Product Gate
  - Session Gate
  - Policy Gate
  - Task Gate
- **模式选择**
  - `single-controller`
  - `native-subagents`
  - `config-guided-codex-subagents`
  - `artifact-orchestrated-swarm`
- **上下文控制**
  - 薄核心 `SKILL.md`
  - 深引用 `references/`
  - 规则动作脚本化
- **可验证闭环**
  - `run_root`
  - `task-registry`
  - `protocol-audit`
  - `team-report`
  - `scorecard`

## 这个仓库不承诺什么

- 不承诺“任何自然语言都一定会自动触发这个 skill”
- 不承诺“只要叫 team / swarm 就一定存在原生团队 runtime”
- 不把 `codex exec` 子运行冒充成 native multi-agent
- 不在没有 live session evidence 的情况下宣称当前会话一定支持 child-agent 工具

## 仓库结构

```text
.
├─ skills/
│  ├─ codex-subagents-kit/          # 当前公开发布版
│  └─ baseline-codex-agent-swarm/   # 基线对照版
├─ fixtures/                        # 用于 smoke / eval 的最小工作区
├─ prompts/                         # 测试 prompt 模板
├─ scripts/                         # 安装、校验、评测辅助脚本
├─ docs/                            # 触发行为、冲突路由、历史索引
├─ reports/                         # 公开保留的摘要报告
└─ .github/                         # Issue / PR 模板
```

## 快速开始

### 1) 校验 skill 目录

```bash
python scripts/quick_validate_skill.py --skill-dir skills/codex-subagents-kit
```

### 2) 校验仓库结构

```bash
python scripts/validate_release_repo.py --repo-root .
```

### 3) 安装到本机 Codex skills 目录

```bash
python scripts/install_skill.py --repo-root . --force
```

默认会安装到：

```text
~/.codex/skills/codex-subagents-kit
```

### 4) 查看版本变更摘要

```text
CHANGELOG.md
```

## 推荐调用方式

默认推荐：

```text
Use $codex-subagents-kit
```

需要更强确定性时：

```text
Use $codex-subagents-kit at <skill-path>
```

也可以显式点名：

```text
Use the skill named "codex-subagents-kit"
```

## 关键证据摘要

截至 **2026-03-20** 的接受版证据：

- live eval 最优版：`reports/score-report-release-eval-04-final-candidate.md`
  - `release total = 110`
  - `avg_input_tokens = 39874`
  - `avg_output_tokens = 2076`
- discoverability 最优版：`reports/discoverability-report-release-02-post-cutover.md`
  - 显式调用成功率 `6/8 = 75%`
  - `explicit-dollar = 100%`
  - `explicit-named = 100%`
  - `explicit-path = 100%`
  - `implicit = 0%`
- 最终发布结论：`reports/final-release-validation-20260320.md`
- 阶段对比摘要：`reports/compare-release-eval-01-vs-04.md`

## 2026-04 升级同步摘要

这个公开仓库现已同步到 **2026-04-13 / 2026-04-14** 的最终版 skill 内容。

本次同步重点不是重写仓库结构，而是把你当前实际在用的新版能力回填到公开版 skill：

- 强化 `single-controller first`
- 补齐 `ownership-first` 与 `research-swarm`
- 增加官方模式桥接与评分 rubric
- 升级 `artifact contract v2`
- 升级 runtime probe / run checker
- 增加 forward regression cases 与回归脚本

说明：

- **2026-03-20** 的公开发布报告仍然保留，作为历史接受版证据
- **2026-04** 这次主要体现为“skill 内容升级同步”，不是重新提交一整套新的公开 live eval 包

详见：

- `reports/open-source-sync-20260414-skill-upgrade.md`
- `CHANGELOG.md`

## 迭代历史与聊天记录

你当时围绕这个 skill 的“聊天式迭代痕迹”主要集中在：

- `skill-lab/runs/`：早期 baseline / optimized 实验
- `skill-lab+/runs/`：发布命名、收敛与验证阶段
- `.workspace/subagent-model-smoke/`：子 agent / skill 触发行为烟测

已在仓库中整理：

- 索引：`docs/history/chat-records-index.md`
- 代表性原始片段：`docs/history/raw/`

## 已知限制

- `implicit` discoverability 仍不可靠，不应当作主入口
- 是否真的能使用 native child-agent，仍需要 **当前会话的 live evidence**
- 一旦环境里存在语义相近的 team / swarm skill，自动路由可能被抢占

更多说明见：

- `docs/triggering-behavior.md`
- `docs/conflicting-skills.md`

## 开源协作文件

本仓库已补齐：

- `LICENSE`
- `CONTRIBUTING.md`
- `SECURITY.md`
- `CODE_OF_CONDUCT.md`
- `.github/ISSUE_TEMPLATE/*`
- `.github/pull_request_template.md`
- `.github/workflows/validate.yml`

GitHub 仓库简介、topics 与开源发布文案建议见：

- `docs/github-about.md`

版本变更记录见：

- `CHANGELOG.md`

## License

MIT — see `LICENSE`.
