# Decision Matrix

## Four Gates

| Gate | Pass when | If not passed |
| --- | --- | --- |
| Product Gate | Codex 产品层支持相关能力，例如 `multi_agent`、Subagents、`.codex/agents/`、`skills.config` | 不要宣称这是“官方原生路径” |
| Session Gate | 当前 session 确实暴露 native agent 工具证据 | 不要伪装成原生子代理；转 `config-guided` 或 `artifact` |
| Policy Gate | 当前任务、风险、时间、用户要求允许真正 spawn | 退回 controller 或 blueprint |
| Task Gate | 能定义 owner / input / output / acceptance / spawn_reason | 不 spawn |

## Mode Selection

| Mode | Use when | Avoid when | Evidence to record |
| --- | --- | --- | --- |
| `blueprint-only` | 目标不清、风险高、需要先沉淀蓝图 | 已可直接执行 | 缺失信息、关键假设 |
| `single-controller` | 任务小、热点文件重叠高、并行收益低 | 已有多份独立输出 | 为什么 spawn 浪费 |
| `native-subagents` | 四层门控都通过，当前 session 有 live native tool evidence | 只有 feature flag 或文档证据，没有 live tools | 版本、feature flag、tool evidence、agent id |
| `config-guided-codex-subagents` | 产品层支持，但当前 session 不直接暴露 native tools，或本轮更适合做项目级配置沉淀 | 任务极小、不需要后续复用 | `.codex/agents/`、`AGENTS.md`、`skills.config` 证据 |
| `artifact-orchestrated-swarm` | 任务值得拆，需稳定降级路径，且 `codex exec` 可用 | 任务太小或没有稳定 I/O | run root、prompt/output/log 结构、降级原因 |

## Spawn Worthiness

一个任务只有同时满足以下条件才值得独立 agent：

1. 单一目标
2. 稳定输入
3. 稳定输出
4. 可写 acceptance
5. 热文件重叠低
6. 协调成本 < 收益

## Concurrency Budget

- explorer：2~4
- writer：1~2
- reviewer/verifier：1
- 同热点文件 writer：不并行

## Controller Responsibilities

主控永远保留：

- preflight framing
- mode selection
- registry integrity
- final merge / acceptance
- audit honesty
- scorecard ownership
