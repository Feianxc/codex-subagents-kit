# Decision Matrix

## Layer 1: Do you need more than one agent?

只有当下面至少一项明显成立时，才值得升级：

- `context_protection`
  - 子任务会产生大量主线程不需要记住的噪音
- `parallel_exploration`
  - 多个角度可以正交并行
- `specialization`
  - 工具、权限、领域规则或评估标准明显不同

如果都不明显，选 `single-controller`。

## Layer 2: Ownership shape

| Shape | Best for | Avoid when |
| --- | --- | --- |
| `single-controller` | 单轮、小任务、单文件热点高 | 明显需要并行研究 / 隔离噪音 |
| `manager-with-specialists` | 主控保留最终 synthesis，specialist 只做 bounded sidecar | specialist 需要自己接管用户分支 |
| `handoff-network` | 外部 OpenAI Agents SDK / Responses 方案蓝图 | 当前只是 Codex session 本地执行 |
| `research-shared-findings` | 研究型任务，需要共享发现 | 只是固定顺序流水线 |

## Layer 3: Four Gates

| Gate | Pass when | If not passed |
| --- | --- | --- |
| Product Gate | Codex 产品层支持相关能力，例如 `multi_agent`、Subagents、`.codex/agents/`、`skills.config` | 不要宣称这是“官方原生路径” |
| Session Gate | 当前 session 确实暴露 native agent 工具证据 | 不要伪装成原生子代理；转 `config-guided` 或 `artifact` |
| Policy Gate | 当前任务、风险、时间、用户要求允许真正 spawn | 退回 controller 或 blueprint |
| Task Gate | 能定义 owner / input / output / acceptance / spawn_reason / stop_condition | 不 spawn |

## Layer 4: Runtime mode

| Mode | Use when | Avoid when | Evidence to record |
| --- | --- | --- | --- |
| `blueprint-only` | 目标不清、风险高、需要先沉淀蓝图 | 已可直接执行 | 缺失信息、关键假设 |
| `single-controller` | 任务小、热点文件重叠高、并行收益低 | 已有多份独立输出 | 为什么 spawn 浪费 |
| `native-subagents` | 四层门控都通过，当前 session 有 live native tool evidence | 只有 feature flag 或文档证据，没有 live tools | 版本、feature flag、tool evidence、agent id |
| `config-guided-codex-subagents` | 产品层支持，但当前 session 不直接暴露 native tools，或本轮更适合做项目级配置沉淀 | 任务极小、不需要后续复用 | `.codex/agents/`、`AGENTS.md`、`skills.config` 证据 |
| `artifact-orchestrated-swarm` | 任务值得拆，需稳定降级路径，且 `codex exec` 可用 | 任务太小或没有稳定 I/O | run root、prompt/output/log 结构、降级原因 |

## Layer 5: Overlay patterns

- `generator-verifier`
  - 输出质量敏感、rubric 清晰时叠加
- `research-swarm`
  - 多角度资料研究时叠加 shared findings ledger
- `review-separation`
  - 实现者与 reviewer / verifier 分离
- `long-lived-role-ownership`
  - 仅在 runtime 真的支持持久 teammate 时才声称“团队成员持续记忆”

## Spawn Worthiness

一个任务只有同时满足以下条件才值得独立 agent：

1. 单一目标
2. 稳定输入
3. 稳定输出
4. 可写 acceptance
5. 热文件重叠低
6. 可写 stop condition
7. 协调成本 < 收益

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
- stop / fallback ownership
