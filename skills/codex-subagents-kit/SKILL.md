---
name: codex-subagents-kit
description: Codex 专用 Subagents 工作台与测试套件。用于 Codex Subagents、`.codex/agents/`、`skills.config`、context efficiency、artifact-backed path、运行时探针、scorecard 与并行/降级决策。适用于需要按 Codex 真实机制设计、测试或优化多智能体协作技能的场景。
---

# Codex Subagents Kit

把这个 skill 当成 **Codex-only orchestration guide**：

- 优先对齐 **Codex Subagents / `.codex/agents/` / `skills.config`**
- 控制上下文体积，避免把长说明塞进主对话
- 用可验证 artifacts、脚本和 scorecard 构成闭环
- 对 native child-agent 能力保持诚实；证据不足时改走 artifact 路径

## Core rules

1. 先做 preflight，再决定是否并行。
2. 区分 **产品支持**、**会话证据**、**策略许可**、**任务适配** 四层事实。
3. 只把独立、边界清晰、验收明确的任务交给子 agent。
4. 长计划、长结果、对比表优先落盘，不优先塞进聊天上下文。
5. 规则性动作优先脚本/CLI，不要把一切都做成 agent。

## Minimal workflow

### 1) Preflight

先写清：

- `final_goal`
- `deliverables`
- `constraints`
- `success_criteria`
- `spawn_candidates`
- `tasks_not_worth_spawning`

复杂任务先初始化 run：

```powershell
powershell -ExecutionPolicy Bypass -File "C:/Users/feian/.codex/tools/safe-run.ps1" `
  -ScriptPath "<skill-root>/scripts/init_codex_swarm_run.py" `
  -ScriptArgs @("--workspace-root",".","--case","my-task")
```

最小 artifacts：

- `preflight.md`
- `agent-blueprints.md`
- `execution-plan.md`
- `task-registry.md`
- `protocol-audit.md`
- `team-report.md`
- `scorecard.md`

### 2) Four gates

先判断四层门控：

1. **Product Gate**：Codex 产品层是否支持当前机制
2. **Session Gate**：当前 session 是否有 live native agent 工具证据
3. **Policy Gate**：当前任务/风险/用户要求是否允许真正 spawn
4. **Task Gate**：能否写出 owner / input / output / acceptance

如果需要完整判断规则，读：

- `references/selection-guide.md`

### 3) Choose a mode

默认只在四层门控都通过时选 `native-subagents`。  
否则按任务目标选择：

- `single-controller`
- `config-guided-codex-subagents`
- `artifact-orchestrated-swarm`

如果需要完整模式矩阵，读：

- `references/selection-guide.md`

### 4) Keep context small

默认只读：

- 当前 `SKILL.md`
- 与当前决策直接相关的少量 reference
- 必要入口文件

不要默认读完所有 references、logs、历史会话。

如果需要更细的 token 控制规则，读：

- `references/context-efficiency.md`

### 5) Use project agents when config-guided mode wins

当产品层支持，但当前 session 不适合直接 native spawn 时：

1. 优先在项目里维护 `.codex/agents/`
2. 保持 `AGENTS.md` 简短，只放高复用协作规则
3. 用 `skills.config` 精确指向 skill 路径
4. 用固定模板定义 explorer / worker / reviewer / verifier

如果需要模板与复制规则，读：

- `references/project-agents.md`
- `assets/project-agents/*.toml`

### 6) Use artifact swarm when a stable artifact path is needed

当需要稳定降级路径时：

1. 每个子任务写独立 prompt
2. 每个子任务写独立 output file
3. 通过 `codex exec` 或现成脚本执行
4. 持续维护 registry / audit / scorecard

执行子任务优先用：

- `scripts/run_codex_swarm_task.py`

如果需要 child prompt 合同、热文件规则、reviewer 分离规则，读：

- `references/multi-agent-hardening.md`
- `references/topology-catalog.md`
- `references/artifact-contract.md`

### 7) Probe and validate

需要 runtime 证据时执行：

```powershell
powershell -ExecutionPolicy Bypass -File "C:/Users/feian/.codex/tools/safe-run.ps1" `
  -ScriptPath "<skill-root>/scripts/probe_codex_swarm_runtime.py" `
  -ScriptArgs @("--run-root",".workspace/codex-swarm/runs/<run_id>","--workspace-root",".")
```

完成后先校验：

```powershell
powershell -ExecutionPolicy Bypass -File "C:/Users/feian/.codex/tools/safe-run.ps1" `
  -ScriptPath "<skill-root>/scripts/check_codex_swarm_run.py" `
  -ScriptArgs @("--run-root",".workspace/codex-swarm/runs/<run_id>")
```

## Output contract

最终回答至少说明：

1. 选择了哪种模式
2. 四层门控的判断结果
3. 是否真的用了 native subagents / config-guided setup / artifact mode
4. `run_root` 和主要 artifacts
5. 哪些任务值得 spawn，哪些不值得
6. 哪些上下文被刻意不加载，以节省 token

如果回答是 compact checklist 或 smoke 风格，仍应在 `artifact-core` 或等价字段里明确：

- 是否需要 `run_root`
- 是否需要 `registry`
- 是否需要 `audit`
- 是否需要 `scorecard`

## Read-on-demand map

- `references/selection-guide.md`
  - 需要四层门控、模式矩阵、并发预算时读
- `references/context-efficiency.md`
  - 需要控制 token / prompt 体积时读
- `references/project-agents.md`
  - 需要落地 `.codex/agents/` 模板时读
- `references/topology-catalog.md`
  - 需要选择研究/修复/审查队形时读
- `references/multi-agent-hardening.md`
  - 需要 prompt 合同、热文件规则、review 分离时读
- `references/artifact-contract.md`
  - 需要 artifacts / audit / scorecard 规范时读
- `references/codex-runtime-notes.md`
  - 需要本机 runtime 已知事实时读
