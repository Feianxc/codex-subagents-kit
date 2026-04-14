# Final Release Validation — 2026-03-20

## Final decision

- 发布名称：`codex-subagents-kit`
- 当前接受版 skill 路径：`skills/codex-subagents-kit/`
- 当前本机安装目标（历史记录）：`~/.codex/skills/codex-subagents-kit`

## Naming result

从 `codex-agent-swarm-optimized` 改名为 `codex-subagents-kit`，目标是：

1. 更产品化
2. 更贴近 Codex 当前机制命名
3. 避免 `optimized` 这种阶段性实验命名
4. 避免 `swarm` 对不存在原生 team runtime 的过度暗示

## Accepted test evidence

### 1) Static validation

- Historical tool: Codex `skill-creator` 自带的 `quick_validate.py`
- Result: `Skill is valid!`

### 2) Live eval accepted run

- Run ID: `20260320-release-eval-04-final-candidate`
- Report: `reports/score-report-release-eval-04-final-candidate.md`

Accepted result:

- `release total = 110`
- `avg_input_tokens = 39874`
- `avg_output_tokens = 2076`
- `failure_cases = none`

### 3) Discoverability accepted run

- Run ID: `20260320-release-discovery-02-post-cutover`
- Report: `reports/discoverability-report-release-02-post-cutover.md`

Accepted result:

- total success = `6/8 = 75%`
- `explicit-dollar = 100%`
- `explicit-named = 100%`
- `explicit-path = 100%`
- `implicit = 0%`

### 4) Global smoke accepted runs

- Empty workspace run ID: `20260320-global-release-smoke-01`
- Real workspace root run ID: `20260320-global-release-smoke-02-root`

Accepted result:

- `explicit-named = success`
- `explicit-dollar = success`
- `explicit-path = success`

## Token efficiency conclusion

当前接受版 `codex-subagents-kit` 在 live eval accepted run 中：

- 与同仓 baseline 相比：
  - 分数更高
  - 输入 token 更低
  - 输出 token 更低

在全局 smoke 中：

- `explicit-dollar` 依然是默认推荐入口
- `explicit-path` 适合需要更强确定性的场景
- `explicit-named` 在全局安装后已恢复稳定可用

## 2026-04-09 staging note

本开源整理目录在保留 2026-03-20 发布证据的同时，又同步覆盖了当前本机安装版中较新的两份文件：

- `skills/codex-subagents-kit/SKILL.md`
- `skills/codex-subagents-kit/references/selection-guide.md`

这样可以让这个公开整理目录更贴近你现在实际在用的 skill 内容，同时不丢失原始发布验证结论。

## Publish recommendation

公开发布时建议仓库名直接使用：

- `codex-subagents-kit`

默认对外用法：

- `Use $codex-subagents-kit`

更强约束用法：

- `Use $codex-subagents-kit at <skill-path>`
