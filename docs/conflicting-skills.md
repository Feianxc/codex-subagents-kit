# Conflicting skills and routing collisions

这个文档专门记录一个工程事实：

> 即使 `codex-subagents-kit` 本身设计正确，只要当前环境里仍暴露了其他语义非常接近的 team/swarm skill，自动路由就可能被“抢走”。

## 当前已确认的冲突样本

### `agent-team-planner`

路径：

- `C:\Users\feian\.agents\skills\agent-team-planner`

它的核心 metadata 明确覆盖：

- `Agent Teams`
- `swarm`
- `TeamCreate`
- `TaskCreate`
- `TaskUpdate`

这意味着在技能发现层面，它对下面这类说法拥有非常强的语义吸引力：

- “创建一个 AGENT 团队”
- “搭一个 swarm”
- “并行 AGENT”
- “team runtime”

而 `codex-subagents-kit` 的定位更偏：

- Codex Subagents
- `.codex/agents/`
- `skills.config`
- artifact-backed orchestration
- 四层门控

因此，**两者虽然不是同一 runtime 合约，但在 discoverability 意图空间里确实是冲突的。**

## 重要区分：同类别，不同 runtime

### 从“任务类别”看

二者都属于：

- 多智能体 / 团队 / 并行编排类 skill

### 从“运行时目标”看

二者不是同一个东西：

- `agent-team-planner`
  - 面向 Claude Code / TeamCreate / TaskCreate 风格 runtime
- `codex-subagents-kit`
  - 面向 Codex / Subagents / `.codex/agents/` / `skills.config` / artifact path

所以：

1. 它们在**意图类别上相似**
2. 它们在**机制层实现上不同**
3. 一旦同时暴露在同一技能池里，就会产生路由竞争

## 当前工程建议

如果你的目标是：

> 在这个环境里让 `codex-subagents-kit` 成为“创建 AGENT 团队 / 多 agent 编排”的唯一主路由

那么建议：

1. 删除或禁用 `agent-team-planner`
2. 避免同时保留其他 team/swarm 同类 skill
3. 在文档与 prompt 示例里统一使用：
   - `Use $codex-subagents-kit`

## 如果必须共存

如果你必须同时保留两个 skill，那么不要依赖纯自然语言自动选中。

请显式绑定：

### 调用 Codex 版

```text
Use $codex-subagents-kit
```

### 调用 CC team runtime 版

```text
Use $agent-team-planner
```

## 清理原则

同一个运行 surface 上，最好只保留一个“team/swarm orchestration 的默认 owner”：

- 要么是 `agent-team-planner`
- 要么是 `codex-subagents-kit`

不要让两个都同时扮演“默认 AGENT 团队 skill”。

