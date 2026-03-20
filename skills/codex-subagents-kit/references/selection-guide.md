# Selection Guide

## Four gates

| Gate | Pass when | If not passed |
| --- | --- | --- |
| Product Gate | Codex 产品层支持 `multi_agent`、Subagents、`.codex/agents/`、`skills.config` 等相关能力 | 不要把方案称为“Codex 原生已启用” |
| Session Gate | 当前 session 确实暴露 live native child-agent 工具证据 | 不要宣称可直接 native spawn |
| Policy Gate | 当前任务、风险、用户要求允许真正并行/子运行 | 降级到 controller 或 blueprint |
| Task Gate | 能定义 owner / input / output / acceptance / spawn_reason | 不 spawn |

## Mode matrix

| Mode | Use when | Avoid when | Evidence |
| --- | --- | --- | --- |
| `blueprint-only` | 目标模糊、信息不足、风险高 | 已能直接执行 | 缺失信息与关键假设 |
| `single-controller` | 任务小、文件热点高、并行收益低 | 有多份独立输出可并行 | 为什么不值得 spawn |
| `native-subagents` | 四层门控都通过，且有 live tool evidence | 只有 feature flag / 文档证据 | version + feature + tool evidence |
| `config-guided-codex-subagents` | 产品层支持，但当前 session 不适合直接 native spawn；更适合沉淀项目级配置 | 极小任务、不需要复用 | `.codex/agents/`、`skills.config`、`AGENTS.md` |
| `artifact-orchestrated-swarm` | 任务值得拆，但需要稳定可审计降级路径 | 没有稳定 I/O | run_root + prompts/outputs/logs |

## Spawn worthiness

只有同时满足以下条件才值得独立 agent：

1. 单一目标
2. 稳定输入
3. 稳定输出
4. 可验证 acceptance
5. 热文件重叠低
6. 协调成本低于收益

## Concurrency budget defaults

- explorer：2~4
- writer：1~2
- reviewer / verifier：1
- 同热点文件 writer：禁止并发

## Controller ownership

主控永远保留：

- preflight
- mode selection
- registry integrity
- final merge / acceptance
- audit honesty
- scorecard ownership
