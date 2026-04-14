# Triggering behavior and discoverability

这个文档解释一个常见误解：

> “既然这是 AGENT 团队 skill，为什么我说一句‘创建一个 AGENT 团队’它不一定自动调用？”

## 结论

对于 `codex-subagents-kit`，当前接受版结论是：

1. **显式调用** 是当前稳定主路径
2. **自然语言隐式自动触发** 不能被当成稳定承诺
3. “多 agent / 团队”能力存在于 Codex 产品方向中，但 skill 是否被自动选中，取决于：
   - 运行 surface（app / CLI / IDE）
   - 是否全局安装
   - 是否只是在 project / injected 局部加载
   - 当前上下文里还有没有其他竞争 skill
   - 本轮 prompt 是否足够明确

## 我们测试过什么

### 已测试并确认稳定的方式

- `Use $codex-subagents-kit`
- `Use the skill named "codex-subagents-kit"`
- `Use $codex-subagents-kit at <skill-path>`

注意：

- 上面三种“显式调用”是指 **在正确安装与正确环境下**
- 其中默认推荐仍是 `$skill-name`

### 没有承诺稳定的方式

- 只说“创建一个 AGENT 团队”
- 只说“并行搞一下”
- 不提 skill 名、也不给 path、也不给更强约束

这类说法在某些场景可能会触发，但**当前证据不足以把它当成稳定主入口**。

## 最新冲突证据（2026-03-21）

我们专门做过一条自然语言探针：

```text
请帮我创建一个AGENT团队来处理这个任务。
```

结果不是命中 `codex-subagents-kit`，而是命中了另一个可见技能：

- `agent-team-planner`

这说明一件很关键的事：

> 自然语言“意图”并不会天然绑定到“你想要的那个 skill”。

它更像是在当前可见技能池里做一次**语义路由 / 检索匹配**：

- 如果别的 skill 在名字或描述上更贴近“AGENT 团队”
- 或者别的 skill 描述更强、更直接
- 或者当前 surface 更偏向命中某个现成 team skill

那么 Codex/运行环境就可能选到别的 skill，而不是 `codex-subagents-kit`。

## 为什么默认推荐 `$skill-name`

原因有三层：

### 1. 本机 shipped skill-creator 规则就是这么引导的

本机 `skill-creator` 的 `openai_yaml` 约束明确要求：

- `default_prompt` 要显式提到 `$skill-name`

这说明从产品/元数据设计角度，**显式 mention 本身就是推荐路径**。

### 2. 本仓库测试结果支持它

本仓库当前接受版 discoverability 结果见：

- `reports/discoverability-report-release-02-post-cutover.md`

接受版里：

- `explicit-dollar = 100%`
- `explicit-named = 100%`
- `explicit-path = 100%`
- `implicit = 0%`

### 3. 官方也只说“可以自动用”，不是“任何自然语言都必然自动用”

OpenAI 在 Codex app 相关公开说明里表达的是：

- 你可以**显式要求**使用某个 skill
- 也可以让 Codex **根据任务自动使用**

但这不等于：

- 每个 surface
- 每个 session
- 每种自然语言表述
- 每个本地安装状态

都会稳定自动命中同一个 skill。

## 为什么“创建一个 AGENT 团队”不等于“自动命中 codex-subagents-kit”

因为这句话同时具备两个问题：

1. 它描述的是**意图**
2. 它没有给出**目标 skill 绑定**

而 `codex-subagents-kit` 的定位并不是“任何 team 相关表达的唯一匹配项”，它更具体地是：

- Codex 专用
- Subagents / `.codex/agents/`
- `skills.config`
- artifact-backed orchestration
- 四层门控和 scorecard

所以如果环境里还有别的 skill 更像：

- `agent-team-planner`
- team runtime
- team graph
- 并行 AGENT 规划器

那么“创建一个 AGENT 团队”这句话就非常容易先命中对方。

## “创建一个 AGENT 团队”为什么不等于“自动调用这个 skill”

因为这句话表达的是 **任务意图**，不是 **技能绑定**。

Codex 需要先做两层判断：

1. 这句话是不是需要“多 agent / subagents / orchestration”能力
2. 在当前可见 skill 里，哪一个 skill 最匹配

如果：

- metadata 不够强
- 当前有其他近似 skill
- 只是 project/injected 局部加载
- 当前 surface 的 discoverability 行为更保守

那么它可能：

- 不触发任何 skill
- 触发错误 skill
- 只按普通推理完成，不显式采用该 skill

## 当前推荐口径

如果你要稳定、可复现地触发：

```text
Use $codex-subagents-kit
```

如果你要最强确定性：

```text
Use $codex-subagents-kit at <skill-path>
```

如果你只是想测试“自然语言是不是会自己选中它”，那应该把这当成 **discoverability 实验**，而不是交付路径。

## 如果你真的想让“创建一个 AGENT 团队”更容易自动命中它

可以做，但那是**路由优化工程**，不是默认保证。常见手段包括：

1. 在当前环境里移除或禁用语义更强的冲突 skill
2. 进一步增强 `codex-subagents-kit` 的 metadata，使其更直接覆盖：
   - agent team
   - parallel agents
   - subagents team
   - multi-agent coding team
3. 在项目级 `AGENTS.md` / team config 中写入更强的优先路由说明
4. 在 app / automation 里把该 skill 显式绑定到对应自动化任务

但即便如此，也仍应把：

```text
Use $codex-subagents-kit
```

当作最稳的交付入口。
