# Project Agents for Codex

## Why use `.codex/agents/`

当 `config-guided-codex-subagents` 胜出时，项目级 `.codex/agents/` 是最适合沉淀角色化行为的地方：

- 减少每次重复解释角色职责
- 让项目级角色优先于全局角色
- 把 explorer / worker / reviewer / verifier 的边界固定下来

## Recommended templates

在 `assets/project-agents/` 中提供了四类最小模板：

- `explorer.toml`
- `worker.toml`
- `reviewer.toml`
- `verifier.toml`

## Recommended copy target

复制到项目：

```text
.codex/agents/
  explorer.toml
  worker.toml
  reviewer.toml
  verifier.toml
```

## Minimal project config

建议项目 `.codex/config.toml` 至少包含：

- `[features] multi_agent = true`
- `[agents] max_threads = <small default>`
- `[agents] max_depth = <small default>`
- `[[skills.config]] path = '<skill-path>'`

## Design principles

1. explorer 偏只读，不写文件
2. worker 负责编写与修复
3. reviewer 不与 implementer 混同
4. verifier 只负责测试、回归和 acceptance 证据
5. 热文件改动仍由 controller 决定是否串行
